#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Variables
PROJECT_ID="$(gcloud config get-value project)"
REGION="us-central1"
COST_MONITORING_SERVICE_NAME="cost-monitoring-service"
NOTIFICATION_SERVICE_NAME="notification-service"
RUNTIME_SA_EMAIL="runtime-sa@$PROJECT_ID.iam.gserviceaccount.com"
PUB_SUB_TOPIC="cost-alerts"
SCHEDULER_JOB_NAME="cost-monitoring-job"

if [ -z "$PROJECT_ID" ]; then
    echo "gcloud project not set. Please run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi

# Enable APIs
./scripts/enable_apis.sh

# Create Service Accounts
./scripts/create_service_accounts.sh

# Create Pub/Sub topic
echo "Creating Pub/Sub topic..."
gcloud pubsub topics create $PUB_SUB_TOPIC || echo "Topic $PUB_SUB_TOPIC already exists."

# Deploy cost monitoring service
echo "Deploying cost monitoring service..."
gcloud run deploy $COST_MONITORING_SERVICE_NAME \
    --source ./src/cost_monitoring \
    --region $REGION \
    --service-account $RUNTIME_SA_EMAIL \
    --allow-unauthenticated

# Deploy notification service
echo "Deploying notification service..."
gcloud run deploy $NOTIFICATION_SERVICE_NAME \
    --source ./src/notification_service \
    --region $REGION \
    --service-account $RUNTIME_SA_EMAIL \
    --no-allow-unauthenticated \
    --set-env-vars="SENDGRID_API_KEY=YOUR_SENDGRID_API_KEY,NOTIFICATION_EMAIL=your-email@example.com"

# Create Pub/Sub subscription for the notification service
echo "Creating Pub/Sub subscription..."
NOTIFICATION_SERVICE_URL=$(gcloud run services describe $NOTIFICATION_SERVICE_NAME --region $REGION --format 'value(status.url)')
gcloud pubsub subscriptions create ${PUB_SUB_TOPIC}-subscription \
    --topic $PUB_SUB_TOPIC \
    --push-endpoint=$NOTIFICATION_SERVICE_URL \
    --push-auth-service-account=$RUNTIME_SA_EMAIL

# Create Cloud Scheduler job
echo "Creating Cloud Scheduler job..."
COST_MONITORING_SERVICE_URL=$(gcloud run services describe $COST_MONITORING_SERVICE_NAME --region $REGION --format 'value(status.url)')
gcloud scheduler jobs create http $SCHEDULER_JOB_NAME \
    --schedule="*/10 * * * *" \
    --uri=$COST_MONITORING_SERVICE_URL \
    --http-method=POST

echo "Deployment completed successfully."
