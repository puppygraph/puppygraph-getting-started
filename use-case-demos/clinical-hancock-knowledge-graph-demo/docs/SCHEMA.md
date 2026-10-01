# Patient Graph — Schema Reference

## Stack
- Source: 4 JSON files → DuckDB (4 raw tables + 7 views)
- Graph layer: PuppyGraph (logical mapping over Glue/Iceberg)

---

## Raw Tables

### clinical_data
**PK:** `patient_id` | One row per patient. The spine of the schema — carries the full longitudinal clinical record including diagnosis, treatment, and all post-treatment events.

| Column | Description |
|---|---|
| `patient_id` | Unique patient identifier |
| `sex` | Biological sex of the patient |
| `smoking_status` | Smoking history (e.g. smoker, non-smoker, ex-smoker) |
| `year_of_initial_diagnosis` | Year the patient was first diagnosed |
| `age_at_initial_diagnosis` | Patient's age at time of first diagnosis |
| `primarily_metastasis` | Whether the cancer had already spread to distant sites at the time of diagnosis (i.e. presented as stage IV) |
| `survival_status` | Whether the patient is living or deceased |
| `survival_status_with_cause` | Survival status with cause of death if applicable |
| `days_to_last_information` | Days from first treatment to the last date any information was recorded for this patient |
| `first_treatment_intent` | Goal of first treatment (e.g. curative, palliative) |
| `first_treatment_modality` | Type of first treatment administered (e.g. local surgery, radiotherapy) |
| `days_to_first_treatment` | Days from initial diagnosis to start of first treatment |
| `adjuvant_treatment_intent` | Goal of adjuvant treatment (e.g. curative, palliative) |
| `adjuvant_radiotherapy` | Whether adjuvant radiotherapy was given (yes/no) |
| `adjuvant_radiotherapy_modality` | Type of radiotherapy administered (e.g. percutaneous radiotherapy) |
| `adjuvant_systemic_therapy` | Whether adjuvant systemic therapy (e.g. chemotherapy) was given (yes/no) |
| `adjuvant_systemic_therapy_modality` | Specific systemic therapy regimen (e.g. fluorouracil + cisplatin) |
| `adjuvant_radiochemotherapy` | Whether radiotherapy and chemotherapy were given concurrently. Not strictly derivable from the two flags above — concurrent administration is clinically distinct from sequential (yes/no) |
| `recurrence` | Whether the cancer recurred after remission (yes/no) |
| `days_to_recurrence` | Days from first treatment to recurrence |
| `progress_1` | Whether a first disease progression event occurred (yes/no) |
| `days_to_progress_1` | Days from first treatment to first progression event |
| `progress_2` | Whether a second disease progression event occurred (yes/no) |
| `days_to_progress_2` | Days from first treatment to second progression event |
| `metastasis_1_locations` | Anatomical site of first metastatic event |
| `days_to_metastasis_1` | Days from first treatment to first metastatic event |
| `metastasis_2_locations` | Anatomical site of second metastatic event |
| `days_to_metastasis_2` | Days from first treatment to second metastatic event |
| `metastasis_3_locations` | Anatomical site of third metastatic event |
| `days_to_metastasis_3` | Days from first treatment to third metastatic event |
| `metastasis_4_locations` | Anatomical site of fourth metastatic event |
| `days_to_metastasis_4` | Days from first treatment to fourth metastatic event |

---

### pathological_data
**PK:** `patient_id` | One row per patient. Contains pathological findings from surgical examination of the tumor and surrounding tissue.

| Column | Description |
|---|---|
| `patient_id` | Unique patient identifier |
| `primary_tumor_site` | Anatomical location of the primary tumor |
| `pt_stage` | Pathological T-stage — size and local extent of the primary tumor |
| `pn_stage` | Pathological N-stage — degree of regional lymph node involvement |
| `grading` | Histological grade — how abnormal the tumor cells look (proxy for aggressiveness) |
| `hpv_association_p16` | Result of p16 immunohistochemistry stain, used as a surrogate marker for HPV infection. Tested on tumor tissue |
| `number_of_positive_lymph_nodes` | Count of lymph nodes found to contain cancer cells |
| `number_of_resected_lymph_nodes` | Total count of lymph nodes surgically removed and examined |
| `perinodal_invasion` | Whether the tumor has spread beyond the lymph node capsule into surrounding tissue |
| `lymphovascular_invasion_l` | Whether the tumor has invaded lymphatic vessels |
| `vascular_invasion_v` | Whether the tumor has invaded blood vessels |
| `perineural_invasion_pn` | Whether the tumor has invaded along nerve sheaths |
| `resection_status` | Whether surgical margins were clear: R0 (clean), R1 (microscopic residual), R2 (macroscopic residual) |
| `resection_status_carcinoma_in_situ` | Resection margin status specifically for any in-situ component of the tumor |
| `carcinoma_in_situ` | Whether carcinoma in situ (pre-invasive cancer) was present |
| `closest_resection_margin_in_cm` | Distance in cm between the tumor edge and the surgical cut |
| `histologic_type` | Microscopic tissue type of the tumor (e.g. squamous cell carcinoma) |
| `infiltration_depth_in_mm` | How deeply the tumor has grown into surrounding tissue |

