# Deployment Guide

This guide provides all the steps necessary to deploy and test the GCP Cost Control Kill Switch.

## Prerequisites

1.  A Google Cloud Platform project.
2.  The `gcloud` command-line tool installed and authenticated (`gcloud auth login`).
3.  A Google account with a Gmail App Password for sending email notifications.
4.  Your GCP project ID configured in `gcloud` (`gcloud config set project YOUR_PROJECT_ID`).

## Required APIs

The deployment script will automatically enable the following APIs:

*   Cloud Run API
*   Cloud Scheduler API
*   Cloud Billing API
*   Cloud Monitoring API
*   Pub/Sub API
*   IAM API
*   Service Usage API
*   Firestore API
*   Cloud Build API
*   Secret Manager API

## IAM Setup

The deployment script will create two service accounts with the necessary roles:

*   **`deployment-sa`:** Used for deploying the application.
*   **`runtime-sa`:** Used by the Cloud Run services to access other GCP services.

## Deployment Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/custom-gcp-kill-switch.git
    cd custom-gcp-kill-switch
    ```

2.  **Configure the budget:**
    *   Copy the example config file: `cp config.yaml.example config.yaml`
    *   Edit `config.yaml` and set your `gcp_project_id` and `notification_email`.
    *   Adjust the budget limits for each service as needed.

3.  **Set environment variables for deployment script:**
    The `deploy.sh` script requires your Gmail credentials. You can set them as environment variables:
    ```bash
    export SMTP_EMAIL="your-email@gmail.com"
    export SMTP_APP_PASSWORD="YOUR_GMAIL_APP_PASSWORD"
    export ALERT_RECEIVER_EMAIL="your-email@example.com"
    ```
    Then update the `deploy.sh` script to use these variables in the `gcloud run deploy` command for the notification service.

4.  **Run the deployment script:**
    ```bash
    chmod +x scripts/*.sh
    ./scripts/deploy.sh
    ```

    This script will:
    *   Enable all required APIs.
    *   Create the necessary service accounts.
    *   Create the Pub/Sub topic.
    *   Deploy the `cost-monitoring-service` and `notification-service` to Cloud Run.
    *   Create a Pub/Sub subscription to trigger the notification service.
    *   Create a Cloud Scheduler job to trigger the cost monitoring service every 10 minutes.

## Testing Steps

1.  **Trigger the cost monitoring service manually:**
    *   Go to the Cloud Scheduler page in the GCP Console.
    *   Find the `cost-monitoring-job` and click "Run now".
    *   Check the logs for the `cost-monitoring-service` in the Cloud Run console to see the output.

2.  **Simulate a budget warning:**
    *   In `src/cost_monitoring/main.py`, temporarily modify the `get_service_cost` function to return a value that is > 80% of a service's budget.
    *   Redeploy the service: `gcloud run deploy cost-monitoring-service --source ./src/cost_monitoring --region us-central1`
    *   Trigger the job manually again.
    *   You should receive a warning email.

3.  **Simulate a budget overrun and service disabling:**
    *   Modify `get_service_cost` to return a value that exceeds the budget.
    *   Redeploy and trigger the job.
    *   You should receive a "service disabled" email.
    *   Verify that the service is disabled by going to the "APIs & Services" -> "Enabled APIs & services" page in the GCP Console and checking the status of the service you configured.

## Production Deployment

For a production environment, consider the following:

*   **Cost Calculation:** Implement the BigQuery-based cost calculation for accurate cost data.
*   **Security:** Store the `SMTP_APP_PASSWORD` in Secret Manager instead of passing it as an environment variable.
*   **Reset Mechanism:** The current version lacks an automated reset. You would need to add a script or another Cloud Scheduler job to re-enable services at the start of each billing cycle.

## Deployment in an Organization GCP Environment

When deploying in a corporate environment, you may face stricter IAM policies. Ensure the `deployment-sa` has sufficient permissions to create projects, service accounts, and assign IAM roles. You might need to work with your organization's cloud administrators to get the necessary permissions.
