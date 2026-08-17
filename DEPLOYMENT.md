# Deployment Guide for CivicPulse Complaint Management System

This guide explains how to deploy the Complaint Management System to **Render**, **Railway**, or using **Docker**.

---

## Option 1: Deploy on Render (Recommended Free Hosting)

1. Push your project repository to GitHub:
   ```bash
   git add .
   git commit -m "Add cloud deployment configuration"
   git push origin main
   ```

2. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Render will auto-detect the configuration from `render.yaml` or you can manually enter:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**. Render will build and deploy your app with a free HTTPS URL!

---

## Option 2: Deploy on Railway

1. Go to [Railway.app](https://railway.app/).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your repository.
4. Railway auto-detects `Procfile` and `requirements.txt` and deploys automatically.
5. In your project settings, click **Generate Domain** to get your public URL.

---

## Option 3: Deploy with Docker

### Local Container Run
```bash
docker compose up --build -d
```
Access the application at `http://localhost:8000`.

### Manual Docker Build & Push
```bash
# Build image
docker build -t your-dockerhub-username/complaint-system:latest .

# Push to Docker Hub
docker push your-dockerhub-username/complaint-system:latest
```

---

## Health Check Endpoint
Verify your deployment live by accessing `/api/health`:
`https://<your-app-domain>/api/health`
`https://<your-app-domain>/` (Web Interface)
