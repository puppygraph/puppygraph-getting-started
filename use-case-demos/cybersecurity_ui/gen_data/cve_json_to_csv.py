# CVE JSON data can be downloaded from https://nvd.nist.gov/vuln/data-feeds#APIS

import os
import json
import csv
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Please adjust according to your local paths:
JSON_DIR = "./cve_json"        # Directory containing all CVE JSON files
OUTPUT_CSV = "cve.csv"         # Final output CSV filename
# ─────────────────────────────────────────────────────────────────────────────

def isoformat_or_empty(value):
    """If value is a datetime object, format as an ISO string; otherwise return as is or an empty string."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value or ""

# Define the columns to output in the final CSV (column names correspond to script fields)
fieldnames = [
    "id",                    # CVE ID
    "source_identifier",     # sourceIdentifier
    "published",             # published time (ISO 8601)
    "last_modified",         # lastModified time (ISO 8601)
    "vuln_status",           # vulnStatus
    "description_en",        # English description
    "vector_string",         # CVSSv3 vector
    "base_score",            # CVSSv3 base score
    "base_severity",         # CVSSv3 base severity
    "exploitability_score",  # CVSSv3 exploitability score
    "impact_score",          # CVSSv3 impact score
    "weaknesses",            # comma-separated list of CWE IDs
    "reference_urls"         # comma-separated list of reference URLs
]

# Collect all CVE records
all_records = []

for filename in os.listdir(JSON_DIR):
    if not filename.lower().endswith(".json"):
        continue
    path = os.path.join(JSON_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vulns = data.get("vulnerabilities", [])
    for entry in vulns:
        cv = entry.get("cve", {})
        rec = {}

        # Base scalar fields
        rec["id"] = cv.get("id", "")
        rec["source_identifier"] = cv.get("sourceIdentifier", "")
        rec["published"] = cv.get("published", "")
        rec["last_modified"] = cv.get("lastModified", "")
        rec["vuln_status"] = cv.get("vulnStatus", "")

        # English description: find where lang == "en" in descriptions array
        desc_en = ""
        for d in cv.get("descriptions", []):
            if d.get("lang") == "en":
                desc_en = d.get("value", "").strip()
                break
        rec["description_en"] = desc_en

        # Extract CVSSv3 data (prefer cvssMetricV31; leave empty if missing)
        vector = ""
        base_score = ""
        base_severity = ""
        exploitability = ""
        impact = ""
        metrics_v31 = cv.get("metrics", {}).get("cvssMetricV31", [])
        if metrics_v31:
            cvss_data = metrics_v31[0].get("cvssData", {})
            vector = cvss_data.get("vectorString", "")
            base_score = cvss_data.get("baseScore", "")
            base_severity = cvss_data.get("baseSeverity", "")
            exploitability = metrics_v31[0].get("exploitabilityScore", "")
            impact = metrics_v31[0].get("impactScore", "")
        rec["vector_string"] = vector
        rec["base_score"] = base_score
        rec["base_severity"] = base_severity
        rec["exploitability_score"] = exploitability
        rec["impact_score"] = impact

        # weaknesses: collect all CWE values and join with commas
        weaknesses_list = []
        for w in cv.get("weaknesses", []):
            for desc in w.get("description", []):
                if desc.get("lang") == "en":
                    weaknesses_list.append(desc.get("value", ""))
        rec["weaknesses"] = ",".join(weaknesses_list)

        # reference_urls: collect all URLs and join with commas
        references_list = [ref.get("url", "") for ref in cv.get("references", [])]
        rec["reference_urls"] = ",".join(references_list)

        all_records.append(rec)

# Write final CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for record in all_records:
        writer.writerow(record)

print(f"Written {len(all_records)} CVE records to {OUTPUT_CSV}")
