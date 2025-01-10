import json
import argparse
import time
from uuid import uuid4

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer,SerializationContext, MessageField


DELAY_TIME = 0.01
SNAPSHOT_DATA_PATH = "data/snapshot_data.json"
INCREMENTAL_DATA_PATH = "data/incremental_data.json"

# Kafka and Schema Registry configuration
SERVER_URL = "<server_url>"
SCHEMA_REGISTRY_URL = "<schema_registry_url>"
JWT_TOKEN = "<jwt_token>"
PASSWORD = "token:" + JWT_TOKEN
TOPIC_PREFIX = "pg_"

SCHEMAS = {
  "Account": """
    {
        "name": "Account",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "accountId", "type": "long"},
            {"name": "createTime", "type": "string"},
            {"name": "isBlocked", "type": "boolean"},
            {"name": "accountType", "type": "string"},
            {"name": "nickname", "type": "string"},
            {"name": "phonenum", "type": "string"},
            {"name": "email", "type": "string"},
            {"name": "freqLoginType", "type": "string"},
            {"name": "lastLoginTime", "type": "string"},
            {"name": "accountLevel", "type": "string"}
        ]
    }
    """,
  "AccountRepayLoan": """
    {
        "name": "AccountRepayLoan",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "accountrepayloanId", "type": "long"},
            {"name": "accountId", "type": "long"},
            {"name": "loanId", "type": "long"},
            {"name": "amount", "type": "double"},
            {"name": "createTime", "type": "string"}
        ]
    }
    """,
  "AccountTransferAccount": """
    {
        "name": "AccountTransferAccount",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "accounttransferaccountId", "type": "long"},
            {"name": "fromId", "type": "long"},
            {"name": "toId", "type": "long"},
            {"name": "amount", "type": "double"},
            {"name": "createTime", "type": "string"},
            {"name": "orderNum", "type": "string"},
            {"name": "comment", "type": "string"},
            {"name": "payType", "type": "string"},
            {"name": "goodsType", "type": "string"}
        ]
    }
    """,
  "AccountWithdrawAccount": """
    {
        "name": "AccountWithdrawAccount",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "accountwithdrawaccountId", "type": "long"},
            {"name": "fromId", "type": "long"},
            {"name": "toId", "type": "long"},
            {"name": "amount", "type": "double"},
            {"name": "createTime", "type": "string"}
        ]
    }
    """,
  "Company": """
    {
        "name": "Company",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "companyId", "type": "long"},
            {"name": "companyName", "type": "string"},
            {"name": "isBlocked", "type": "boolean"},
            {"name": "createTime", "type": "string"},
            {"name": "country", "type": "string"},
            {"name": "city", "type": "string"},
            {"name": "business", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "url", "type": "string"}
        ]
    }
    """,
  "CompanyApplyLoan": """
    {
        "name": "CompanyApplyLoan",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "companyapplyloanId", "type": "long"},
            {"name": "companyId", "type": "long"},
            {"name": "loanId", "type": "long"},
            {"name": "createTime", "type": "string"},
            {"name": "org", "type": "string"}
        ]
    }
    """,
  "CompanyGuaranteeCompany": """
    {
        "name": "CompanyGuaranteeCompany",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "companyguaranteecompanyId", "type": "long"},
            {"name": "fromId", "type": "long"},
            {"name": "toId", "type": "long"},
            {"name": "createTime", "type": "string"},
            {"name": "relation", "type": "string"}
        ]
    }
    """,
  "CompanyInvestCompany": """
    {
        "name": "CompanyInvestCompany",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "companyinvestcompanyId", "type": "long"},
            {"name": "investorId", "type": "long"},
            {"name": "companyId", "type": "long"},
            {"name": "ratio", "type": "double"},
            {"name": "createTime", "type": "string"}
        ]
    }
    """,
  "CompanyOwnAccount": """
    {
        "name": "CompanyOwnAccount",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "companyownaccountId", "type": "long"},
            {"name": "companyId", "type": "long"},
            {"name": "accountId", "type": "long"},
            {"name": "createTime", "type": "string"}
        ]
    }
    """,
  "Loan": """
    {
        "name": "Loan",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "loanId", "type": "long"},
            {"name": "loanAmount", "type": "double"},
            {"name": "balance", "type": "double"},
            {"name": "createTime", "type": "string"},
            {"name": "loanUsage", "type": "string"},
            {"name": "interestRate", "type": "double"}
        ]
    }
    """,
  "LoanDepositAccount": """
    {
        "name": "LoanDepositAccount",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "loandepositaccountId", "type": "long"},
            {"name": "loanId", "type": "long"},
            {"name": "accountId", "type": "long"},
            {"name": "amount", "type": "double"},
            {"name": "createTime", "type": "string"}
        ]
    }
    """,
  "Medium": """
    {
        "name": "Medium",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "mediumId", "type": "long"},
            {"name": "mediumType", "type": "string"},
            {"name": "isBlocked", "type": "boolean"},
            {"name": "createTime", "type": "string"},
            {"name": "lastLoginTime", "type": "string"},
            {"name": "riskLevel", "type": "string"}
        ]
    }
    """,
  "MediumSignInAccount": """
    {
        "name": "MediumSignInAccount",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "mediumsigninaccountId", "type": "long"},
            {"name": "mediumId", "type": "long"},
            {"name": "accountId", "type": "long"},
            {"name": "createTime", "type": "string"},
            {"name": "location", "type": "string"}
        ]
    }
    """,
  "Person": """
    {
        "name": "Person",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "personId", "type": "long"},
            {"name": "personName", "type": "string"},
            {"name": "isBlocked", "type": "boolean"},
            {"name": "createTime", "type": "string"},
            {"name": "gender", "type": "string"},
            {"name": "birthday", "type": "string"},
            {"name": "country", "type": "string"},
            {"name": "city", "type": "string"}
        ]
    }
    """,
  "PersonApplyLoan": """
    {
        "name": "PersonApplyLoan",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "personapplyloanId", "type": "long"},
            {"name": "personId", "type": "long"},
            {"name": "loanId", "type": "long"},
            {"name": "createTime", "type": "string"},
            {"name": "org", "type": "string"}
        ]
    }
    """,
  "PersonGuaranteePerson": """
    {
        "name": "PersonGuaranteePerson",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "personguaranteepersonId", "type": "long"},
            {"name": "fromId", "type": "long"},
            {"name": "toId", "type": "long"},
            {"name": "createTime", "type": "string"},
            {"name": "relation", "type": "string"}
        ]
    }
    """,
  "PersonInvestCompany": """
    {
        "name": "PersonInvestCompany",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "personinvestcompanyId", "type": "long"},
            {"name": "investorId", "type": "long"},
            {"name": "companyId", "type": "long"},
            {"name": "ratio", "type": "double"},
            {"name": "createTime", "type": "string"}
        ]
    }
    """,
  "PersonOwnAccount": """
    {
        "name": "PersonOwnAccount",
        "type": "record",
        "fields": [
            {"name": "label", "type": "string"},
            {"name": "personownaccountId", "type": "long"},
            {"name": "personId", "type": "long"},
            {"name": "accountId", "type": "long"},
            {"name": "createTime", "type": "string"}
        ]
    }
    """
}

