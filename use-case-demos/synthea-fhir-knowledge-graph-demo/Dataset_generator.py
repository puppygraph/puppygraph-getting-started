import json
import os
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import duckdb
import pandas as pd

# Input Paths
FHIR_DIR = Path("synthea/output/fhir")
OUT_DIR = Path("puppygraph_output")
OUT_DIR.mkdir(exist_ok=True)

# Default: two non-overlapping public FHIR R4 bundles (patient counts vary by release).
_DEFAULT_SYNTHEA_ZIPS = [
    "https://raw.githubusercontent.com/synthetichealth/synthea-sample-data/main/downloads/synthea_sample_data_fhir_r4_sep2019.zip",
    "https://raw.githubusercontent.com/synthetichealth/synthea-sample-data/main/downloads/synthea_sample_data_fhir_r4_nov2021.zip",
]

def _synthea_zip_urls():
    raw = os.environ.get("SYNTHEA_SAMPLE_URLS", "").strip()
    if raw:
        return [u.strip() for u in raw.split(",") if u.strip()]
    single = os.environ.get("SYNTHEA_SAMPLE_URL", "").strip()
    if single:
        return [single]
    return list(_DEFAULT_SYNTHEA_ZIPS)


def _max_json_files():
    v = os.environ.get("MAX_JSON_FILES", "").strip()
    if not v:
        return None
    return int(v)


def _maybe_seed_rng():
    """Optional reproducibility hook for any future randomized steps in this script."""
    raw = os.environ.get("SYNTHEA_RANDOM_SEED", "").strip()
    if not raw:
        return
    s = int(raw)
    import random

    random.seed(s)
    try:
        import numpy as np

        np.random.seed(s)
    except ImportError:
        pass

def extract_observation_value(resource):
    """
    FHIR Observation uses polymorphic value[x]
    The field NAME changes based on data type
    """
    if "valueQuantity" in resource:
        return resource["valueQuantity"].get("value"), "numeric"
    if "valueString" in resource:
        return resource["valueString"], "string"
    if "valueCodeableConcept" in resource:
        display = resource["valueCodeableConcept"]["coding"][0].get("display")
        return display, "codeable_concept"
    if "valueBoolean" in resource:
        return str(resource["valueBoolean"]), "boolean"
    return None, None

def parse_observation(resource):
    if resource.get("resourceType") != "Observation":
        return None
    
    coding = resource.get("code", {}).get("coding", [])
    obs_code = coding[0].get("code") if coding else None
    obs_display = coding[0].get("display") if coding else None
    
    patient_ref = resource.get("subject", {}).get("reference", "")
    patient_id = patient_ref.split("/")[-1]
    
    value, value_type = extract_observation_value(resource)
    
    return {
        "patient_id": patient_id,
        "observation_code": obs_code,
        "observation_display": obs_display,
        "value": value,
        "value_type": value_type,
        "effective_date": resource.get("effectiveDateTime")
    }

def parse_condition(resource):
    if resource.get("resourceType") != "Condition":
        return None
    
    coding = resource.get("code", {}).get("coding", [])
    code = coding[0].get("code") if coding else None
    display = coding[0].get("display") if coding else None
    
    patient_ref = resource.get("subject", {}).get("reference", "")
    patient_id = patient_ref.replace("urn:uuid:", "").split("/")[-1]
    
    return {
        "patient_id": patient_id,
        "condition_code": code,
        "condition_display": display,
        "recorded_date": resource.get("recordedDate"),
        "clinical_status": resource.get("clinicalStatus", {})
                          .get("coding", [{}])[0].get("code")
    }

def parse_patient(resource):
    if resource.get("resourceType") != "Patient":
        return None
    
    birth_date = resource.get("birthDate")
    birth_year = int(birth_date[:4]) if birth_date else None
    
    return {
        "patient_id": resource.get("id"),
        "gender": resource.get("gender"),
        "birth_year": birth_year,
        "age": 2026 - birth_year if birth_year else None
    }

def parse_practitioner(resource):
    if resource.get("resourceType") != "Practitioner":
        return None
    
    practitioner_id = resource.get("id")
    name_info = resource.get("name", [{}])[0]
    family = name_info.get("family", "")
    given = name_info.get("given", [""])[0]
    prefix = name_info.get("prefix", [""])[0]
    name = f"{prefix} {given} {family}".strip()
    
    npi = next(
        (i.get("value") for i in resource.get("identifier", [])
         if "us-npi" in i.get("system", "")),
        None,
    )

    return {
        "practitioner_id": practitioner_id,
        "npi": npi,
        "name": name
    }

