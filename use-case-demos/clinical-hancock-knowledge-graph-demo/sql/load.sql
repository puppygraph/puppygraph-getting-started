CREATE DATABASE IF NOT EXISTS hancock_db;

CREATE TABLE hancock_db.blood_data_reference_ranges USING iceberg AS SELECT * FROM parquet.`/parquet_data/blood_data_reference_ranges.parquet`;
CREATE TABLE hancock_db.blood_data USING iceberg AS SELECT * FROM parquet.`/parquet_data/blood_data.parquet`;
CREATE TABLE hancock_db.clinical_data USING iceberg AS SELECT * FROM parquet.`/parquet_data/clinical_data.parquet`;
CREATE TABLE hancock_db.pathological_data USING iceberg AS SELECT * FROM parquet.`/parquet_data/pathological_data.parquet`;
CREATE TABLE hancock_db.metastases USING iceberg AS SELECT * FROM parquet.`/parquet_data/metastases.parquet`;
CREATE TABLE hancock_db.first_metastases USING iceberg AS SELECT * FROM parquet.`/parquet_data/first_metastases.parquet`;
CREATE TABLE hancock_db.progressions USING iceberg AS SELECT * FROM parquet.`/parquet_data/progressions.parquet`;
CREATE TABLE hancock_db.first_progressions USING iceberg AS SELECT * FROM parquet.`/parquet_data/first_progressions.parquet`;
CREATE TABLE hancock_db.recurrences USING iceberg AS SELECT * FROM parquet.`/parquet_data/recurrences.parquet`;
CREATE TABLE hancock_db.blood_test_reference_ranges USING iceberg AS SELECT * FROM parquet.`/parquet_data/blood_test_reference_ranges.parquet`;
CREATE TABLE hancock_db.adjuvant_treatments USING iceberg AS SELECT * FROM parquet.`/parquet_data/adjuvant_treatments.parquet`;
