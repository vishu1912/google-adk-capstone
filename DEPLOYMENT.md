# Deployment Guide 🚀

This guide shows how to deploy the Health Journal Agent to Google Cloud using Cloud Run and Agent Engine.

## Table of Contents
- [Quick Deploy (Cloud Run)](#quick-deploy-cloud-run)
- [Agent Engine Deployment](#agent-engine-deployment)
- [Environment Variables](#environment-variables)
- [Monitoring & Logs](#monitoring--logs)

---

## Quick Deploy (Cloud Run)

### Prerequisites
- Google Cloud account with billing enabled
- `gcloud` CLI installed and authenticated
- Docker installed locally

### Step 1: Prepare Deployment Files

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent.py .
COPY evaluation.py .

# Set environment variable for production
ENV PYTHONUNBUFFERED=1

# Run the agent server
CMD ["python", "-m", "google.adk.cli", "serve", "agent:root_agent", "--host", "0.0.0.0", "--port", "8080"]
```

Create `.dockerignore`:
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
.env
.git/
.gitignore
README.md
*.md
tests/
```

### Step 2: Build and Deploy

1. **Set your project ID:**
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
gcloud config set project $PROJECT_ID
```

2. **Enable required APIs:**
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

3. **Build the container:**
```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/health-journal-agent
```

4. **Deploy to Cloud Run:**
```bash
gcloud run deploy health-journal-agent \
  --image gcr.io/$PROJECT_ID/health-journal-agent \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300
```

5. **Get your deployment URL:**
```bash
gcloud run services describe health-journal-agent \
  --region $REGION \
  --format 'value(status.url)'
```

### Step 3: Test Deployment

```bash
curl -X POST https://your-service-url.run.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have a headache with severity 8"
  }'
```

---

## Agent Engine Deployment

Agent Engine provides managed hosting specifically designed for ADK agents.

### Step 1: Install Agent Engine CLI

```bash
pip install google-adk-agent-engine
```

### Step 2: Initialize Project

```bash
adk-engine init \
  --project $PROJECT_ID \
  --region $REGION
```

### Step 3: Deploy Agent

```bash
adk-engine deploy \
  --agent-file agent.py \
  --agent-name health_coordinator \
  --display-name "Health Journal Agent" \
  --description "AI assistant for health tracking"
```

### Step 4: Get Endpoint

```bash
adk-engine list --project $PROJECT_ID
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key | `AIza...` |
| `PORT` | Server port (Cloud Run uses 8080) | `8080` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `MAX_SESSIONS` | Max concurrent sessions | `100` |
| `SESSION_TTL` | Session timeout (seconds) | `3600` |

### Setting Variables in Cloud Run

```bash
gcloud run services update health-journal-agent \
  --region $REGION \
  --set-env-vars LOG_LEVEL=DEBUG,MAX_SESSIONS=200
```

---

## Monitoring & Logs

### View Logs

```bash
# Stream logs in real-time
gcloud run services logs tail health-journal-agent --region $REGION

# View logs in Cloud Console
gcloud run services logs read health-journal-agent \
  --region $REGION \
  --limit 50
```

### Set Up Alerts

1. Go to Cloud Console → Monitoring
2. Create alert policy for:
   - High error rate (>5% of requests)
   - High latency (>2 seconds)
   - High memory usage (>80%)

### Metrics to Monitor

- **Request count:** Successful agent interactions
- **Error rate:** Failed requests/total requests
- **Latency:** Response time per request
- **Memory usage:** RAM consumption
- **Token usage:** Gemini API tokens consumed

---

## Scaling Configuration

### Auto-scaling Settings

```bash
gcloud run services update health-journal-agent \
  --region $REGION \
  --min-instances 1 \
  --max-instances 10 \
  --concurrency 80
```

### Performance Tuning

For high traffic:
```bash
gcloud run services update health-journal-agent \
  --region $REGION \
  --memory 2Gi \
  --cpu 2 \
  --concurrency 100
```

For cost optimization:
```bash
gcloud run services update health-journal-agent \
  --region $REGION \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3
```

---

## Security Best Practices

### 1. API Key Management

**Never commit API keys!** Use Secret Manager:

```bash
# Store secret
echo -n "your-api-key" | gcloud secrets create gemini-api-key --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run to use secret
gcloud run services update health-journal-agent \
  --region $REGION \
  --update-secrets GOOGLE_API_KEY=gemini-api-key:latest
```

### 2. Authentication

Enable Cloud Run authentication:
```bash
gcloud run services update health-journal-agent \
  --region $REGION \
  --no-allow-unauthenticated
```

### 3. Rate Limiting

Implement rate limiting in your agent code or use Cloud Armor.

---

## Cost Estimation

### Cloud Run Pricing (approximate)

- **Request cost:** $0.40 per million requests
- **CPU cost:** $0.00002400 per vCPU-second
- **Memory cost:** $0.00000250 per GiB-second
- **Gemini API:** Varies by model and tokens

### Example Monthly Cost

For 10,000 requests/month:
- Cloud Run: ~$5
- Gemini API: ~$10-30 (depends on usage)
- **Total: ~$15-35/month**

---

## Troubleshooting

### Common Issues

**Issue: Container exits immediately**
```bash
# Check logs
gcloud run services logs read health-journal-agent --limit 100

# Verify Dockerfile CMD is correct
```

**Issue: 503 Service Unavailable**
```bash
# Increase timeout
gcloud run services update health-journal-agent \
  --timeout 600

# Check memory limits
gcloud run services update health-journal-agent \
  --memory 2Gi
```

**Issue: High latency**
```bash
# Enable request/response compression
# Increase CPU allocation
# Consider caching frequently accessed data
```

---

## Rollback Procedure

If deployment fails:

```bash
# List revisions
gcloud run revisions list --service health-journal-agent --region $REGION

# Rollback to previous revision
gcloud run services update-traffic health-journal-agent \
  --region $REGION \
  --to-revisions REVISION_NAME=100
```

---

## Next Steps

After successful deployment:

1. ✅ Set up monitoring and alerts
2. ✅ Configure custom domain (optional)
3. ✅ Implement authentication
4. ✅ Enable Cloud CDN for static assets
5. ✅ Set up CI/CD pipeline

---

## Support

For deployment issues:
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [ADK Documentation](https://github.com/google/agentic-development-kit)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-run)

---

**Deployment completed! 🎉**

Your Health Journal Agent is now live and ready to help users track their health.