def parse_medication_request(resource, medications_by_ref):
    """
    medications_by_ref maps a bundle entry's fullUrl to its Medication resource.
    Newer Synthea releases put the drug in a Medication resource and point to it
    with medicationReference instead of an inline medicationCodeableConcept.
    """
    if resource.get("resourceType") != "MedicationRequest":
        return None

    patient_ref = resource.get("subject", {}).get("reference", "")
    patient_id = patient_ref.replace("urn:uuid:", "").split("/")[-1]

    # Kept raw: resolved to a practitioner NPI in main(), once all bundles are read.
    practitioner_ref = resource.get("requester", {}).get("reference", "")

    concept = resource.get("medicationCodeableConcept")
    if concept is None:
        med_ref = resource.get("medicationReference", {}).get("reference", "")
        concept = medications_by_ref.get(med_ref, {}).get("code", {})
    coding = concept.get("coding", [])
    drug_name = coding[0].get("display") if coding else None

    if not practitioner_ref or not patient_id or not drug_name:
        return None

    return {
        "patient_id": patient_id,
        "practitioner_ref": practitioner_ref,
        "drug_name": drug_name,
        "authored_on": resource.get("authoredOn")
    }


def resolve_practitioner_npi(ref, npi_by_id):
    """
    Synthea references practitioners in two ways, depending on the release:
      urn:uuid:<practitioner id>                                   (2019)
      Practitioner?identifier=http://hl7.org/fhir/sid/us-npi|<NPI> (2021)
    Both are resolved to the practitioner's NPI, which is the vertex ID.
    """
    if "identifier=" in ref:
        return ref.rsplit("|", 1)[-1]
    return npi_by_id.get(ref.replace("urn:uuid:", "").split("/")[-1])

