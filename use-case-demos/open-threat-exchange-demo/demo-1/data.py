import json
import psycopg2
import os
import argparse
from OTXv2 import OTXv2
from datetime import datetime
from typing import List, Dict, Any

API_KEY = "" # Add your OTX API key here


def insert_data(json_data: Dict[str, Any], conn) -> None:
    """Inserts JSON data into the PostgreSQL database."""

    cur = conn.cursor()

    # --- Pulse Table ---
    pulse_data = {
        'id': json_data['id'],
        'name': json_data['name'],
        'description': json_data.get('description'),  # Use .get() for optional fields
        'tlp': json_data.get('tlp'),
        'public': bool(json_data['public']),  # Ensure boolean conversion
        'adversary': json_data.get('adversary'),
        'created': json_data.get('created'),
        'modified': json_data.get('modified'),
        'author_name': json_data.get('author_name'),
        'revision': json_data.get('revision')
    }
    # Handle the case if pulse already exists, update it
    cur.execute("""
        INSERT INTO pulse (id, name, description, tlp, public, adversary, created, modified, author_name, revision)
        VALUES (%(id)s, %(name)s, %(description)s, %(tlp)s, %(public)s, %(adversary)s, %(created)s, %(modified)s, %(author_name)s, %(revision)s)
        ON CONFLICT (id) DO UPDATE
        SET name = EXCLUDED.name,
            description = EXCLUDED.description,
            tlp = EXCLUDED.tlp,
            public = EXCLUDED.public,
            adversary = EXCLUDED.adversary,
            created = EXCLUDED.created,
            modified = EXCLUDED.modified,
            author_name = EXCLUDED.author_name,
            revision = EXCLUDED.revision;
    """, pulse_data)


    pulse_id = json_data['id']
    
    # --- Indicator Table ---
    for indicator_data in json_data.get('indicators', []):  # Default to empty list if 'indicators' is missing
        indicator_id = indicator_data['id']

        # Check and handle existing indicator
        cur.execute("SELECT id FROM indicator WHERE id = %s", (indicator_id, ))
        existing_indicator = cur.fetchone()

        if existing_indicator:
          cur.execute("""
              UPDATE indicator
              SET indicator = %s, type = %s, created = %s, expiration = %s, is_active = %s, role = %s
              WHERE id = %s
          """, (indicator_data['indicator'], indicator_data['type'], indicator_data.get('created'),
                indicator_data.get('expiration'), bool(indicator_data.get('is_active')), indicator_data.get('role'), indicator_id))
        else:
          cur.execute("""
              INSERT INTO indicator (id, indicator, type, created, expiration, is_active, role)
              VALUES (%s, %s, %s, %s, %s, %s, %s)
          """, (indicator_id, indicator_data['indicator'], indicator_data['type'],
                indicator_data.get('created'), indicator_data.get('expiration'),
                bool(indicator_data.get('is_active')), indicator_data.get('role')))

        # --- Pulse-Indicator Table ---
        cur.execute("""
            INSERT INTO pulse_indicator (pulse_id, indicator_id)
            VALUES (%s, %s)
            ON CONFLICT (pulse_id, indicator_id) DO NOTHING;
        """, (pulse_id, indicator_id))

    # --- Tag Table ---
    for tag_name in json_data.get('tags', []):
        cur.execute("INSERT INTO tag (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (tag_name,))
        tag_id = cur.fetchone()
        if tag_id:
          cur.execute("""
              INSERT INTO pulse_tag (pulse_id, tag_id)
              VALUES (%s, %s)
              ON CONFLICT (pulse_id, tag_id) DO NOTHING;
          """, (pulse_id, tag_id[0]))


    # --- Country Table ---
    for country_name in json_data.get('targeted_countries', []):
        cur.execute("INSERT INTO country (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (country_name,))
        country_id = cur.fetchone()
        if country_id:
             cur.execute("""
                 INSERT INTO pulse_country (pulse_id, country_id)
                 VALUES (%s, %s)
                 ON CONFLICT (pulse_id, country_id) DO NOTHING;
              """, (pulse_id, country_id[0]))

    # --- Malware Family Table ---
    for malware_name in json_data.get('malware_families', []):
        cur.execute("INSERT INTO malware (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (malware_name,))
        malware_id = cur.fetchone()
        if malware_id:
            cur.execute("""
                INSERT INTO pulse_malware (pulse_id, malware_id)
                VALUES (%s, %s)
                ON CONFLICT (pulse_id, malware_id) DO NOTHING;
            """, (pulse_id, malware_id[0]))

    # --- Attack ID Table ---
    for attack_id_str in json_data.get('attack_ids', []):
        cur.execute("INSERT INTO attack (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (attack_id_str,))
        # No RETURNING id needed, attack_id is the string itself

        cur.execute("""
            INSERT INTO pulse_attack (pulse_id, attack_id)
            VALUES (%s, %s)
            ON CONFLICT (pulse_id, attack_id) DO NOTHING;
        """, (pulse_id, attack_id_str))  # Use attack_id_str directly

    # --- Reference Table ---
    for reference_url in json_data.get('references', []):
        cur.execute("INSERT INTO reference (url) VALUES (%s) ON CONFLICT (url) DO NOTHING RETURNING id", (reference_url,))
        reference_id_result = cur.fetchone()
        if reference_id_result:
          reference_id = reference_id_result[0]
          cur.execute("""
              INSERT INTO pulse_reference (pulse_id, reference_id)
              VALUES (%s, %s)
              ON CONFLICT (pulse_id, reference_id) DO NOTHING;
          """, (pulse_id, reference_id))
    
    # --- Industry Table ---
    for industry_name in json_data.get('industries', []):
        cur.execute("INSERT INTO industry (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (industry_name,))
        industry_id = cur.fetchone()
        if industry_id:
          cur.execute("""
              INSERT INTO pulse_industry (pulse_id, industry_id)
              VALUES (%s, %s)
              ON CONFLICT (pulse_id, industry_id) DO NOTHING;
          """, (pulse_id, industry_id[0]))
    
    # --- Groups Table ---
    for group_id in json_data.get('groups', []):
        group_id = int(group_id)  # Attempt conversion
        cur.execute("INSERT INTO groups (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (group_id,))
        cur.execute("""
                INSERT INTO pulse_groups (pulse_id, group_id)
                VALUES (%s, %s)
                ON CONFLICT (pulse_id, group_id) DO NOTHING;
            """, (pulse_id, group_id))

    conn.commit()


def import_pulses(directory: str, db_params: Dict[str, str]) -> None:
    """Processes all JSON files in a directory and imports them into the database."""
    conn = None  # Initialize conn outside the try block
    try:
        conn = psycopg2.connect(**db_params)
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        insert_data(data, conn)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {filename}: {e}")
                    except psycopg2.Error as e:
                        print(f"Error inserting data from file {filename}: {e}")
                        conn.rollback()  # Rollback in case of database error


    except psycopg2.OperationalError as e:
        print(f"Unable to connect to the database: {e}")
    finally:
        if conn:
            conn.close()


def download_pulses(directory: str, number: int) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)

    otx = OTXv2(API_KEY)
    pulses = otx.getall_iter(max_items=number)

    for number, pulse in enumerate(pulses, 1):
        print(f"{number}: {pulse['name']}")
        filename = f"pulse-{pulse['id']}.json"
        with open(os.path.join(directory, filename), 'w') as f:
            f.write(json.dumps(pulse, indent=2))


def create_parser():
    parser = argparse.ArgumentParser(description="Download and import pulse data into PostgreSQL.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    download_parser = subparsers.add_parser("download", help="Download pulse data")
    download_parser.add_argument("-d", "--json_directory", default="./pulses", help="Path to the directory to save JSON files.")
    download_parser.add_argument("-n", "--number", type=int, default=100, help="Number of pulses to download.")

    import_parser = subparsers.add_parser("import", help="Import data to database")
    import_parser.add_argument("-d", "--json_directory", default="./pulses", help="Path to the directory containing JSON files.")
    import_parser.add_argument("-H", "--host", default="localhost", help="Database host (default: localhost)")
    import_parser.add_argument("-D", "--database", default="postgres", help="Database name (default: postgres)")
    import_parser.add_argument("-u", "--user", default="postgres", help="Database user (default: postgres)")
    import_parser.add_argument("-p", "--password", default="postgres123", help="Database password (default: postgres123)")
    import_parser.add_argument("-P", "--port", type=int, default=5432, help="Database port (default: 5432)")

    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    if args.command == "download":
        download_pulses(args.json_directory, args.number)
    elif args.command == "import":
        db_params = {
            'host': args.host,
            'database': args.database,
            'user': args.user,
            'password': args.password,
            'port': args.port,
        }
        import_pulses(args.json_directory, db_params)
