# Reads CSV files into the corresponding Delta tables

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

tables = [
    ("person", "/tmp/1_omop_data_csv/person.csv"),
    ("observation_period", "/tmp/1_omop_data_csv/observation_period.csv"),
    ("visit_occurrence", "/tmp/1_omop_data_csv/visit_occurrence.csv"),
    ("visit_detail", "/tmp/1_omop_data_csv/visit_detail.csv"),
    ("condition_occurrence", "/tmp/1_omop_data_csv/condition_occurrence.csv"),
    ("drug_exposure", "/tmp/1_omop_data_csv/drug_exposure.csv"),
    ("procedure_occurrence", "/tmp/1_omop_data_csv/procedure_occurrence.csv"),
    ("device_exposure", "/tmp/1_omop_data_csv/device_exposure.csv"),
    ("measurement", "/tmp/1_omop_data_csv/measurement.csv"),
    ("observation", "/tmp/1_omop_data_csv/observation.csv"),
    ("death", "/tmp/1_omop_data_csv/death.csv"),
    ("note", "/tmp/1_omop_data_csv/note.csv"),
    ("note_nlp", "/tmp/1_omop_data_csv/note_nlp.csv"),
    ("specimen", "/tmp/1_omop_data_csv/specimen.csv"),
    ("fact_relationship", "/tmp/1_omop_data_csv/fact_relationship.csv"),
    ("location", "/tmp/1_omop_data_csv/location.csv"),
    ("care_site", "/tmp/1_omop_data_csv/care_site.csv"),
    ("provider", "/tmp/1_omop_data_csv/provider.csv"),
    ("payer_plan_period", "/tmp/1_omop_data_csv/payer_plan_period.csv"),
    ("cost", "/tmp/1_omop_data_csv/cost.csv"),
    ("drug_era", "/tmp/1_omop_data_csv/drug_era.csv"),
    ("dose_era", "/tmp/1_omop_data_csv/dose_era.csv"),
    ("condition_era", "/tmp/1_omop_data_csv/condition_era.csv"),
    ("metadata", "/tmp/1_omop_data_csv/metadata.csv"),
    ("cdm_source", "/tmp/1_omop_data_csv/cdm_source.csv"),
    ("concept", "/tmp/1_omop_data_csv/2b_concept.csv"),
    ("vocabulary", "/tmp/1_omop_data_csv/2b_vocabulary.csv"),
    ("concept_relationship", "/tmp/1_omop_data_csv/2b_concept_relationship.csv"),
    ("cohort_definition", "/tmp/1_omop_data_csv/cohort_definition.csv"),
    ("cohort", "/tmp/1_omop_data_csv/cohort.csv"),
    ("cohort_attribute", "/tmp/1_omop_data_csv/cohort_attribute.csv"),
    ("attribute_definition", "/tmp/1_omop_data_csv/attribute_definition.csv"),
]

for table, path in tables:
    table_name = f"delta.`/delta/mimic/{table}`"
    schema = spark.table(table_name).schema
    df = spark.read.options(header=True).schema(schema).csv(path)
    df.write.format("delta").mode("append").saveAsTable(table_name)