def main():
    _maybe_seed_rng()
    print("Starting data parsing from Synthea output...")
    patients = []
    conditions = []
    observations = []
    practitioners = []
    medication_requests = []

    FHIR_DIR.mkdir(parents=True, exist_ok=True)
    if not list(FHIR_DIR.glob("**/*.json")):
        urls = _synthea_zip_urls()
        print(
            "No local Synthea data found. Downloading FHIR bundle(s) from the internet "
            f"({len(urls)} zip(s)); patient and file counts vary by Synthea release."
        )
        for i, url in enumerate(urls, start=1):
            print(f"  [{i}/{len(urls)}] {url}")
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            try:
                urllib.request.urlretrieve(url, tmp_path)
                with zipfile.ZipFile(tmp_path, "r") as zip_ref:
                    zip_ref.extractall(FHIR_DIR)
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()
        print("Download(s) complete. Unzipped into", FHIR_DIR.resolve())

    all_files = sorted(FHIR_DIR.glob("**/*.json"))
    cap = _max_json_files()
    files = all_files if cap is None else all_files[:cap]
    if cap is not None and len(all_files) > cap:
        print(f"Note: processing first {cap:,} of {len(all_files):,} JSON files (MAX_JSON_FILES).")
    print(f"Total files found: {len(files)}")

    for i, file_path in enumerate(files):
        if i % 5000 == 0 and i > 0:
            print(f"  Processing {i}/{len(files)}...")
        
        try:
            with open(file_path) as f:
                bundle = json.load(f)
        except Exception as e:
            continue
        
        medications_by_ref = {
            entry.get("fullUrl"): entry.get("resource", {})
            for entry in bundle.get("entry", [])
            if entry.get("resource", {}).get("resourceType") == "Medication"
        }

        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            rtype = resource.get("resourceType")
            
            if rtype == "Patient":
                row = parse_patient(resource)
                if row: patients.append(row)
            elif rtype == "Observation":
                row = parse_observation(resource)
                if row: observations.append(row)
            elif rtype == "Condition":
                row = parse_condition(resource)
                if row: conditions.append(row)
            elif rtype == "Practitioner":
                row = parse_practitioner(resource)
                if row: practitioners.append(row)
            elif rtype == "MedicationRequest":
                row = parse_medication_request(resource, medications_by_ref)
                if row: medication_requests.append(row)

    print("Converting to Pandas DataFrames...")
    patients_df = pd.DataFrame(patients).drop_duplicates(subset=["patient_id"])
    observations_df = pd.DataFrame(observations)
    conditions_df = pd.DataFrame(conditions)
    practitioners_df = pd.DataFrame(practitioners).drop_duplicates(subset=["practitioner_id"])
    med_req_df = pd.DataFrame(medication_requests)

    print(f" Loaded:")
    print(f"  Patients: {len(patients_df):,}")
    print(f"  Observations: {len(observations_df):,}")
    print(f"  Conditions: {len(conditions_df):,}")
    print(f"  Practitioners: {len(practitioners_df):,}")
    print(f"  MedicationRequests: {len(med_req_df):,}")

    print("Transforming observations...")
    observations_df["value_numeric"] = pd.to_numeric(
        observations_df["value"], errors="coerce"
    )
    observations_df["value_text"] = observations_df["value"].where(
        observations_df["value_type"].isin(["codeable_concept", "string"])
    )
    observations_df = observations_df.drop(columns=["value"])
    observations_df["patient_id"] = observations_df["patient_id"].str.replace("urn:uuid:", "", regex=False)

    # Resolve each prescription's requester to a practitioner NPI (the Practitioner vertex ID)
    npi_by_id = dict(zip(practitioners_df["practitioner_id"], practitioners_df["npi"]))
    med_req_df["practitioner_npi"] = med_req_df["practitioner_ref"].map(
        lambda ref: resolve_practitioner_npi(ref, npi_by_id)
    )
    med_req_df = med_req_df.drop(columns=["practitioner_ref"])
    known = med_req_df["practitioner_npi"].isin(set(practitioners_df["npi"].dropna()))
    if (~known).any():
        print(f"  Dropping {(~known).sum():,} MedicationRequests whose requester is not in the data")
    med_req_df = med_req_df[known]
    practitioners_df = practitioners_df.dropna(subset=["npi"]).drop_duplicates(subset=["npi"])

    # Vertex tables: one row per vertex ID. The per-patient tables above hold one row
    # per FHIR resource (many rows per code), so they are used only as edge tables.
    # A code can carry more than one display text; keep the most common one.
    def one_row_per_code(df, code_col, display_col):
        return (
            df.dropna(subset=[code_col])
            .groupby(code_col)[display_col]
            .agg(lambda d: d.mode().iat[0] if not d.mode().empty else None)
            .reset_index()
        )

    condition_codes_df = one_row_per_code(conditions_df, "condition_code", "condition_display")
    observation_codes_df = one_row_per_code(observations_df, "observation_code", "observation_display")
    medications_df = med_req_df[["drug_name"]].drop_duplicates().reset_index(drop=True)
    conditions_df = conditions_df.dropna(subset=["condition_code"])
    observations_df = observations_df.dropna(subset=["observation_code"])

    # Add edge ID columns (PuppyGraph needs a unique edge ID per edge row)
    conditions_df = conditions_df.reset_index(drop=True)
    conditions_df["edge_id"] = conditions_df.index.astype(str)

    observations_df = observations_df.reset_index(drop=True)
    observations_df["edge_id"] = observations_df.index.astype(str)

    med_req_df = med_req_df.reset_index(drop=True)
    med_req_df["edge_id"] = med_req_df.index.astype(str)

    tables = {
        # vertex tables
        "patients": patients_df,
        "practitioners": practitioners_df,
        "condition_codes": condition_codes_df,
        "observation_codes": observation_codes_df,
        "medications": medications_df,
        # edge tables (one row per FHIR resource)
        "conditions": conditions_df,
        "observations": observations_df,
        "medication_requests": med_req_df,
    }

    print("Writing Parquet files...")
    for name, df in tables.items():
        df.to_parquet(OUT_DIR / f"{name}.parquet", index=False)

    # Create DuckDB with real tables (not views) so PuppyGraph can read them inside Docker
    print("Creating DuckDB with tables...")
    db_path = OUT_DIR / "data.duckdb"
    if db_path.exists():
        db_path.unlink()
    con = duckdb.connect(str(db_path))

    # Create actual tables from the Parquet data (uses default 'main' schema)
    for name in tables:
        parquet_path = (OUT_DIR / f"{name}.parquet").absolute()
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_parquet('{parquet_path}')")

    # Verify
    for name in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        print(f"  {name}: {count:,} rows")

    con.close()
    print("DuckDB tables created successfully.")
    print("Dataset generation complete. Ready for PuppyGraph!")

if __name__ == "__main__":
    main()
