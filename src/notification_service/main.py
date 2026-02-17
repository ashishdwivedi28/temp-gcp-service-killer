import os
import base64
import json
from flask import Flask, request
from email_service import send_email

app = Flask(__name__)

ALERT_RECEIVER_EMAIL = os.environ.get('ALERT_RECEIVER_EMAIL')

@app.route('/', methods=['POST'])
def receive_notification():
    """Receives Pub/Sub messages and sends an email."""
    if not request.json or 'message' not in request.json:
        return "Invalid request", 400

    message_data = base64.b64decode(request.json['message']['data']).decode('utf-8')
    data = json.loads(message_data)

    service_name = data.get('service_name', 'N/A')
    current_cost = data.get('current_cost', 0)
    budget_limit = data.get('budget_limit', 0)
    action_taken = data.get('action_taken', 'N/A')
    timestamp = data.get('timestamp', 'N/A')

    subject = f"GCP Budget Alert: {service_name}"
    body = f"""
    <p>A budget alert has been triggered for your GCP project.</p>
    <ul>
        <li><strong>Service:</strong> {service_name}</li>
        <li><strong>Current Cost:</strong> ${current_cost:.2f}</li>
        <li><strong>Budget Limit:</strong> ${budget_limit:.2f}</li>
        <li><strong>Action Taken:</strong> {action_taken}</li>
        <li><strong>Timestamp:</strong> {timestamp}</li>
    </ul>
    """

    send_email(subject, body, ALERT_RECEIVER_EMAIL)

    return "OK", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
