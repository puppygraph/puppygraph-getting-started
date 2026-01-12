DROP DATABASE IF EXISTS omop;
CREATE DATABASE omop
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE omop;

SET GLOBAL local_infile = 1;
SET SESSION local_infile = 1;

CREATE TABLE person (
  person_id BIGINT PRIMARY KEY,
  gender_concept_id INT,
  year_of_birth INT,
  month_of_birth INT,
  day_of_birth INT,
  race_concept_id INT,
  ethnicity_concept_id INT
);

CREATE TABLE visit_occurrence (
  visit_occurrence_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  visit_concept_id INT,
  visit_start_date DATE,
  visit_end_date DATE
);

CREATE TABLE visit_detail (
  visit_detail_id BIGINT PRIMARY KEY,
  visit_occurrence_id BIGINT,
  person_id BIGINT,
  visit_detail_start_date DATE,
  visit_detail_end_date DATE
);

CREATE TABLE condition_occurrence (
  condition_occurrence_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  visit_occurrence_id BIGINT,
  condition_concept_id INT,
  condition_start_date DATE
);

CREATE TABLE drug_exposure (
  drug_exposure_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  visit_occurrence_id BIGINT,
  drug_concept_id INT,
  drug_exposure_start_date DATE
);

CREATE TABLE procedure_occurrence (
  procedure_occurrence_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  visit_occurrence_id BIGINT,
  procedure_concept_id INT,
  procedure_date DATE
);

CREATE TABLE observation (
  observation_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  observation_concept_id INT,
  observation_date DATE
);

CREATE TABLE measurement (
  measurement_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  measurement_concept_id INT,
  measurement_date DATE,
  value_as_number DOUBLE
);

CREATE TABLE device_exposure (
  device_exposure_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  device_concept_id INT,
  device_exposure_start_date DATE
);

CREATE TABLE specimen (
  specimen_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  specimen_concept_id INT,
  specimen_date DATE
);

CREATE TABLE death (
  person_id BIGINT PRIMARY KEY,
  death_date DATE,
  death_type_concept_id INT
);


CREATE TABLE provider (
  provider_id BIGINT PRIMARY KEY,
  specialty_concept_id INT,
  care_site_id BIGINT
);

CREATE TABLE care_site (
  care_site_id BIGINT PRIMARY KEY,
  location_id BIGINT,
  care_site_name VARCHAR(255)
);

CREATE TABLE location (
  location_id BIGINT PRIMARY KEY,
  city VARCHAR(100),
  state VARCHAR(50),
  country VARCHAR(50)
);

CREATE TABLE payer_plan_period (
  payer_plan_period_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  payer_concept_id INT,
  plan_concept_id INT,
  payer_plan_period_start_date DATE,
  payer_plan_period_end_date DATE
);


CREATE TABLE observation_period (
  observation_period_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  observation_period_start_date DATE,
  observation_period_end_date DATE
);


CREATE TABLE note (
  note_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  note_date DATE,
  note_text TEXT
);

CREATE TABLE note_nlp (
  note_nlp_id BIGINT PRIMARY KEY,
  note_id BIGINT,
  lexical_variant VARCHAR(255),
  note_nlp_concept_id INT
);


CREATE TABLE cost (
  cost_id BIGINT PRIMARY KEY,
  cost_event_id BIGINT,
  cost_domain_id VARCHAR(50),
  total_charge DOUBLE
);

CREATE TABLE fact_relationship (
  domain_concept_id_1 INT,
  fact_id_1 BIGINT,
  domain_concept_id_2 INT,
  fact_id_2 BIGINT,
  relationship_concept_id INT
);


CREATE TABLE condition_era (
  condition_era_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  condition_concept_id INT,
  condition_era_start_date DATE,
  condition_era_end_date DATE
);

CREATE TABLE drug_era (
  drug_era_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  drug_concept_id INT,
  drug_era_start_date DATE,
  drug_era_end_date DATE
);

CREATE TABLE dose_era (
  dose_era_id BIGINT PRIMARY KEY,
  person_id BIGINT,
  drug_concept_id INT,
  dose_era_start_date DATE,
  dose_era_end_date DATE
);


CREATE TABLE cohort (
  cohort_definition_id BIGINT,
  subject_id BIGINT,
  cohort_start_date DATE,
  cohort_end_date DATE
);

CREATE TABLE cohort_definition (
  cohort_definition_id BIGINT PRIMARY KEY,
  cohort_name VARCHAR(255),
  cohort_description TEXT
);

CREATE TABLE cohort_attribute (
  cohort_definition_id BIGINT,
  cohort_start_date DATE,
  cohort_end_date DATE,
  subject_id BIGINT,
  attribute_definition_id BIGINT,
  value_as_number DOUBLE
);

CREATE TABLE attribute_definition (
  attribute_definition_id BIGINT PRIMARY KEY,
  attribute_name VARCHAR(255),
  attribute_description TEXT
);


CREATE TABLE metadata (
  metadata_id BIGINT PRIMARY KEY,
  metadata_concept_id INT,
  metadata_type_concept_id INT,
  value_as_string VARCHAR(255)
);

CREATE TABLE cdm_source (
  cdm_source_name VARCHAR(255),
  cdm_release_date DATE,
  cdm_version VARCHAR(50)
);

CREATE TABLE concept (
  concept_id INT PRIMARY KEY,
  concept_name VARCHAR(255),
  domain_id VARCHAR(50),
  vocabulary_id VARCHAR(50),
  concept_class_id VARCHAR(50)
);

CREATE TABLE vocabulary (
  vocabulary_id VARCHAR(50) PRIMARY KEY,
  vocabulary_name VARCHAR(255)
);

CREATE TABLE concept_relationship (
  concept_id_1 INT,
  concept_id_2 INT,
  relationship_id VARCHAR(50)
);