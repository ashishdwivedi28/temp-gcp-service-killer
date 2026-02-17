# Quick Setup Guide for Qwiklabs

## Current Configuration
- Project ID: `qwiklabs-gcp-03-3e9201f3ade6` (set in config.yaml)
- Budget per service: $0.01 USD (very low for testing)
- Simulated cost: $0.009 USD (90% of budget - will trigger WARNING alerts)

## Step-by-Step Deployment

### 1. Set Environment Variables (Already done in your session)
```bash
export SMTP_EMAIL="ashish.dwivedi@onixnet.us"
export SMTP_APP_PASSWORD="izwumpiumtfvmtly"
export ALERT_RECEIVER_EMAIL="ashishdwivedi9229@gmail.com"
```

### 2. Make Scripts Executable (Already done)
```bash
chmod +x scripts/*.sh
```

### 3. Deploy the Services
```bash
./scripts/deploy.sh
```

This will:
- Enable required GCP APIs
- Create service accounts (without billing.viewer role - fixed!)
- Create Pub/Sub topic for alerts
- Deploy cost monitoring service to Cloud Run
- Create secret for SMTP password (uses environment variable)
- Deploy notification service to Cloud Run
- Create Pub/Sub subscription
- Create Cloud Scheduler job (runs every 10 minutes)

### 4. Test the Notification Service

#### Option A: Trigger Cloud Scheduler Job
```bash
gcloud scheduler jobs run cost-monitoring-job --location=us-central1
```

#### Option B: Trigger via Cloud Console
1. Go to Cloud Console → Cloud Scheduler
2. Find `cost-monitoring-job`
3. Click "RUN NOW"

#### Option C: Call the Cost Monitoring Service Directly
```bash
# Get the service URL
COST_SERVICE_URL=$(gcloud run services describe cost-monitoring-service --region us-central1 --format 'value(status.url)')

# Trigger it
curl -X POST $COST_SERVICE_URL
```

### 5. Check Results

**Check Logs:**
```bash
# Cost monitoring service logs
gcloud run services logs read cost-monitoring-service --region us-central1 --limit=50

# Notification service logs
gcloud run services logs read notification-service --region us-central1 --limit=50
```

**Check Your Email:**
- You should receive an email at `ashishdwivedi9229@gmail.com`
- Subject: "GCP Budget Alert: [service-name]"
- Body will show: Current cost ($0.009), Budget ($0.01), Action: warning

### 6. Test Different Scenarios

Edit `/home/ashish/custom-gcp-kill-switch/src/cost_monitoring/main.py`, line ~52:

**For Warning Alert (80-99% of budget):**
```python
simulated_cost = 0.009
```

**For Service Disable Alert (>100% of budget):**
```python
simulated_cost = 0.011
```

After editing, redeploy:
```bash
gcloud run deploy cost-monitoring-service --source ./src/cost_monitoring --region us-central1
```

Then trigger the job again.

## Troubleshooting

### No email received?
1. Check Gmail App Password is correct
2. Check notification service logs for errors
3. Verify Pub/Sub subscription exists:
   ```bash
   gcloud pubsub subscriptions list
   ```

### Service deployment failed?
1. Check if all APIs are enabled
2. Verify service accounts exist:
   ```bash
   gcloud iam service-accounts list
   ```

### Want to clean up?
```bash
# Delete Cloud Run services
gcloud run services delete cost-monitoring-service --region us-central1 --quiet
gcloud run services delete notification-service --region us-central1 --quiet

# Delete Cloud Scheduler job
gcloud scheduler jobs delete cost-monitoring-job --location us-central1 --quiet

# Delete Pub/Sub resources
gcloud pubsub subscriptions delete cost-alerts-subscription --quiet
gcloud pubsub topics delete cost-alerts --quiet

# Delete service accounts
gcloud iam service-accounts delete deployment-sa@qwiklabs-gcp-03-3e9201f3ade6.iam.gserviceaccount.com --quiet
gcloud iam service-accounts delete runtime-sa@qwiklabs-gcp-03-3e9201f3ade6.iam.gserviceaccount.com --quiet
```

## What Changed?
1. ✅ Removed `roles/billing.viewer` from service accounts (not supported at project level)
2. ✅ Added automatic use of environment variables for SMTP credentials
3. ✅ Updated cost simulation to return $0.009 (triggers warning)
4. ✅ All files are in the same folder structure (already was)
