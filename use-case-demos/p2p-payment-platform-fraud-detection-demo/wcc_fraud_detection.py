from neo4j import GraphDatabase

# Initialize connection to the PuppyGraph.
uri = "bolt://localhost:7687"
username = "puppygraph"
password = "puppygraph123"

# Step 1: Setup driver and session
try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    session = driver.session()

    # Step 2: Query all confirmed fraudulent users.
    query_confirmed_frauds = """
    MATCH (u:User)
    WHERE u.fraudMoneyTransfer = 1
    RETURN ID(u) as confirmed_fraud_user_id
    """
    confirmed_fraud_result = session.run(query_confirmed_frauds)

    # Store confirmed fraudulent users in a set for faster lookup.
    confirmed_fraud_users = {record['confirmed_fraud_user_id'] for record in confirmed_fraud_result}
    # Print the confirmed fraudulent users.
    print(f"Confirmed fraudulent users: {confirmed_fraud_users}")

    # Step 3: Get all components (groups) using WCC.
    query_wcc = """
    CALL algo.wcc({
        labels: ['User'],
        relationshipTypes: ['PatternAssociation']
    }) 
    YIELD id, componentId 
    RETURN componentId, collect(id) as ids 
    ORDER BY size(ids) DESC
    """
    wcc_result = session.run(query_wcc)

    # Step 4: Iterate over each group and check for confirmed fraudulent users.
    for record in wcc_result:
        component_id = record['componentId']
        user_ids = record['ids']  # List of user IDs in this group

        # Step 5: Find confirmed fraudulent users in this group.
        fraud_users = [user_id for user_id in user_ids if user_id in confirmed_fraud_users]

        if fraud_users and len(user_ids) > len(fraud_users):
            # Only mark other users as suspected if there are more users in the group than fraud users
            suspected_users = [user_id for user_id in user_ids if user_id not in fraud_users]
            print(f"Group {component_id} contains confirmed fraudulent users: {fraud_users}")
            print(f"Marking the following users as suspected frauds: {suspected_users}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Ensure the session is closed properly
    if session:
        session.close()
    if driver:
        driver.close()