---

### blood_data
**PK:** `blood_test_id` | Many rows per patient — one per lab measurement. Timing is expressed as days *before* first treatment, opposite in convention to all other `days_to_*` fields in the schema.

| Column | Description |
|---|---|
| `blood_test_id` | Surrogate integer PK populated from DuckDB `rowid` at load time |
| `patient_id` | Reference to the patient |
| `loinc_code` | Standardised LOINC code identifying the test |
| `loinc_name` | Human-readable LOINC test name. FK to `blood_data_reference_ranges` |
| `analyte_name` | Name of the substance being measured |
| `group` | Administrative grouping — likely indicates which lab panel or ordering group the test belongs to |
| `value` | Numeric measurement result |
| `unit` | Unit of measurement |
| `days_before_first_treatment` | Days before first treatment the sample was taken. Note: opposite direction to `days_to_*` fields elsewhere in the schema |

---

### blood_data_reference_ranges
**PK:** `loinc_name` | One row per test type. Lookup table of normal lab ranges shared across all patients. Sex-stratified because many lab values have different normal ranges for males and females.

| Column | Description |
|---|---|
| `loinc_name` | Test identifier — FK from `blood_data` |
| `analyte_name` | Name of the substance being measured |
| `group` | Lab panel or ordering group |
| `unit` | Unit of measurement |
| `normal_male_min` | Lower bound of normal range for males |
| `normal_male_max` | Upper bound of normal range for males |
| `normal_female_min` | Lower bound of normal range for females |
| `normal_female_max` | Upper bound of normal range for females |

---

## Views

### adjuvant_treatments
**PK:** `patient_id` | Filters `clinical_data` to the 479 patients who received any adjuvant treatment. A patient is included if any of `adjuvant_radiotherapy`, `adjuvant_systemic_therapy`, or `adjuvant_radiochemotherapy` is `'yes'`.

| Column | Description |
|---|---|
| `patient_id` | Reference to the patient |
| `adjuvant_treatment_intent` | Goal of adjuvant treatment (e.g. curative, palliative) |
| `adjuvant_radiotherapy` | Whether adjuvant radiotherapy was given (yes/no) |
| `adjuvant_radiotherapy_modality` | Type of radiotherapy administered (e.g. percutaneous radiotherapy) |
| `adjuvant_systemic_therapy` | Whether adjuvant systemic therapy was given (yes/no) |
| `adjuvant_systemic_therapy_modality` | Specific systemic therapy regimen (e.g. fluorouracil + cisplatin) |
| `adjuvant_radiochemotherapy` | Whether radiotherapy and chemotherapy were given concurrently (yes/no) |

---

### metastases
**PK:** `metastasis_id` | Unpivots the 4 wide metastasis column pairs in `clinical_data` into individual rows. Skips null locations. `prev_metastasis_id` enables self-referential chaining in the graph.

| Column | Description |
|---|---|
| `metastasis_id` | Surrogate ID in format `{patient_id}_met_{order}` |
| `patient_id` | Reference to the patient |
| `metastasis_order` | Sequence of this metastatic event (1–4). Verified chronologically ascending by `days_to_metastasis` |
| `locations` | Anatomical site of metastasis (e.g. Lung) |
| `days_to_metastasis` | Days from first treatment to this metastatic event |
| `prev_metastasis_id` | `metastasis_id` of the previous event in the chain. NULL on the first event for a patient |

---

### first_metastases
**PK:** — | Join table used exclusively as the source for the `HAD_METASTASIS` edge. Contains only the two FKs needed to link a `Patient` to their first `Metastasis` node.

| Column | Description |
|---|---|
| `patient_id` | Reference to the patient |
| `metastasis_id` | Reference to the first metastasis (`metastasis_order = 1`) |

---

### progressions
**PK:** `progression_id` | Unpivots the 2 wide progression column pairs in `clinical_data` into individual rows. Skips null progressions. `prev_progression_id` enables self-referential chaining in the graph.

| Column | Description |
|---|---|
| `progression_id` | Surrogate ID in format `{patient_id}_prog_{order}` |
| `patient_id` | Reference to the patient |
| `progression_order` | Sequence of this progression event (1–2) |
| `days_to_progress` | Days from first treatment to this progression event |
| `prev_progression_id` | `progression_id` of the previous event in the chain. NULL on the first event for a patient |

---

### first_progressions
**PK:** — | Join table used exclusively as the source for the `HAD_PROGRESSION` edge. Contains only the two FKs needed to link a `Patient` to their first `Progression` node.

| Column | Description |
|---|---|
| `patient_id` | Reference to the patient |
| `progression_id` | Reference to the first progression (`progression_order = 1`) |

---