def delivery_report(err, msg):
  """Reports the success or failure of a message delivery."""
  if err is not None:
    print(f"Delivery failed for record {msg.key()}: {err}")
  else:
    print(f"Record {msg.key()} successfully produced to {msg.topic()} "
          f"[{msg.partition()}] at offset {msg.offset()}")

def setup():
    producer_config = {
        'bootstrap.servers': SERVER_URL,
        'sasl.mechanism': 'PLAIN',
        'security.protocol': 'SASL_SSL',
        'sasl.username': 'user',
        'sasl.password': PASSWORD
    }
    producer = Producer(producer_config)
    schema_registry_config = {
        'url': SCHEMA_REGISTRY_URL,
        'basic.auth.user.info': 'user:' + PASSWORD
    }
    schema_registry_client = SchemaRegistryClient(schema_registry_config)
    string_serializer = StringSerializer('utf_8')
    avro_serializer_dict = {}
    for table_name, schema_str in SCHEMAS.items():
        avro_serializer_dict[table_name] = AvroSerializer(schema_registry_client, schema_str)
    
    return producer, string_serializer, avro_serializer_dict

def import_data(file_path, delay_time=0):
    producer, string_serializer, avro_serializer_dict = setup()
    with open(file_path, 'r') as f:
        data_list = json.load(f)
    for data in data_list:
        table_name, data_value = data["table_name"], data["data_value"]
        topic = TOPIC_PREFIX + table_name
        avro_serializer = avro_serializer_dict[table_name]
        key_field = table_name + str(data_value.get(f"{table_name.lower()}Id"))
        producer.produce(
            topic = topic,
            key = string_serializer(key_field),
            value = avro_serializer(data_value, SerializationContext(topic, MessageField.VALUE)),
            on_delivery = delivery_report
        )
        producer.poll(0)
        time.sleep(delay_time)

    producer.flush()

def import_snapshot_data():
    import_data(SNAPSHOT_DATA_PATH)

def import_incremental_data():
    import_data(INCREMENTAL_DATA_PATH, delay_time=DELAY_TIME)

def main():
    parser = argparse.ArgumentParser(description='Import snapshot data and incremental data.')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', action='store_true', help='Import snapshot data.')
    group.add_argument('-i', action='store_true', help='Import incremental data.')
    args = parser.parse_args()
    
    if args.s:
        print("Importing snapshot data...")
        import_snapshot_data()
        print("Finished importing snapshot data.")
        
    if args.i:
        print("Importing incremental data...")
        import_incremental_data()
        print("Finished importing incremental data.")


if __name__ == "__main__":
    main()
 
  