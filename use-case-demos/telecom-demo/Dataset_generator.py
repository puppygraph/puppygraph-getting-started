import pandas as pd
import numpy as np
import random
import itertools
from collections import defaultdict
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Define constants
NUM_CUSTOMERS = 1002
NUM_PLANS = 5
NUM_DEVICES = 10
NUM_ISOLATED_CUSTOMERS = int(NUM_CUSTOMERS * 0.01)  # 1% isolated customers

end_date = datetime.now()

device_types = ["iPhone", "Android", "Tablet"]
os_versions = ["v1", "v2", "v3", "v4"]

# All possible combinations
combinations = list(itertools.product(device_types, os_versions))

# Create DataFrame
devices = pd.DataFrame(combinations, columns=["device_type", "os_version"])

# Add a unique device_id column (e.g., DEV_0, DEV_1, ...)
devices['device_id'] = [f"DEV_{i}" for i in range(len(devices))]

devices = devices[['device_id', 'device_type', 'os_version']]


locations = pd.DataFrame({
    "city": ["NY", "LA", "SF", "CHI", "HOU"]
})
locations["location_id"] = [f"LOC_{i}" for i in range(5)]
locations = locations[['location_id', 'city']]

# Generate customer data
customers = pd.DataFrame({
    "customer_id": [f"CUST_{i}" for i in range(NUM_CUSTOMERS)],
    "age": np.random.randint(18, 75, NUM_CUSTOMERS),
    "tenure_months": np.random.randint(1, 60, NUM_CUSTOMERS),
    "phone_number": [f"+1{random.randint(1000000000, 9999999997)}" for _ in range(NUM_CUSTOMERS)],
    "churned": np.random.choice([0, 1], NUM_CUSTOMERS, p=[0.85, 0.15])
})



customer_devices = pd.DataFrame({
    "customer_id": customers["customer_id"],
    "device_id": np.random.choice(devices["device_id"], NUM_CUSTOMERS)
})

def generate_support_interactions(customers, num_interactions=500):
    support_data = []

    channels = ['call', 'chat', 'email', 'app']
    issue_types = ['billing', 'network', 'device', 'plan inquiry', 'upgrade', 'cancellation']
    satisfaction_scores = [1, 2, 3, 4, 5, None]  # some customers skip rating

    for i in range(num_interactions):
        cust_id = random.choice(customers["customer_id"].values)
        ticket_id = f"SUPP_{i}"
        interaction_time = end_date - timedelta(days=random.random() * 90)
        channel = random.choices(channels, weights=[0.4, 0.3, 0.2, 0.1], k = 1)[0]
        issue = random.choice(issue_types)
        resolution_time = int(random.gauss(mu=30, sigma=15))  # in minutes
        resolution_time = max(5, min(120, resolution_time))  # clamp to 5-120 mins
        escalated = random.random() < 0.1 if issue != 'cancellation' else True
        satisfaction = random.choices(satisfaction_scores, weights=[0.04, 0.06, 0.1, 0.15, 0.15, 0.5], k=1)[0]

        support_data.append({
            "ticket_id": ticket_id,
            "customer_id": cust_id,
            "interaction_time": interaction_time,
            "channel": channel,
            "issue_type": issue,
            "resolution_time_min": resolution_time,
            "escalated": escalated,
            "satisfaction_score": satisfaction
        })

    return pd.DataFrame(support_data)

friend_edges = defaultdict(set)
isolated_customers = set(np.random.choice(customers["customer_id"], NUM_ISOLATED_CUSTOMERS, replace=False))
non_isolated_customers = set(customers["customer_id"]) - isolated_customers
calls = []
customer_id_to_phone = dict(zip(customers["customer_id"], customers["phone_number"]))
for i in range(5000):  # 5,000 random call interactions
    # Ensure that isolated customers are not chosen as source unless they have no friends
    src = random.choice(customers["customer_id"].values)
    if src not in isolated_customers:
        # If the source is isolated, choose a random target from all customers
        tgt = random.choice(list(set(customers["customer_id"]) - {src} - isolated_customers))
    time = end_date - timedelta(days=random.random() * 90)
    calls.append((customer_id_to_phone[src], customer_id_to_phone[tgt], int(random.randint(1, 10000)*(random.random()/2)**2+1), time))  # Random call duration between 1 and 10000 seconds
customer_calls = pd.DataFrame(calls, columns=["source_customer", "target_customer", "call_duration", "call_time"])

new_calls = []
for isolated_cust in isolated_customers:
    # Add isolated customers with no friends
    if (random.random() < 0.2):
        pass
    else:
        for i in range (random.randint(50, 100)):
            tgt = random.choice(list(customers["customer_id"]))
            if tgt != isolated_cust:
                new_calls.append({
                    "source_customer": customer_id_to_phone[isolated_cust],
                    "target_customer": customer_id_to_phone[tgt],
                    "call_duration": random.randint(1,30),
                    "call_time": end_date - timedelta(days=random.random() * 90)
                })
new_calls_df = pd.DataFrame(new_calls)

customer_calls = pd.concat([customer_calls, new_calls_df], ignore_index=True)
NUM_CIRCLES = 30
CIRCLE_SIZE = random.randint(2, 15)  # Random circle size between 2 and 15