### recurrences
**PK:** `patient_id` | Filters `clinical_data` to patients where `recurrence = 'yes'` (177 patients). At most one row per patient. The existence of a row implies recurrence occurred — no boolean flag is needed.

| Column | Description |
|---|---|
| `patient_id` | Reference to the patient |
| `days_to_recurrence` | Days from first treatment to recurrence |

---

### blood_test_reference_ranges
**PK:** — | Join table used as the source for the `HAS_REFERENCE_RANGE` edge. Links each `BloodTest` to its corresponding `ReferenceRange` via `loinc_name`.

| Column | Description |
|---|---|
| `blood_test_id` | Reference to the blood test |
| `loinc_name` | Reference to the reference range |

---

## Node Counts

| Node | Count |
|---|---|
| Patient | 763 |
| InitialDiagnosis | 763 |
| Tumor | 763 |
| TumorRemoval | 763 |
| LymphNodeStatus | 763 |
| TumorInvasion | 763 |
| FirstTreatment | 763 |
| AdjuvantTreatment | 479 |
| Metastasis | 156 |
| Progression | 193 |
| Recurrence | 177 |
| Outcome | 763 |
| BloodTest | 23234 |
| ReferenceRange | 38 |

---

## Graph Node Mapping (PuppyGraph)

| Node | Source | PK | Attributes |
|---|---|---|---|
| Patient | clinical_data | patient_id | patient_id, sex, smoking_status |
| InitialDiagnosis | clinical_data | patient_id | year_of_initial_diagnosis, age_at_initial_diagnosis, primarily_metastasis |
| Tumor | pathological_data | patient_id | primary_tumor_site, pt_stage, grading, hpv_association_p16, carcinoma_in_situ, histologic_type, infiltration_depth_in_mm |
| TumorRemoval | pathological_data | patient_id | resection_status, resection_status_carcinoma_in_situ, closest_resection_margin_in_cm |
| LymphNodeStatus | pathological_data | patient_id | pn_stage, number_of_positive_lymph_nodes, number_of_resected_lymph_nodes |
| TumorInvasion | pathological_data | patient_id | perinodal_invasion, lymphovascular_invasion_l, vascular_invasion_v, perineural_invasion_pn |
| FirstTreatment | clinical_data | patient_id | first_treatment_intent, first_treatment_modality, days_to_first_treatment |
| AdjuvantTreatment | adjuvant_treatments | patient_id | adjuvant_treatment_intent, adjuvant_radiotherapy, adjuvant_radiotherapy_modality, adjuvant_systemic_therapy, adjuvant_systemic_therapy_modality, adjuvant_radiochemotherapy |
| Metastasis | metastases | metastasis_id | metastasis_order, locations, days_to_metastasis |
| Progression | progressions | progression_id | progression_order, days_to_progress |
| Recurrence | recurrences | patient_id | days_to_recurrence |
| Outcome | clinical_data | patient_id | survival_status, survival_status_with_cause, days_to_last_information |
| BloodTest | blood_data | blood_test_id | value, unit, analyte_name, loinc_code, loinc_name, group, days_before_first_treatment |
| ReferenceRange | blood_data_reference_ranges | loinc_name | group, analyte_name, unit, normal_male_min, normal_male_max, normal_female_min, normal_female_max |

---

## Graph Edge Mapping (PuppyGraph)

| Edge | From Node | To Node | Source Table/View | FK |
|---|---|---|---|---|
| RECEIVED_INITIAL_DIAGNOSIS | Patient | InitialDiagnosis | clinical_data | patient_id |
| HAS_TUMOR | Patient | Tumor | pathological_data | patient_id |
| HAS_TUMOR_REMOVAL | Tumor | TumorRemoval | pathological_data | patient_id |
| HAS_LYMPH_NODE_STATUS | Tumor | LymphNodeStatus | pathological_data | patient_id |
| HAS_TUMOR_INVASION | Tumor | TumorInvasion | pathological_data | patient_id |
| UNDERWENT_FIRST_TREATMENT | Patient | FirstTreatment | clinical_data | patient_id |
| UNDERWENT_ADJUVANT_TREATMENT | Patient | AdjuvantTreatment | adjuvant_treatments | patient_id |
| HAD_METASTASIS | Patient | Metastasis | first_metastases | patient_id → metastasis_id |
| NEXT_METASTASIS | Metastasis | Metastasis | metastases | prev_metastasis_id → metastasis_id |
| HAD_PROGRESSION | Patient | Progression | first_progressions | patient_id → progression_id |
| NEXT_PROGRESSION | Progression | Progression | progressions | prev_progression_id → progression_id |
| HAD_RECURRENCE | Patient | Recurrence | recurrences | patient_id |
| HAS_OUTCOME | Patient | Outcome | clinical_data | patient_id |
| HAD_BLOOD_TEST | Patient | BloodTest | blood_data | patient_id → blood_test_id |
| HAS_REFERENCE_RANGE | BloodTest | ReferenceRange | blood_test_reference_ranges | blood_test_id → loinc_name |