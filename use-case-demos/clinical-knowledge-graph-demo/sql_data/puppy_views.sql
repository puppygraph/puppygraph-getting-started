--Nodes

drop view if exists 
faers_puppyview, drug_usage_puppyview, pdb_puppyview, umls_puppyview, 
snomed_puppyview, pharma_class_puppyview, usage_to_snomed_puppyview, 
usage_to_umls_puppyview, synonyms_to_parent_puppyview, snomed_to_doid_puppyview,
umls_to_doid_puppyview, stem_puppyview, vetprod2struct_puppyview,
struct2parent_puppyview, struct2obprod_puppyview, td2tc_puppyview,
drug_to_atc_puppyview, interactive_puppyview, ob_patent_puppyview, ob_exclusivity_puppyview;

create or replace view faers_puppyview as
select distinct meddra_code, meddra_name
from (
select id, meddra_code, meddra_name
from faers_ped fp 
union all
select id, meddra_code, meddra_name
from faers_ger fg 
union all
select id, meddra_code, meddra_name
from faers_female ff
union all
select id, meddra_code, meddra_name
from faers_male fm 
union all
select id, meddra_code, meddra_name
from faers f
) t;

create or replace view drug_usage_puppyview as
select distinct concept_id, concept_name
from omop_relationship or2;

create or replace view pdb_puppyview as
select distinct pdb, chain_id, accession, title, pubmed_id, exp_method, deposition_date, ligand_id
from pdb p;

create or replace view umls_puppyview as
select distinct id
from (
select xref::text as id
from doid_xref dx 
where starts_with(source, 'UMLS_CUI')
union all
select umls_cui::text as id
from omop_relationship or2 
) t
where id is not null;

create or replace view snomed_puppyview as
select distinct id
from (
select xref::int8 as id
from doid_xref dx 
where starts_with(source, 'SNOMED')
union all
select snomed_conceptid as id
from omop_relationship or2 
) t
where id is not null;

create or replace view pharma_class_puppyview as
select distinct class_code, source, name
from pharma_class pc;

create or replace view species_puppyview as
select distinct species
from vetomop v;

--Edges

create or replace view usage_to_snomed_puppyview as
select distinct concept_id, snomed_conceptid, snomed_full_name
from omop_relationship or2 
where snomed_conceptid is not null;

create or replace view usage_to_umls_puppyview as
select distinct concept_id, umls_cui, cui_semantic_type
from omop_relationship or2 
where umls_cui is not null;

create or replace view synonyms_to_parent_puppyview as
select syn_id, parent_id
from synonyms s 
where parent_id is not null;

create or replace view snomed_to_doid_puppyview as
select id, xref::bigint as xref, doid
from doid_xref dx 
where starts_with(source, 'SNOMED');

create or replace view umls_to_doid_puppyview as
select id, xref::text as xref, doid
from doid_xref dx 
where starts_with(source, 'UMLS_CUI');

create or replace view stem_puppyview as
select id, stem::text as stem
from structures
where stem is not null;

create or replace view vetprod2struct_puppyview as
select struct_id * 10000 + prodid as id, prodid, struct_id
from vetprod2struct vs; 

create or replace view struct2parent_puppyview as
select struct_id * 10000 + parent_id as id, struct_id, parent_id
from struct2parent sp;

create or replace view struct2obprod_puppyview as
select struct_id::bigint * 1000000 + prod_id::bigint as id, struct_id, prod_id, strength
from struct2obprod so; 

create or replace view td2tc_puppyview as
select target_id * 100000 + component_id as id, target_id, component_id
from td2tc;

create or replace view drug_to_atc_puppyview as
select sa.id, sa.struct_id, sa.atc_code, ad.ddd, ad.unit_type, ad.route, ad."comment" 
from struct2atc sa left join atc_ddd ad on sa.atc_code = ad.atc_code;

create or replace view interactive_puppyview as
select d.id, dc1.id as drug_class1_id, dc2.id as drug_class2_id, d.ddi_risk, d.description, d.source_id
from ddi d join drug_class dc1 on d.drug_class1 = dc1.name join drug_class dc2 on d.drug_class2 = dc2.name;

create or replace view ob_patent_puppyview as
select op.id, op2.id as product_id
from ob_patent op join ob_product op2 on op.appl_no = op2.appl_no and op.product_no = op2.product_no; 

create or replace view ob_exclusivity_puppyview as
select op.id, oe.id as product_id
from ob_exclusivity oe join ob_product op on op.appl_no = oe.appl_no and op.product_no = oe.product_no;