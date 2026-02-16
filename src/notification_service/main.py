import os
import base64
import json
from flask import Flask, request
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL')

@app.route('/', methods=['POST'])
def receive_notification():
    """Receives Pub/Sub messages and sends an email."""
    if not request.json or 'message' not in request.json:
        return "Invalid request", 400

    message_data = base64.b64decode(request.json['message']['data']).decode('utf-8')
    data = json.loads(message_data)

    send_email(data)

    return "OK", 200

def send_email(data):
    """Sends an email using SendGrid."""
    service_name = data['service_name']
    current_cost = data['current_cost']
    budget_limit = data['budget_limit']
    action_taken = data['action_taken']
    timestamp = data['timestamp']

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

    message = Mail(
        from_email=NOTIFICATION_EMAIL,
        to_emails=NOTIFICATION_EMAIL,
        subject=subject,
        html_content=body)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent with status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
