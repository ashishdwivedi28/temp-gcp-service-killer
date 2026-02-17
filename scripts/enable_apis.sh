#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Variables
PROJECT_ID="$(gcloud config get-value project)"

if [ -z "$PROJECT_ID" ]; then
    echo "gcloud project not set. Please run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi

echo "Enabling APIs for project: $PROJECT_ID"

gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudbilling.googleapis.com \
  monitoring.googleapis.com \
  pubsub.googleapis.com \
  iam.googleapis.com \
  serviceusage.googleapis.com \
  firestore.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com

echo "APIs enabled successfully."
