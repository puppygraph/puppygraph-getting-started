from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
import argparse
import json
import time

table_array=["Account", "AccountRepayLoan", "AccountTransferAccount", "AccountWithdrawAccount", "Company", "CompanyApplyLoan", "CompanyGuaranteeCompany", "CompanyInvestCompany", "CompanyOwnAccount", "Loan", "LoanDepositAccount", "Medium", "MediumSignInAccount", "Person", "PersonApplyLoan", "PersonGuaranteePerson", "PersonInvestCompany", "PersonOwnAccount"]
SNAPSHOT_DATA_PATH = "data/snapshot_data"
INCREMENTAL_DATA_PATH = "data/incremental_data.ndjson"
SERVER_URL = "localhost:19092"


def create_topic(bootstrap_servers, topic_name, num_partitions, replication_factor):
    conf = {'bootstrap.servers': bootstrap_servers}
    admin_client = AdminClient(conf)
    new_topic = NewTopic(topic=topic_name,
                         num_partitions=num_partitions,
                         replication_factor=replication_factor)
    fs = admin_client.create_topics([new_topic])
    for topic, future in fs.items():
        try:
            future.result()
            print(f"Topic '{topic}' created successfully.")
        except Exception as e:
            print(f"Failed to create topic '{topic}': {e}")

def create_topics():
    for table_name in table_array:
        topic = f"kafka-{table_name}"
        create_topic(SERVER_URL, topic, 1, 1)

def delete_topic(bootstrap_servers, topic_name):
    conf = {'bootstrap.servers': bootstrap_servers}
    admin_client = AdminClient(conf)
    fs = admin_client.delete_topics([topic_name], operation_timeout=30)
    for topic, future in fs.items():
        try:
            # The result() call blocks until the topic is deleted or an error occurs.
            future.result()
            print(f"Topic '{topic}' deleted successfully.")
        except Exception as e:
            print(f"Failed to delete topic '{topic}': {e}")

def delete_topics():
    for table_name in table_array:
        topic = f"kafka-{table_name}"
        delete_topic(SERVER_URL, topic)


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def import_snapshot_data(bootstrap_servers, data_path):
    producer = Producer({'bootstrap.servers': bootstrap_servers})
    for table_name in table_array:
        topic = f"kafka-{table_name}"
        with open(f"{data_path}/{table_name}.ndjson") as f:
            for line in f:
                producer.produce(topic, line.encode('utf-8'), callback=delivery_report)
                producer.poll(0)
    producer.flush()

def import_incremental_data(bootstrap_servers, file_path, delay_time=1):
    producer = Producer({'bootstrap.servers': bootstrap_servers})
    with open(file_path) as f:
        for count, line in enumerate(f, start=1):
            try:
                if count % 100 == 0:
                    print(f"Imported {count} messages.")
                    time.sleep(delay_time)
                data = json.loads(line)
                topic = f"kafka-{data.get('label')}"
                # Send message asynchronously
                producer.produce(topic, line.encode('utf-8'), callback=delivery_report)
                # Serve delivery reports (if any)
                producer.poll(0)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON: {line}")

    # Wait for any outstanding messages to be delivered and delivery reports to be received.
    producer.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import snapshot data and incremental data.')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', action='store_true', help='Create topics.')
    group.add_argument('-d', action='store_true', help='Delete topics.')
    group.add_argument('-s', action='store_true', help='Import snapshot data.')
    group.add_argument('-i', action='store_true', help='Import incremental data.')
    args = parser.parse_args()
    
    if args.c:
        print("Creating topics...")
        create_topics()
        print("Finished creating topics.")
    
    if args.d:
        print("Deleting topics...")
        delete_topics()
        print("Finished deleting topics.")

    if args.s:
        print("Importing snapshot data...")
        import_snapshot_data(SERVER_URL, SNAPSHOT_DATA_PATH)
        print("Finished importing snapshot data.")
        
    if args.i:
        print("Importing incremental data...")
        import_incremental_data(SERVER_URL, INCREMENTAL_DATA_PATH)
        print("Finished importing incremental data.")
