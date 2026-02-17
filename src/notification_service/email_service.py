import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.cloud import secretmanager

def get_smtp_app_password():
    """Fetches the SMTP app password from Secret Manager or environment variables."""
    project_id = os.environ.get("GCP_PROJECT")
    secret_name = "SMTP_APP_PASSWORD"

    if project_id:
        try:
            client = secretmanager.SecretManagerServiceClient()
            secret_version_name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": secret_version_name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Could not fetch secret from Secret Manager: {e}. Falling back to environment variable.")

    return os.environ.get('SMTP_APP_PASSWORD')

def send_email(subject, message, recipient):
    """Sends an email using Gmail SMTP."""

    smtp_email = os.environ.get('SMTP_EMAIL')
    smtp_app_password = get_smtp_app_password()

    if not smtp_email or not smtp_app_password:
        print("SMTP credentials not found.")
        return

    msg = MIMEMultipart()
    msg['From'] = smtp_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(smtp_email, smtp_app_password)
            server.sendmail(smtp_email, recipient, msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
