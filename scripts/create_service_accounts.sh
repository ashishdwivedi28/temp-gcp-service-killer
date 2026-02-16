#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Variables
PROJECT_ID="$(gcloud config get-value project)"
DEPLOYMENT_SA_NAME="deployment-sa"
RUNTIME_SA_NAME="runtime-sa"

if [ -z "$PROJECT_ID" ]; then
    echo "gcloud project not set. Please run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi

# Create Deployment Service Account
echo "Creating Deployment Service Account..."
gcloud iam service-accounts create $DEPLOYMENT_SA_NAME \
    --display-name="Deployment Service Account"

DEPLOYMENT_SA_EMAIL="$DEPLOYMENT_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Grant roles to Deployment Service Account
echo "Granting roles to Deployment Service Account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DEPLOYMENT_SA_EMAIL" \
    --role="roles/run.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DEPLOYMENT_SA_EMAIL" \
    --role="roles/iam.serviceAccountAdmin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DEPLOYMENT_SA_EMAIL" \
    --role="roles/billing.viewer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DEPLOYMENT_SA_EMAIL" \
    --role="roles/resourcemanager.projectIamAdmin"

# Create Runtime Service Account
echo "Creating Runtime Service Account..."
gcloud iam service-accounts create $RUNTIME_SA_NAME \
    --display-name="Runtime Service Account"

RUNTIME_SA_EMAIL="$RUNTIME_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Grant roles to Runtime Service Account
echo "Granting roles to Runtime Service Account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$RUNTIME_SA_EMAIL" \
    --role="roles/monitoring.viewer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$RUNTIME_SA_EMAIL" \
    --role="roles/logging.logWriter"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$RUNTIME_SA_EMAIL" \
    --role="roles/run.invoker"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$RUNTIME_SA_EMAIL" \
    --role="roles/billing.viewer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$RUNTIME_SA_EMAIL" \
    --role="roles/serviceusage.serviceUsageAdmin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$RUNTIME_SA_EMAIL" \
    --role="roles/pubsub.publisher"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$RUNTIME_SA_EMAIL" \
    --role="roles/datastore.user" # For Firestore

echo "Service accounts created and configured successfully."
