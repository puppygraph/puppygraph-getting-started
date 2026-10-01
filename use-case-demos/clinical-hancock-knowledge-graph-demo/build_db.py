"""Build DuckDB tables and views from source JSON files."""

import duckdb
from config import DB_PATH

def load_tables(conn):
    conn.sql("""
        CREATE OR REPLACE TABLE clinical_data AS
        SELECT * REPLACE (
            CAST(patient_id AS VARCHAR) AS patient_id,
            CAST(year_of_initial_diagnosis AS SMALLINT) AS year_of_initial_diagnosis,
            CAST(age_at_initial_diagnosis AS SMALLINT) AS age_at_initial_diagnosis,
            CAST(days_to_first_treatment AS INTEGER) AS days_to_first_treatment,
            CAST(days_to_last_information AS INTEGER) AS days_to_last_information,
            CAST(days_to_recurrence AS INTEGER) AS days_to_recurrence,
            CAST(days_to_metastasis_1 AS INTEGER) AS days_to_metastasis_1,
            CAST(days_to_metastasis_2 AS INTEGER) AS days_to_metastasis_2,
            CAST(days_to_metastasis_3 AS INTEGER) AS days_to_metastasis_3,
            CAST(days_to_metastasis_4 AS INTEGER) AS days_to_metastasis_4,
            CAST(days_to_progress_1 AS INTEGER) AS days_to_progress_1,
            CAST(days_to_progress_2 AS INTEGER) AS days_to_progress_2
        )
        FROM read_json('json/clinical_data.json')
    """)

    ## Strip left-censored '<' values and cast inline
    conn.sql("""
        CREATE OR REPLACE TABLE pathological_data AS
        SELECT * REPLACE (
            CAST(patient_id AS VARCHAR) AS patient_id,
            CAST(infiltration_depth_in_mm AS DOUBLE) AS infiltration_depth_in_mm,
            TRY_CAST(REPLACE(closest_resection_margin_in_cm::VARCHAR, '<', '') AS DOUBLE) AS closest_resection_margin_in_cm,
            CAST(number_of_positive_lymph_nodes AS SMALLINT) AS number_of_positive_lymph_nodes,
            CAST(number_of_resected_lymph_nodes AS SMALLINT) AS number_of_resected_lymph_nodes
        )
        FROM read_json('json/pathological_data.json')
    """)

    ## Add PK inline via rowid
    conn.sql("""
        CREATE OR REPLACE TABLE blood_data AS
        SELECT
            row_number() OVER () AS blood_test_id,
            * REPLACE (
                CAST(patient_id AS VARCHAR) AS patient_id,
                CAST(value AS DOUBLE) AS value,
                CAST(days_before_first_treatment AS INTEGER) AS days_before_first_treatment
            )
        FROM read_json('json/blood_data.json')
    """)

    conn.sql("""
        CREATE OR REPLACE TABLE blood_data_reference_ranges AS
        SELECT * REPLACE (
            CAST(normal_male_min AS DOUBLE) AS normal_male_min,
            CAST(normal_male_max AS DOUBLE) AS normal_male_max,
            CAST(normal_female_min AS DOUBLE) AS normal_female_min,
            CAST(normal_female_max AS DOUBLE) AS normal_female_max
        )
        FROM read_json('json/blood_data_reference_ranges.json')
    """)

def load_views(conn):
    ## metastases
    conn.sql("""
        CREATE OR REPLACE VIEW metastases AS
        WITH locations AS (
            UNPIVOT clinical_data
            ON metastasis_1_locations AS '1',
                metastasis_2_locations AS '2',
                metastasis_3_locations AS '3',
                metastasis_4_locations AS '4'
            INTO
            NAME metastasis_order
            VALUE locations
        ),
        days_to AS (
            UNPIVOT clinical_data
            ON days_to_metastasis_1 AS '1',
                days_to_metastasis_2 AS '2',
                days_to_metastasis_3 AS '3',
                days_to_metastasis_4 AS '4'
            INTO
                NAME metastasis_order
                VALUE days_to_metastasis
        )
        SELECT
            l.patient_id || '_met_' || l.metastasis_order::INT AS metastasis_id,
            l.patient_id,
            l.metastasis_order::INT AS metastasis_order,
            l.locations,
            d.days_to_metastasis,
            CASE WHEN l.metastasis_order::INT > 1
                THEN l.patient_id || '_met_' || (l.metastasis_order::INT - 1)
            END AS prev_metastasis_id
        FROM locations l
        JOIN days_to d
            ON l.patient_id = d.patient_id
                AND l.metastasis_order = d.metastasis_order
        WHERE l.locations IS NOT NULL;
    """)

    ## first_metastases
    conn.sql("""
        CREATE OR REPLACE VIEW first_metastases AS
        SELECT
            c.patient_id,
            c.patient_id || '_met_1' AS metastasis_id
        FROM clinical_data c
        WHERE c.metastasis_1_locations IS NOT NULL;
    """)

    ## progressions
    conn.sql("""
        CREATE OR REPLACE VIEW progressions AS
        WITH days_to AS (
            UNPIVOT clinical_data
                ON days_to_progress_1 AS '1',
                    days_to_progress_2 AS '2'
            INTO
                NAME progression_order
                VALUE days_to_progress
        )
        SELECT
            d.patient_id || '_prog_' || d.progression_order::INT AS progression_id,
            d.patient_id,
            d.progression_order::INT as progression_order,
            d.days_to_progress,
            CASE WHEN d.progression_order::INT > 1
                THEN d.patient_id || '_prog_' || (d.progression_order::INT - 1)
            END AS prev_progression_id
        FROM days_to d
        WHERE d.days_to_progress IS NOT NULL;
    """)

    ## first_progressions
    conn.sql("""
        CREATE OR REPLACE VIEW first_progressions AS
        SELECT
            c.patient_id,
            c.patient_id || '_prog_1' AS progression_id
        FROM clinical_data c
        WHERE c.progress_1 = 'yes';
    """)

    ## recurrences
    conn.sql("""
        CREATE OR REPLACE VIEW recurrences AS
        SELECT
            c.patient_id,
            c.days_to_recurrence
        FROM clinical_data c
        WHERE c.recurrence = 'yes';
    """)

    ## blood_test_reference_ranges
    conn.sql("""
        CREATE OR REPLACE VIEW blood_test_reference_ranges AS
        SELECT
            b.blood_test_id,
            r.loinc_name
        FROM blood_data b
        JOIN blood_data_reference_ranges r
        ON b.loinc_name = r.loinc_name
    """)

    ## adjuvant_treatments
    conn.sql("""
        CREATE OR REPLACE VIEW adjuvant_treatments AS
            SELECT
                c.patient_id,
                c.adjuvant_treatment_intent,
                c.adjuvant_radiotherapy,
                c.adjuvant_radiotherapy_modality,
                c.adjuvant_systemic_therapy,
                c.adjuvant_systemic_therapy_modality,
                c.adjuvant_radiochemotherapy
            FROM clinical_data c
            WHERE adjuvant_radiotherapy = 'yes'
                OR adjuvant_systemic_therapy = 'yes'
                OR adjuvant_radiochemotherapy = 'yes'
    """)

def main():
    conn = duckdb.connect(DB_PATH)

    try:
        load_tables(conn)
        load_views(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