used_customers = set()
call_circles = []
churn_lookup = dict(zip(customers["customer_id"], customers["churned"]))

customer_locations_dict = {}
for i in range(NUM_CIRCLES):
    eligible = list(set(customers["customer_id"]) - isolated_customers - used_customers)
    circle = random.sample(eligible, CIRCLE_SIZE)
    used_customers.update(circle)
    churn = False
    location = random.choice(locations["city"].values)
    for person in circle:
        churn = churn or churn_lookup[person] == 1
        customer_locations_dict[person] = location
        for friend in circle:
            if person != friend:
                for _ in range(random.randint(3, 10)):  # Each pair can have 6 to 20 calls (double counting)
                    call_circles.append({
                        "source_customer": customer_id_to_phone[person],
                        "target_customer": customer_id_to_phone[friend],
                        "call_duration": int(random.randint(1, 10000)*(random.random()/2)**2+1),
                        "call_time": end_date - timedelta(days=random.random() * 90)
                    })
    CIRCLE_SIZE = random.randint(2, 15)  # Random circle size between 2 and 15
    if churn:
        for person in circle:
            if random.random() < 0.3:
                customers.loc[customers["customer_id"] == person, "churned"] = 1


family_plan_data = []
family_plan_groups = []
customer_to_family_plan = {}
available_customers = set(customers["customer_id"])
num_family_plans = 50  # Number of family plan groups
for i in range(num_family_plans):
    family_size = random.randint(2, 6)  # Family plan size between 3 and 6
    family_members = random.sample(list(available_customers), family_size)
    available_customers -= set(family_members)
    family_plan_id = f"FAM_PLAN_{i}"
    plan_selection = f"PLAN_{random.randint(1, 10)}"  # Randomly select a plan for the family
    family_plan_groups.append(family_members)
    shared_location = random.choice(locations["city"].values)
    family_plan_data.append({
            "primary_id": random.choice(family_members),
            "plan_id": plan_selection,
            "family_plan_id": family_plan_id,
            "members": family_members,
            "shared_location": shared_location,
        })
    if random.random() < 0.1:
        pass
    for member in family_members:
        customer_locations_dict[member] = shared_location
        customer_to_family_plan[member] = family_plan_id
        customers.loc[customers["customer_id"] == member, "churned"] = 0
        for other_fam in family_members:
            if member != other_fam:
                for _ in range(random.randint(1, 15)):  # Each pair can have 6 to 20 calls (double counting)
                    call_circles.append({
                        "source_customer": customer_id_to_phone[member],
                        "target_customer": customer_id_to_phone[other_fam],
                        "call_duration": int(random.randint(1, 10000)*(random.random()/2)**2+1),
                        "call_time": end_date - timedelta(days=random.random() * 90)
                    })

# Create DataFrame for family plans
family_plans = pd.DataFrame(family_plan_data)
new_customers = pd.DataFrame({
    "customer_id": ["CUST_1001", "CUST_1002"],
    "age": [29, 45],
    "tenure_months": [10, 24],
    "phone_number": ["+19999999999", "+19999999998"],
    "churned": [0, 1]
})

# Append the two new customers to the DataFrame
customers = pd.concat([customers, new_customers], ignore_index=True)

new_family_plans = pd.DataFrame({
    "primary_id": "CUST_1001",
    "plan_id": "PLAN_1",
    "family_plan_id": "FAM_PLAN_51",
    "members": ["CUST_1001", "CUST_1002"],
    "shared_location": "NY"
})
family_plans = pd.concat([family_plans, new_family_plans], ignore_index=True)

family_plans = family_plans.explode('members').reset_index(drop=True)
new_calls_df = pd.DataFrame(call_circles)
customer_calls = pd.concat([customer_calls, new_calls_df], ignore_index=True)



# Add family_plan_id column to customers dataframe
customers["family_plan_id"] = customers["customer_id"].map(customer_to_family_plan)

for cust_id in customers["customer_id"]:
    if cust_id not in customer_locations_dict:
        customer_locations_dict[cust_id] = random.choice(locations["city"].values)

customer_locations = pd.DataFrame({
    "customer_id": list(customer_locations_dict.keys()),
    "location_id": list(customer_locations_dict.values())
})

customer_support = generate_support_interactions(customers, num_interactions=500)

# Show sample of each DataFrame
print("Customers:\n", customers.head(5), "\n")
customer_calls = customer_calls.sort_values(by='source_customer')

print("Customer Calls:\n", customer_calls.head(5), "\n")
print("Family Plans:\n", family_plans.head(5), "\n")
print("Customer Support Interactions:\n", customer_support.head(5), "\n")



from db_utils import connect_db, save_all_tables

# Prepare dictionary of DataFrames to save
all_data = {
    "customers": customers,
    # "devices": devices,
    # "locations": locations,
    "customer_calls": customer_calls,
    "family_plans": family_plans,
    "customer_support": customer_support,
    "customer_devices": customer_devices,
    "customer_locations": customer_locations,
}

# Save to DuckDB
con = connect_db("duckdb/my_project.duckdb")
save_all_tables(con, all_data)


