# System Architecture

## Project Purpose

This project provides a robust and automated system to monitor and control spending on specific Google Cloud Platform (GCP) services. It prevents budget overruns by automatically disabling services when their costs exceed predefined limits.

## Architecture Diagram

```
+-----------------------+      HTTP POST      +---------------------------+
|   Cloud Scheduler     | ----------------> |  Cost Monitoring Service  |
| (Every 10 minutes)    |                   |       (Cloud Run)         |
+-----------------------+                     +---------------------------+
                                                         |
                                                         | 1. Get cost (Billing API)
                                                         | 2. Compare to budget
                                                         | 3. Disable service if needed (Service Usage API)
                                                         | 4. Store state (Firestore)
                                                         | 5. Publish notification (Pub/Sub)
                                                         |
         +------------------------------------------------+-------------------------------------------------+
         |
         v
+-----------------------+
|      Pub/Sub          |
|  (cost-alerts topic)  |
+-----------------------+
         |
         | (Push Subscription)
         v
+---------------------------+
|   Notification Service    |
|       (Cloud Run)         |
+---------------------------+
         |
         | 1. Receive message
         | 2. Send email (Gmail SMTP)
         v
+-----------------------+
|      User Email       |
+-----------------------+
```

## Component Interaction

1.  **Cloud Scheduler:** A cron job triggers the `cost-monitoring-service` every 10 minutes via an HTTP POST request.

2.  **Cost Monitoring Service (Cloud Run):** This is the core component.
    *   It receives the trigger from Cloud Scheduler.
    *   It retrieves cost data for configured services using the Cloud Billing API.
    *   It compares the current monthly cost against the predefined budget in `config.yaml`.
    *   If a budget threshold is met (80% or 100%), it takes action.
    *   **80% Threshold:** It publishes a "warning" message to the `cost-alerts` Pub/Sub topic.
    *   **100% Threshold:** It disables the specific service using the Service Usage API, updates the service state in Firestore to `disabled`, and publishes a "disabled" message to the `cost-alerts` Pub/Sub topic.

3.  **Pub/Sub:** A topic named `cost-alerts` decouples the monitoring service from the notification service.

4.  **Notification Service (Cloud Run):**
    *   A push subscription to the `cost-alerts` topic triggers this service whenever a new message is published.
    *   It parses the message to get details like service name, cost, and action taken.
    *   It formats and sends an email to the configured notification email address using the Gmail SMTP service.

5.  **Firestore:** A `service_states` collection is used to maintain the state of each monitored service (e.g., whether it is currently disabled). This prevents duplicate "disable" actions.

## Cost Calculation Logic

The current implementation uses a placeholder for cost calculation. A production-grade system would require setting up a detailed billing export to a BigQuery table. The `cost-monitoring-service` would then query this table to get fine-grained cost data per service SKU.

## Service Disable Logic

The system uses the `serviceusage.services.disable` method from the Service Usage API. This requires the `serviceusage.serviceUsageAdmin` IAM role for the runtime service account. Disabling a service prevents any further usage (and cost) for that service until it is manually re-enabled or the reset mechanism is triggered.

## Notification Flow

The notification flow is designed to be asynchronous and resilient. By using Pub/Sub, if the `notification-service` is temporarily down, messages will be retained and redelivered once the service is available again.

## Code Explanation for Beginners

*   **`src/cost_monitoring/main.py`:** A simple Flask web server. The `/` route is the entry point called by Cloud Scheduler. It iterates through the services in `config.yaml` and checks their cost.
*   **`src/notification_service/main.py`:** Another Flask server. The `/` route is a webhook that receives messages from Pub/Sub. It decodes the message and sends an email.
*   **`scripts/deploy.sh`:** This script automates the entire deployment process, including setting up APIs, service accounts, and deploying the Cloud Run services.
