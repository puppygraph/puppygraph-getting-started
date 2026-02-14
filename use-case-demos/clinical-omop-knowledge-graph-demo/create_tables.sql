-- OMOP CDM 5.3 DDL for PostgreSQL tailored to MIMIC-IV demo data
-- Adjusted per data notes: bigint IDs, column order aligned to CSV headers, expanded varchar lengths, double precision numerics, plus extra MIMIC-IV tables
-- HINT DISTRIBUTE ON KEY (person_id)

DROP SCHEMA IF EXISTS mimic CASCADE;  
CREATE SCHEMA IF NOT EXISTS mimic;

CREATE TABLE mimic.person (
			person_id bigint NOT NULL,
			gender_concept_id integer NOT NULL,
			year_of_birth integer NOT NULL,
			month_of_birth integer NULL,
			day_of_birth integer NULL,
			birth_datetime timestamp NULL,
			race_concept_id integer NOT NULL,
			ethnicity_concept_id integer NOT NULL,
			location_id integer NULL,
			provider_id bigint NULL,
			care_site_id bigint NULL,
			person_source_value varchar(50) NULL,
			gender_source_value varchar(50) NULL,
			gender_source_concept_id integer NULL,
			race_source_value varchar(50) NULL,
			race_source_concept_id integer NULL,
			ethnicity_source_value varchar(50) NULL,
			ethnicity_source_concept_id integer NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.observation_period (
			observation_period_id bigint NOT NULL,
			person_id bigint NOT NULL,
			observation_period_start_date date NOT NULL,
			observation_period_end_date date NOT NULL,
			period_type_concept_id integer NOT NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.visit_occurrence (
			visit_occurrence_id bigint NOT NULL,
			person_id bigint NOT NULL,
			visit_concept_id integer NOT NULL,
			visit_start_date date NOT NULL,
			visit_start_datetime timestamp NULL,
			visit_end_date date NOT NULL,
			visit_end_datetime timestamp NULL,
			visit_type_concept_id integer NOT NULL,
			provider_id bigint NULL,
			care_site_id bigint NULL,
			visit_source_value varchar(50) NULL,
			visit_source_concept_id integer NULL,
			admitting_source_concept_id integer NULL,
			admitting_source_value varchar(50) NULL,
			discharge_to_concept_id integer NULL,
			discharge_to_source_value varchar(50) NULL,
			preceding_visit_occurrence_id bigint NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.visit_detail (
			visit_detail_id bigint NOT NULL,
			person_id bigint NOT NULL,
			visit_detail_concept_id integer NOT NULL,
			visit_detail_start_date date NOT NULL,
			visit_detail_start_datetime timestamp NULL,
			visit_detail_end_date date NOT NULL,
			visit_detail_end_datetime timestamp NULL,
			visit_detail_type_concept_id integer NOT NULL,
			provider_id bigint NULL,
			care_site_id bigint NULL,
			admitting_source_concept_id integer NULL,
			discharge_to_concept_id integer NULL,
			preceding_visit_detail_id bigint NULL,
			visit_detail_source_value varchar(255) NULL,
			visit_detail_source_concept_id integer NULL,
			admitting_source_value varchar(50) NULL,
			discharge_to_source_value varchar(50) NULL,
			visit_detail_parent_id bigint NULL,
			visit_occurrence_id bigint NOT NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.condition_occurrence (
			condition_occurrence_id bigint NOT NULL,
			person_id bigint NOT NULL,
			condition_concept_id integer NOT NULL,
			condition_start_date date NOT NULL,
			condition_start_datetime timestamp NULL,
			condition_end_date date NULL,
			condition_end_datetime timestamp NULL,
			condition_type_concept_id integer NOT NULL,
			stop_reason varchar(20) NULL,
			provider_id bigint NULL,
			visit_occurrence_id bigint NULL,
			visit_detail_id bigint NULL,
			condition_source_value varchar(50) NULL,
			condition_source_concept_id integer NULL,
			condition_status_source_value varchar(50) NULL,
			condition_status_concept_id integer NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.drug_exposure (
			drug_exposure_id bigint NOT NULL,
			person_id bigint NOT NULL,
			drug_concept_id integer NOT NULL,
			drug_exposure_start_date date NOT NULL,
			drug_exposure_start_datetime timestamp NULL,
			drug_exposure_end_date date NOT NULL,
			drug_exposure_end_datetime timestamp NULL,
			verbatim_end_date date NULL,
			drug_type_concept_id integer NOT NULL,
			stop_reason varchar(20) NULL,
			refills integer NULL,
			quantity double precision NULL,
			days_supply integer NULL,
			sig text NULL,
			route_concept_id integer NULL,
			lot_number varchar(50) NULL,
			provider_id bigint NULL,
			visit_occurrence_id bigint NULL,
			visit_detail_id bigint NULL,
			drug_source_value varchar(255) NULL,
			drug_source_concept_id integer NULL,
			route_source_value varchar(50) NULL,
			dose_unit_source_value varchar(50) NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.procedure_occurrence (
			procedure_occurrence_id bigint NOT NULL,
			person_id bigint NOT NULL,
			procedure_concept_id integer NOT NULL,
			procedure_date date NOT NULL,
			procedure_datetime timestamp NULL,
			procedure_type_concept_id integer NOT NULL,
			modifier_concept_id integer NULL,
			quantity integer NULL,
			provider_id bigint NULL,
			visit_occurrence_id bigint NULL,
			visit_detail_id bigint NULL,
			procedure_source_value varchar(50) NULL,
			procedure_source_concept_id integer NULL,
			modifier_source_value varchar(50) NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.device_exposure (
			device_exposure_id bigint NOT NULL,
			person_id bigint NOT NULL,
			device_concept_id integer NOT NULL,
			device_exposure_start_date date NOT NULL,
			device_exposure_start_datetime timestamp NULL,
			device_exposure_end_date date NULL,
			device_exposure_end_datetime timestamp NULL,
			device_type_concept_id integer NOT NULL,
			unique_device_id varchar(50) NULL,
			quantity integer NULL,
			provider_id bigint NULL,
			visit_occurrence_id bigint NULL,
			visit_detail_id bigint NULL,
			device_source_value varchar(50) NULL,
			device_source_concept_id integer NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.measurement (
			measurement_id bigint NOT NULL,
			person_id bigint NOT NULL,
			measurement_concept_id integer NOT NULL,
			measurement_date date NOT NULL,
			measurement_datetime timestamp NULL,
			measurement_time varchar(10) NULL,
			measurement_type_concept_id integer NOT NULL,
			operator_concept_id integer NULL,
			value_as_number double precision NULL,
			value_as_concept_id integer NULL,
			unit_concept_id integer NULL,
			range_low double precision NULL,
			range_high double precision NULL,
			provider_id bigint NULL,
			visit_occurrence_id bigint NULL,
			visit_detail_id bigint NULL,
			measurement_source_value varchar(50) NULL,
			measurement_source_concept_id integer NULL,
			unit_source_value varchar(50) NULL,
			value_source_value varchar(50) NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.observation (
			observation_id bigint NOT NULL,
			person_id bigint NOT NULL,
			observation_concept_id integer NOT NULL,
			observation_date date NOT NULL,
			observation_datetime timestamp NULL,
			observation_type_concept_id integer NOT NULL,
			value_as_number double precision NULL,
			value_as_string varchar(255) NULL,
			value_as_concept_id integer NULL,
			qualifier_concept_id integer NULL,
			unit_concept_id integer NULL,
			provider_id bigint NULL,
			visit_occurrence_id bigint NULL,
			visit_detail_id bigint NULL,
			observation_source_value varchar(50) NULL,
			observation_source_concept_id integer NULL,
			unit_source_value varchar(50) NULL,
			qualifier_source_value varchar(50) NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.death (
			person_id bigint NOT NULL,
			death_date date NOT NULL,
			death_datetime timestamp NULL,
			death_type_concept_id integer NULL,
			cause_concept_id integer NULL,
			cause_source_value varchar(50) NULL,
			cause_source_concept_id integer NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.note (
			note_id bigint NOT NULL,
			person_id bigint NOT NULL,
			note_date date NOT NULL,
			note_datetime timestamp NULL,
			note_type_concept_id integer NOT NULL,
			note_class_concept_id integer NOT NULL,
			note_title varchar(250) NULL,
			note_text text NOT NULL,
			encoding_concept_id integer NOT NULL,
			language_concept_id integer NOT NULL,
			provider_id bigint NULL,
			visit_occurrence_id bigint NULL,
			visit_detail_id bigint NULL,
			note_source_value varchar(50) NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.note_nlp (
			note_nlp_id bigint NOT NULL,
			note_id bigint NOT NULL,
			section_concept_id integer NULL,
			snippet varchar(250) NULL,
			"offset" varchar(50) NULL,
			lexical_variant varchar(250) NOT NULL,
			note_nlp_concept_id integer NULL,
			note_nlp_source_concept_id integer NULL,
			nlp_system varchar(250) NULL,
			nlp_date date NOT NULL,
			nlp_datetime timestamp NULL,
			term_exists varchar(1) NULL,
			term_temporal varchar(50) NULL,
			term_modifiers varchar(2000) NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.specimen (
			specimen_id bigint NOT NULL,
			person_id bigint NOT NULL,
			specimen_concept_id integer NOT NULL,
			specimen_type_concept_id integer NOT NULL,
			specimen_date date NOT NULL,
			specimen_datetime timestamp NULL,
			quantity double precision NULL,
			unit_concept_id integer NULL,
			anatomic_site_concept_id integer NULL,
			disease_status_concept_id integer NULL,
			specimen_source_id varchar(255) NULL,
			specimen_source_value varchar(50) NULL,
			unit_source_value varchar(50) NULL,
			anatomic_site_source_value varchar(50) NULL,
			disease_status_source_value varchar(50) NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.fact_relationship (
			domain_concept_id_1 integer NOT NULL,
			fact_id_1 bigint NOT NULL,
			domain_concept_id_2 integer NOT NULL,
			fact_id_2 bigint NOT NULL,
			relationship_concept_id integer NOT NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.location (
			location_id integer NOT NULL,
			address_1 varchar(50) NULL,
			address_2 varchar(50) NULL,
			city varchar(50) NULL,
			state varchar(2) NULL,
			zip varchar(9) NULL,
			county varchar(20) NULL,
			location_source_value varchar(50) NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.care_site (
			care_site_id bigint NOT NULL,
			care_site_name varchar(255) NULL,
			place_of_service_concept_id integer NULL,
			location_id integer NULL,
			care_site_source_value varchar(50) NULL,
			place_of_service_source_value varchar(50) NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.provider (
			provider_id bigint NOT NULL,
			provider_name varchar(255) NULL,
			npi varchar(20) NULL,
			dea varchar(20) NULL,
			specialty_concept_id integer NULL,
			care_site_id bigint NULL,
			year_of_birth integer NULL,
			gender_concept_id integer NULL,
			provider_source_value varchar(50) NULL,
			specialty_source_value varchar(50) NULL,
			specialty_source_concept_id integer NULL,
			gender_source_value varchar(50) NULL,
			gender_source_concept_id integer NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.payer_plan_period (
			payer_plan_period_id bigint NOT NULL,
			person_id bigint NOT NULL,
			payer_plan_period_start_date date NOT NULL,
			payer_plan_period_end_date date NOT NULL,
			payer_concept_id integer NULL,
			payer_source_value varchar(50) NULL,
			payer_source_concept_id integer NULL,
			plan_concept_id integer NULL,
			plan_source_value varchar(50) NULL,
			plan_source_concept_id integer NULL,
			sponsor_concept_id integer NULL,
			sponsor_source_value varchar(50) NULL,
			sponsor_source_concept_id integer NULL,
			family_source_value varchar(50) NULL,
			stop_reason_concept_id integer NULL,
			stop_reason_source_value varchar(50) NULL,
			stop_reason_source_concept_id integer NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.cost (
			cost_id bigint NOT NULL,
			cost_event_id bigint NOT NULL,
			cost_domain_id varchar(20) NOT NULL,
			cost_type_concept_id integer NOT NULL,
			currency_concept_id integer NULL,
			total_charge double precision NULL,
			total_cost double precision NULL,
			total_paid double precision NULL,
			paid_by_payer double precision NULL,
			paid_by_patient double precision NULL,
			paid_patient_copay double precision NULL,
			paid_patient_coinsurance double precision NULL,
			paid_patient_deductible double precision NULL,
			paid_by_primary double precision NULL,
			paid_ingredient_cost double precision NULL,
			paid_dispensing_fee double precision NULL,
			payer_plan_period_id bigint NULL,
			amount_allowed double precision NULL,
			revenue_code_concept_id integer NULL,
			revenue_code_source_value varchar(50) NULL,
			drg_concept_id integer NULL,
			drg_source_value varchar(3) NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.drug_era (
			drug_era_id bigint NOT NULL,
			person_id bigint NOT NULL,
			drug_concept_id integer NOT NULL,
			drug_era_start_date date NOT NULL,
			drug_era_end_date date NOT NULL,
			drug_exposure_count integer NULL,
			gap_days integer NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.dose_era (
			dose_era_id bigint NOT NULL,
			person_id bigint NOT NULL,
			drug_concept_id integer NOT NULL,
			unit_concept_id integer NOT NULL,
			dose_value double precision NOT NULL,
			dose_era_start_date date NOT NULL,
			dose_era_end_date date NOT NULL );
--HINT DISTRIBUTE ON KEY (person_id)
CREATE TABLE mimic.condition_era (
			condition_era_id bigint NOT NULL,
			person_id bigint NOT NULL,
			condition_concept_id integer NOT NULL,
			condition_era_start_date date NOT NULL,
			condition_era_end_date date NOT NULL,
			condition_occurrence_count integer NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.metadata (
			metadata_concept_id integer NOT NULL,
			metadata_type_concept_id integer NOT NULL,
			name varchar(250) NOT NULL,
			value_as_string varchar(250) NULL,
			value_as_concept_id integer NULL,
			metadata_date date NULL,
			metadata_datetime timestamp NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.cdm_source (
			cdm_source_name varchar(255) NOT NULL,
			cdm_source_abbreviation varchar(25) NULL,
			cdm_holder varchar(255) NULL,
			source_description text NULL,
			source_documentation_reference varchar(255) NULL,
			cdm_etl_reference varchar(255) NULL,
			source_release_date date NULL,
			cdm_release_date date NULL,
			cdm_version varchar(10) NULL,
			vocabulary_version varchar(20) NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.concept (
			concept_id integer NOT NULL,
			concept_name varchar(255) NOT NULL,
			domain_id varchar(20) NOT NULL,
			vocabulary_id varchar(50) NOT NULL,
			concept_class_id varchar(20) NOT NULL,
			standard_concept varchar(1) NULL,
			concept_code varchar(255) NOT NULL,
			valid_start_date date NOT NULL,
			valid_end_date date NOT NULL,
			invalid_reason varchar(1) NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.vocabulary (
			vocabulary_id varchar(50) NOT NULL,
			vocabulary_name varchar(255) NOT NULL,
			vocabulary_reference varchar(255) NOT NULL,
			vocabulary_version varchar(255) NULL,
			vocabulary_concept_id integer NOT NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.concept_relationship (
			concept_id_1 integer NOT NULL,
			concept_id_2 integer NOT NULL,
			relationship_id varchar(20) NOT NULL,
			valid_start_date date NOT NULL,
			valid_end_date date NOT NULL,
			invalid_reason varchar(1) NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.cohort_definition (
			cohort_definition_id integer NOT NULL,
			cohort_definition_name varchar(255) NOT NULL,
			cohort_definition_description text NULL,
			definition_type_concept_id integer NOT NULL,
			cohort_definition_syntax text NULL,
			subject_concept_id integer NOT NULL,
			cohort_initiation_date date NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.cohort (
			cohort_definition_id integer NOT NULL,
			subject_id bigint NOT NULL,
			cohort_start_date date NOT NULL,
			cohort_end_date date NOT NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.cohort_attribute (
			cohort_definition_id integer NOT NULL,
			subject_id bigint NOT NULL,
			cohort_start_date date NOT NULL,
			cohort_end_date date NOT NULL,
			attribute_definition_id integer NOT NULL,
			value_as_number double precision NULL,
			value_as_concept_id integer NULL );
--HINT DISTRIBUTE ON RANDOM
CREATE TABLE mimic.attribute_definition (
			attribute_definition_id integer NOT NULL,
			attribute_name varchar(255) NOT NULL,
			attribute_description text NULL,
			attribute_type_concept_id integer NOT NULL,
			attribute_syntax text NULL );
