Build a complete clinical knowledge graph from OMOP CSV → MySQL → PuppyGraph.
This project links patients, visits, diagnoses, procedures, medications, labs, observations, and notes into one unified graph.


1. Requirements

Software
	•	macOS or Linux
	•	MySQL 8
	•	Docker
	•	Python 3

Dataset
	•	MIMIC-IV Demo OMOP dataset (or any OMOP CDM–formatted CSV dataset)



2. Overall Pipeline

Before running commands, here is the full ETL + graph-building pipeline:

2.1 Create OMOP MySQL Schema (via SQL)

Download the correct OMOP CDM DDL for MySQL  
Link: https://github.com/OHDSI/CommonDataModel
Use it to create an empty OMOP schema:
	•	person
	•	visit_occurrence
	•	condition_occurrence
	•	drug_exposure
	•	measurement
	•	note
...

2.2 STEP 2 — Import OMOP Vocabularies (Example)

Go to Athena (https://athena.ohdsi.org), download vocab CSVs:
	•	CONCEPT.csv
	•	CONCEPT_RELATIONSHIP.csv
	•	CONCEPT_ANCESTOR.csv
	•	VOCABULARY.csv
	•	DOMAIN.csv
	•	CONCEPT_CLASS.csv

Load them into MySQL using LOAD DATA.

2.3 — Map Your CSV Into OMOP Format (ETL)

If your dataset includes your own patient.csv, visit.csv, diagnosis.csv, you must map them to OMOP tables:
	•	Patients → person
	•	Visits → visit_occurrence
	•	Diagnoses → condition_occurrence
	•	Labs → measurement
	•	Notes → note

Then import the converted CSVs using LOAD DATA.



3. Load OMOP CSV Into MySQL

Enter MySQL:

	mysql --local-infile=1 -u root -p

Create a clean OMOP database:


	DROP DATABASE IF EXISTS omop;
	CREATE DATABASE omop;
	USE omop;

Run the SQL import script (omop_full.sql contains schema + vocab + ETL loading):

	mysql --local-infile=1 -u root -p < /Users/heyuanfei/omop_full.sql

Verify major tables:


	SELECT COUNT(*) FROM person;
	SELECT COUNT(*) FROM visit_occurrence;
	SELECT COUNT(*) FROM condition_occurrence;
	SELECT COUNT(*) FROM drug_exposure;
	SELECT COUNT(*) FROM measurement;
	...



4. ETL Mapping Examples

4.1 Patients → person

Your CSV:

	patient_id, sex, birthdate
	101, M, 1988-01-03

Mapped OMOP CSV:


	person_id, gender_concept_id, year_of_birth
	101, 8507, 1988

	•	8507 = male
	•	8532 = female

4.2 Visits → visit_occurrence

Your CSV:

	visit_id, patient_id, visit_date

Mapped OMOP fields:


	visit_occurrence_id, person_id, visit_start_date, visit_end_date

4.3 Diagnoses → condition_occurrence

Your CSV:
	patient_id, icd10_code, date

	Requires:
	
	•	date → condition_start_date

4.4 Load the Transformed Data

Example:

	LOAD DATA LOCAL INFILE 'person.csv'
	INTO TABLE person
	FIELDS TERMINATED BY ','
	IGNORE 1 LINES;

Repeat for:
	•	visit_occurrence
	•	condition_occurrence
	•	drug_exposure
	•	procedure_occurrence
	•	measurement
	•	observation
	•	note
	...



5. Start PuppyGraph (Docker)

docker stop puppy || true
docker rm puppy || true

docker run -d --name puppy \
  -p 7687:7687 \
  -p 8081:8081 \
  -p 8182:8182 \
  puppygraph/puppygraph:stable

Open the Web UI:
 http://localhost:8081



6. Configure MySQL Catalog in PuppyGraph

Start a local HTTP server for the JDBC driver:

cd ~/mysql-driver

python3 -m http.server 8000

Fill in the catalog settings:

Field	Value
Catalog Type	MySQL 8
Catalog Name	omop_mysql
Username	root
Password	your_password
JDBC URL	jdbc:mysql://host.docker.internal:3306/omop?allowPublicKeyRetrieval=true&useSSL=false
Driver Class	com.mysql.cj.jdbc.Driver
Driver URL	http://host.docker.internal:8000/mysql-connector-j-8.0.33.jar

Click Test → Continue → Submit.



7. Build Graph Schema
 Add OMOP tables as graph nodes:

	Table	                Node Label				ID
	person	                person					person_id
	visit_occurrence		visit_occurrence		visit_occurrence_id
	condition_occurrence	condition_occurrence	condition_occurrence_id
	drug_exposure			drug_exposure			drug_exposure_id
	procedure_occurrence	procedure_occurrence	procedure_occurrence_id
	measurement				measurement				measurement_id
	observation				observation				observation_id
	note					note					note_id



8. Add Graph Edges(Example)

8.1 PERSON → VISIT

	Field	Value
	Edge Label	PERSON_VISIT
	Table	visit_occurrence
	From	person.person_id
	To	visit_occurrence.visit_occurrence_id

8.2 Additional Edges(Example)

	Edge Label	From → To	Table
	VISIT_CONDITION	visit → condition	condition_occurrence
	VISIT_DRUG	visit → drug	drug_exposure
	VISIT_PROCEDURE	visit → procedure	procedure_occurrence
	VISIT_MEASUREMENT	visit → measurement	measurement
	VISIT_OBSERVATION	visit → observation	observation
	VISIT_NOTE	visit → note	note
	NOTE_NLP	note → note_nlp	note_nlp
	PERSON_DEATH	person → death	death
	PERSON_OBS_PERIOD	person → observation_period	observation_period


9. Query Comparison: Graph Query vs SQL Query

In this section, we demonstrate the differences between Graph Queries and SQL Queries when working with the OMOP dataset. While graph queries are easier to write and more efficient when querying complex relationships, SQL queries can become cumbersome and difficult to maintain.

1. Query: Patient’s Diagnoses and Medications
Graph Query (Cypher)

The following graph query retrieves all diagnoses and medication records for a specific patient, John Doe, for visits in 2025. The query leverages the graph structure of the database, where Patient, Visit, Diagnosis, and Medication are connected via relationships.

MATCH (p:Patient)-[:VISIT]->(v:Visit)-[:DIAGNOSES]->(d:Diagnosis)
MATCH (v)-[:PRESCRIBES]->(m:Medication)
WHERE p.name = 'John Doe' AND v.visit_date >= '2025-01-01' AND v.visit_date <= '2025-12-31'
RETURN p, v, d, m;

Explanation:
	•	The MATCH clause matches the nodes and their relationships.
	•	The RETURN statement fetches the required data for Patient, Visit, Diagnosis, and Medication.
	•	Graph queries directly connect nodes through relationships, making this query concise and easy to understand.

SQL Query

The following SQL query performs the same operation using traditional SQL with JOIN statements to combine the data from different tables.

SELECT p.*, v.*, d.*, m.*
FROM patients p
JOIN visits v ON p.patient_id = v.patient_id
JOIN diagnoses d ON v.visit_id = d.visit_id
JOIN medications m ON v.visit_id = m.visit_id
WHERE p.name = 'John Doe' AND v.visit_date >= '2025-01-01' AND v.visit_date <= '2025-12-31';

Explanation:
	•	The SQL query requires multiple JOIN operations to link the patients, visits, diagnoses, and medications tables.
	•	As the number of joins increases, the complexity and performance of the query can degrade, especially for large datasets.

2. Query: Medications Prescribed During Patient Visits
Graph Query (Cypher)

This graph query retrieves all medication prescriptions for John Doe during visits after January 1st, 2025. The graph query focuses on the relationships between Patient, Visit, and Medication.

MATCH (p:Patient)-[:VISIT]->(v:Visit)-[:PRESCRIBES]->(m:Medication)
WHERE p.name = 'John Doe' AND v.visit_date >= '2025-01-01'
RETURN p, v, m;

Explanation:
	•	The MATCH clause directly connects the patient to their visits and prescriptions.
	•	RETURN fetches the relevant patient, visit, and medication data.
	•	This query is straightforward, leveraging the graph database’s strength in handling connected data.


SQL Query

The equivalent SQL query to fetch the same data using multiple joins:

SELECT p.*, v.*, m.*
FROM patients p
JOIN visits v ON p.patient_id = v.patient_id
JOIN medications m ON v.visit_id = m.visit_id
WHERE p.name = 'John Doe' AND v.visit_date >= '2025-01-01';

Explanation:
	•	Again, the SQL query requires multiple JOIN operations.
	•	SQL queries can quickly become harder to manage as the number of tables and joins increases, especially when querying data across several relationships.


10. Final Graph Exploration
 In PuppyGraph:

	Visualize → Query Neighbors

Explore:
	•	Patient-centric networks
	•	Visit-level event timelines
	•	Diagnosis-drug patterns
	•	Longitudinal disease trajectories



11. Author

	Yuanfei He 
	Boston University
	Dec 10, 2025