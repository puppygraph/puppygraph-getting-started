-- OMOP CDM 5.3 DDL for Apache Spark tailored to MIMIC-IV demo data
-- Adjusted per data notes: bigint IDs, column order aligned to CSV headers, expanded varchar lengths, double precision numerics, plus extra MIMIC-IV tables

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/person` (
      person_id bigint NOT NULL,
      gender_concept_id integer NOT NULL,
      year_of_birth integer NOT NULL,
      month_of_birth integer,
      day_of_birth integer,
      birth_datetime timestamp,
      race_concept_id integer NOT NULL,
      ethnicity_concept_id integer NOT NULL,
      location_id integer,
      provider_id bigint,
      care_site_id bigint,
      person_source_value varchar(50),
      gender_source_value varchar(50),
      gender_source_concept_id integer,
      race_source_value varchar(50),
      race_source_concept_id integer,
      ethnicity_source_value varchar(50),
      ethnicity_source_concept_id integer
) USING DELTA LOCATION '/delta/mimic/person';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/observation_period` (
      observation_period_id bigint NOT NULL,
      person_id bigint NOT NULL,
      observation_period_start_date date NOT NULL,
      observation_period_end_date date NOT NULL,
      period_type_concept_id integer NOT NULL
) USING DELTA LOCATION '/delta/mimic/observation_period';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/visit_occurrence` (
      visit_occurrence_id bigint NOT NULL,
      person_id bigint NOT NULL,
      visit_concept_id integer NOT NULL,
      visit_start_date date NOT NULL,
      visit_start_datetime timestamp,
      visit_end_date date NOT NULL,
      visit_end_datetime timestamp,
      visit_type_concept_id integer NOT NULL,
      provider_id bigint,
      care_site_id bigint,
      visit_source_value varchar(50),
      visit_source_concept_id integer,
      admitting_source_concept_id integer,
      admitting_source_value varchar(50),
      discharge_to_concept_id integer,
      discharge_to_source_value varchar(50),
      preceding_visit_occurrence_id bigint
) USING DELTA LOCATION '/delta/mimic/visit_occurrence';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/visit_detail` (
      visit_detail_id bigint NOT NULL,
      person_id bigint NOT NULL,
      visit_detail_concept_id integer NOT NULL,
      visit_detail_start_date date NOT NULL,
      visit_detail_start_datetime timestamp,
      visit_detail_end_date date NOT NULL,
      visit_detail_end_datetime timestamp,
      visit_detail_type_concept_id integer NOT NULL,
      provider_id bigint,
      care_site_id bigint,
      admitting_source_concept_id integer,
      discharge_to_concept_id integer,
      preceding_visit_detail_id bigint,
      visit_detail_source_value varchar(255),
      visit_detail_source_concept_id integer,
      admitting_source_value varchar(50),
      discharge_to_source_value varchar(50),
      visit_detail_parent_id bigint,
      visit_occurrence_id bigint NOT NULL
) USING DELTA LOCATION '/delta/mimic/visit_detail';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/condition_occurrence` (
      condition_occurrence_id bigint NOT NULL,
      person_id bigint NOT NULL,
      condition_concept_id integer NOT NULL,
      condition_start_date date NOT NULL,
      condition_start_datetime timestamp,
      condition_end_date date,
      condition_end_datetime timestamp,
      condition_type_concept_id integer NOT NULL,
      stop_reason varchar(20),
      provider_id bigint,
      visit_occurrence_id bigint,
      visit_detail_id bigint,
      condition_source_value varchar(50),
      condition_source_concept_id integer,
      condition_status_source_value varchar(50),
      condition_status_concept_id integer
) USING DELTA LOCATION '/delta/mimic/condition_occurrence';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/drug_exposure` (
      drug_exposure_id bigint NOT NULL,
      person_id bigint NOT NULL,
      drug_concept_id integer NOT NULL,
      drug_exposure_start_date date NOT NULL,
      drug_exposure_start_datetime timestamp,
      drug_exposure_end_date date NOT NULL,
      drug_exposure_end_datetime timestamp,
      verbatim_end_date date,
      drug_type_concept_id integer NOT NULL,
      stop_reason varchar(20),
      refills integer,
      quantity double,
      days_supply integer,
      sig string,
      route_concept_id integer,
      lot_number varchar(50),
      provider_id bigint,
      visit_occurrence_id bigint,
      visit_detail_id bigint,
      drug_source_value varchar(255),
      drug_source_concept_id integer,
      route_source_value varchar(50),
      dose_unit_source_value varchar(50)
) USING DELTA LOCATION '/delta/mimic/drug_exposure';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/procedure_occurrence` (
      procedure_occurrence_id bigint NOT NULL,
      person_id bigint NOT NULL,
      procedure_concept_id integer NOT NULL,
      procedure_date date NOT NULL,
      procedure_datetime timestamp,
      procedure_type_concept_id integer NOT NULL,
      modifier_concept_id integer,
      quantity integer,
      provider_id bigint,
      visit_occurrence_id bigint,
      visit_detail_id bigint,
      procedure_source_value varchar(50),
      procedure_source_concept_id integer,
      modifier_source_value varchar(50)
) USING DELTA LOCATION '/delta/mimic/procedure_occurrence';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/device_exposure` (
      device_exposure_id bigint NOT NULL,
      person_id bigint NOT NULL,
      device_concept_id integer NOT NULL,
      device_exposure_start_date date NOT NULL,
      device_exposure_start_datetime timestamp,
      device_exposure_end_date date,
      device_exposure_end_datetime timestamp,
      device_type_concept_id integer NOT NULL,
      unique_device_id varchar(50),
      quantity integer,
      provider_id bigint,
      visit_occurrence_id bigint,
      visit_detail_id bigint,
      device_source_value varchar(50),
      device_source_concept_id integer
) USING DELTA LOCATION '/delta/mimic/device_exposure';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/measurement` (
      measurement_id bigint NOT NULL,
      person_id bigint NOT NULL,
      measurement_concept_id integer NOT NULL,
      measurement_date date NOT NULL,
      measurement_datetime timestamp,
      measurement_time varchar(10),
      measurement_type_concept_id integer NOT NULL,
      operator_concept_id integer,
      value_as_number double,
      value_as_concept_id integer,
      unit_concept_id integer,
      range_low double,
      range_high double,
      provider_id bigint,
      visit_occurrence_id bigint,
      visit_detail_id bigint,
      measurement_source_value varchar(50),
      measurement_source_concept_id integer,
      unit_source_value varchar(50),
      value_source_value varchar(50)
) USING DELTA LOCATION '/delta/mimic/measurement';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/observation` (
      observation_id bigint NOT NULL,
      person_id bigint NOT NULL,
      observation_concept_id integer NOT NULL,
      observation_date date NOT NULL,
      observation_datetime timestamp,
      observation_type_concept_id integer NOT NULL,
      value_as_number double,
      value_as_string varchar(255),
      value_as_concept_id integer,
      qualifier_concept_id integer,
      unit_concept_id integer,
      provider_id bigint,
      visit_occurrence_id bigint,
      visit_detail_id bigint,
      observation_source_value varchar(50),
      observation_source_concept_id integer,
      unit_source_value varchar(50),
      qualifier_source_value varchar(50)
) USING DELTA LOCATION '/delta/mimic/observation';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/death` (
      person_id bigint NOT NULL,
      death_date date NOT NULL,
      death_datetime timestamp,
      death_type_concept_id integer,
      cause_concept_id integer,
      cause_source_value varchar(50),
      cause_source_concept_id integer
) USING DELTA LOCATION '/delta/mimic/death';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/note` (
      note_id bigint NOT NULL,
      person_id bigint NOT NULL,
      note_date date NOT NULL,
      note_datetime timestamp,
      note_type_concept_id integer NOT NULL,
      note_class_concept_id integer NOT NULL,
      note_title varchar(250),
      note_text string NOT NULL,
      encoding_concept_id integer NOT NULL,
      language_concept_id integer NOT NULL,
      provider_id bigint,
      visit_occurrence_id bigint,
      visit_detail_id bigint,
      note_source_value varchar(50)
) USING DELTA LOCATION '/delta/mimic/note';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/note_nlp` (
      note_nlp_id bigint NOT NULL,
      note_id bigint NOT NULL,
      section_concept_id integer,
      snippet varchar(250),
      offset varchar(50),
      lexical_variant varchar(250) NOT NULL,
      note_nlp_concept_id integer,
      note_nlp_source_concept_id integer,
      nlp_system varchar(250),
      nlp_date date NOT NULL,
      nlp_datetime timestamp,
      term_exists varchar(1),
      term_temporal varchar(50),
      term_modifiers varchar(2000)
) USING DELTA LOCATION '/delta/mimic/note_nlp';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/specimen` (
      specimen_id bigint NOT NULL,
      person_id bigint NOT NULL,
      specimen_concept_id integer NOT NULL,
      specimen_type_concept_id integer NOT NULL,
      specimen_date date NOT NULL,
      specimen_datetime timestamp,
      quantity double,
      unit_concept_id integer,
      anatomic_site_concept_id integer,
      disease_status_concept_id integer,
      specimen_source_id varchar(255),
      specimen_source_value varchar(50),
      unit_source_value varchar(50),
      anatomic_site_source_value varchar(50),
      disease_status_source_value varchar(50)
) USING DELTA LOCATION '/delta/mimic/specimen';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/fact_relationship` (
      domain_concept_id_1 integer NOT NULL,
      fact_id_1 bigint NOT NULL,
      domain_concept_id_2 integer NOT NULL,
      fact_id_2 bigint NOT NULL,
      relationship_concept_id integer NOT NULL
) USING DELTA LOCATION '/delta/mimic/fact_relationship';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/location` (
      location_id integer NOT NULL,
      address_1 varchar(50),
      address_2 varchar(50),
      city varchar(50),
      state varchar(2),
      zip varchar(9),
      county varchar(20),
      location_source_value varchar(50)
) USING DELTA LOCATION '/delta/mimic/location';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/care_site` (
      care_site_id bigint NOT NULL,
      care_site_name varchar(255),
      place_of_service_concept_id integer,
      location_id integer,
      care_site_source_value varchar(50),
      place_of_service_source_value varchar(50)
) USING DELTA LOCATION '/delta/mimic/care_site';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/provider` (
      provider_id bigint NOT NULL,
      provider_name varchar(255),
      npi varchar(20),
      dea varchar(20),
      specialty_concept_id integer,
      care_site_id bigint,
      year_of_birth integer,
      gender_concept_id integer,
      provider_source_value varchar(50),
      specialty_source_value varchar(50),
      specialty_source_concept_id integer,
      gender_source_value varchar(50),
      gender_source_concept_id integer
) USING DELTA LOCATION '/delta/mimic/provider';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/payer_plan_period` (
      payer_plan_period_id bigint NOT NULL,
      person_id bigint NOT NULL,
      payer_plan_period_start_date date NOT NULL,
      payer_plan_period_end_date date NOT NULL,
      payer_concept_id integer,
      payer_source_value varchar(50),
      payer_source_concept_id integer,
      plan_concept_id integer,
      plan_source_value varchar(50),
      plan_source_concept_id integer,
      sponsor_concept_id integer,
      sponsor_source_value varchar(50),
      sponsor_source_concept_id integer,
      family_source_value varchar(50),
      stop_reason_concept_id integer,
      stop_reason_source_value varchar(50),
      stop_reason_source_concept_id integer
) USING DELTA LOCATION '/delta/mimic/payer_plan_period';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/cost` (
      cost_id bigint NOT NULL,
      cost_event_id bigint NOT NULL,
      cost_domain_id varchar(20) NOT NULL,
      cost_type_concept_id integer NOT NULL,
      currency_concept_id integer,
      total_charge double,
      total_cost double,
      total_paid double,
      paid_by_payer double,
      paid_by_patient double,
      paid_patient_copay double,
      paid_patient_coinsurance double,
      paid_patient_deductible double,
      paid_by_primary double,
      paid_ingredient_cost double,
      paid_dispensing_fee double,
      payer_plan_period_id bigint,
      amount_allowed double,
      revenue_code_concept_id integer,
      revenue_code_source_value varchar(50),
      drg_concept_id integer,
      drg_source_value varchar(3)
) USING DELTA LOCATION '/delta/mimic/cost';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/drug_era` (
      drug_era_id bigint NOT NULL,
      person_id bigint NOT NULL,
      drug_concept_id integer NOT NULL,
      drug_era_start_date date NOT NULL,
      drug_era_end_date date NOT NULL,
      drug_exposure_count integer,
      gap_days integer
) USING DELTA LOCATION '/delta/mimic/drug_era';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/dose_era` (
      dose_era_id bigint NOT NULL,
      person_id bigint NOT NULL,
      drug_concept_id integer NOT NULL,
      unit_concept_id integer NOT NULL,
      dose_value double NOT NULL,
      dose_era_start_date date NOT NULL,
      dose_era_end_date date NOT NULL
) USING DELTA LOCATION '/delta/mimic/dose_era';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/condition_era` (
      condition_era_id bigint NOT NULL,
      person_id bigint NOT NULL,
      condition_concept_id integer NOT NULL,
      condition_era_start_date date NOT NULL,
      condition_era_end_date date NOT NULL,
      condition_occurrence_count integer
) USING DELTA LOCATION '/delta/mimic/condition_era';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/metadata` (
      metadata_concept_id integer NOT NULL,
      metadata_type_concept_id integer NOT NULL,
      name varchar(250) NOT NULL,
      value_as_string varchar(250),
      value_as_concept_id integer,
      metadata_date date,
      metadata_datetime timestamp
) USING DELTA LOCATION '/delta/mimic/metadata';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/cdm_source` (
      cdm_source_name varchar(255) NOT NULL,
      cdm_source_abbreviation varchar(25),
      cdm_holder varchar(255),
      source_description string,
      source_documentation_reference varchar(255),
      cdm_etl_reference varchar(255),
      source_release_date date,
      cdm_release_date date,
      cdm_version varchar(10),
      vocabulary_version varchar(20)
) USING DELTA LOCATION '/delta/mimic/cdm_source';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/concept` (
      concept_id integer NOT NULL,
      concept_name varchar(255) NOT NULL,
      domain_id varchar(20) NOT NULL,
      vocabulary_id varchar(50) NOT NULL,
      concept_class_id varchar(20) NOT NULL,
      standard_concept varchar(1),
      concept_code varchar(255) NOT NULL,
      valid_start_date date NOT NULL,
      valid_end_date date NOT NULL,
      invalid_reason varchar(1)
) USING DELTA LOCATION '/delta/mimic/concept';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/vocabulary` (
      vocabulary_id varchar(50) NOT NULL,
      vocabulary_name varchar(255) NOT NULL,
      vocabulary_reference varchar(255) NOT NULL,
      vocabulary_version varchar(255),
      vocabulary_concept_id integer NOT NULL
) USING DELTA LOCATION '/delta/mimic/vocabulary';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/concept_relationship` (
      concept_id_1 integer NOT NULL,
      concept_id_2 integer NOT NULL,
      relationship_id varchar(20) NOT NULL,
      valid_start_date date NOT NULL,
      valid_end_date date NOT NULL,
      invalid_reason varchar(1)
) USING DELTA LOCATION '/delta/mimic/concept_relationship';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/cohort_definition` (
      cohort_definition_id integer NOT NULL,
      cohort_definition_name varchar(255) NOT NULL,
      cohort_definition_description string,
      definition_type_concept_id integer NOT NULL,
      cohort_definition_syntax string,
      subject_concept_id integer NOT NULL,
      cohort_initiation_date date
) USING DELTA LOCATION '/delta/mimic/cohort_definition';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/cohort` (
      cohort_definition_id integer NOT NULL,
      subject_id bigint NOT NULL,
      cohort_start_date date NOT NULL,
      cohort_end_date date NOT NULL
) USING DELTA LOCATION '/delta/mimic/cohort';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/cohort_attribute` (
      cohort_definition_id integer NOT NULL,
      subject_id bigint NOT NULL,
      cohort_start_date date NOT NULL,
      cohort_end_date date NOT NULL,
      attribute_definition_id integer NOT NULL,
      value_as_number double,
      value_as_concept_id integer
) USING DELTA LOCATION '/delta/mimic/cohort_attribute';

CREATE TABLE IF NOT EXISTS delta.`/delta/mimic/attribute_definition` (
      attribute_definition_id integer NOT NULL,
      attribute_name varchar(255) NOT NULL,
      attribute_description string,
      attribute_type_concept_id integer NOT NULL,
      attribute_syntax string
) USING DELTA LOCATION '/delta/mimic/attribute_definition';

