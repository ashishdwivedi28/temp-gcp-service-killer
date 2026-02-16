import os
import yaml
from flask import Flask, request
from google.cloud import billing_v1
from google.cloud import service_usage_v1
from google.cloud import pubsub_v1
from google.cloud import firestore
import json
from datetime import datetime, date

app = Flask(__name__)

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

PROJECT_ID = config['gcp_project_id']

@app.route('/', methods=['POST'])
def monitor_costs():
    """The main function triggered by Cloud Scheduler."""
    billing_client = billing_v1.CloudBillingClient()
    usage_client = service_usage_v1.ServiceUsageClient()
    publisher = pubsub_v1.PublisherClient()
    db = firestore.Client()

    # Get current billing period
    today = date.today()
    start_of_month = date(today.year, today.month, 1)

    # Iterate through budgeted services
    for budget in config['budgets']:
        service_name = budget['service']
        budget_limit = budget['limit']

        # Get cost for the service
        cost = get_service_cost(billing_client, service_name, start_of_month, today)

        # Check against budget
        if cost >= budget_limit:
            handle_budget_exceeded(usage_client, publisher, db, service_name, cost, budget_limit)
        elif cost >= budget_limit * 0.8:
            handle_budget_warning(publisher, service_name, cost, budget_limit)
    
    return "OK", 200

def get_service_cost(client, service, start_date, end_date):
    # This is a simplified cost retrieval. 
    # A real implementation would need more sophisticated logic to map SKUs to services.
    # For now, we'll simulate this with a placeholder.
    # In a real scenario, you would query the detailed billing export in BigQuery.
    print(f"Getting cost for {service} from {start_date} to {end_date}")
    return 0.0 # Placeholder

def handle_budget_exceeded(usage_client, publisher, db, service_name, cost, budget_limit):
    print(f"Budget exceeded for {service_name}. Cost: {cost}, Budget: {budget_limit}")
    
    # Disable the service
    disable_service(usage_client, service_name)

    # Send notification
    message = {
        "service_name": service_name,
        "current_cost": cost,
        "budget_limit": budget_limit,
        "action_taken": "disabled",
        "timestamp": datetime.now().isoformat()
    }
    publish_message(publisher, json.dumps(message))

    # Update state in Firestore
    doc_ref = db.collection('service_states').document(service_name)
    doc_ref.set({
        'disabled': True,
        'disabled_at': datetime.now()
    })

def handle_budget_warning(publisher, service_name, cost, budget_limit):
    print(f"Budget warning for {service_name}. Cost: {cost}, Budget: {budget_limit}")
    message = {
        "service_name": service_name,
        "current_cost": cost,
        "budget_limit": budget_limit,
        "action_taken": "warning",
        "timestamp": datetime.now().isoformat()
    }
    publish_message(publisher, json.dumps(message))

def disable_service(client, service_name):
    print(f"Disabling service: {service_name}")
    # The parent is the project resource name.
    parent = f"projects/{PROJECT_ID}"
    request = service_usage_v1.DisableServiceRequest(
        name=f"{parent}/services/{service_name}",
    )
    try:
        operation = client.disable_service(request=request)
        print(f"Service {service_name} disabling operation: {operation.name}")
    except Exception as e:
        print(f"Error disabling service {service_name}: {e}")

def publish_message(publisher, message):
    topic_path = publisher.topic_path(PROJECT_ID, 'cost-alerts')
    future = publisher.publish(topic_path, message.encode('utf-8'))
    print(f"Published message ID: {future.result()}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
