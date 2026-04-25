# KrishiMind SustainAI - Deployment Guide

This document provides step-by-step instructions for deploying the KrishiMind SustainAI system to production environments.

## Architecture Overview

KrishiMind is a **monorepo** with two main components:
- **Frontend**: Next.js application (deployed to Vercel)
- **Backend**: FastAPI Python API (deployed to Render.com)

Both components must be deployed and properly connected via the `BACKEND_URL` environment variable.

---

## Local Development Setup

### Prerequisites
- Node.js 18+ and npm (for frontend)
- Python 3.11+ (for backend)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/nikitasachan2004/KrishiMind_SustainAi.git
cd KrishiMind_SustainAi
```

### 2. Setup Backend (FastAPI)
```bash
# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server (runs on http://localhost:8000)
uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Setup Frontend (Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Create development environment file
cp .env.example .env.local
# Edit .env.local if needed (defaults to http://127.0.0.1:8000)

# Start development server (runs on http://localhost:3000)
npm run dev
```

### 4. Test the Integration
- Open http://localhost:3000 in your browser
- Navigate to `/analyze` page
- Submit a form to test the backend connection
- Check browser console for any errors
- Verify `/health` endpoint: http://localhost:8000/health

---

## Production Deployment

### Frontend Deployment (Vercel)

#### Option A: Deploy via GitHub
1. **Push to GitHub** - Your repository is already configured
2. **Connect to Vercel**:
   - Go to https://vercel.com/dashboard
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Select `KrishiMind_SustainAi` project
3. **Configure Settings**:
   - Framework: Next.js (auto-detected)
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next` (auto-detected)
4. **Set Environment Variables** in Vercel:
   - Add `BACKEND_URL` = `https://your-render-api-url.onrender.com`
   - Deploy

#### Option B: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd frontend
vercel --prod
```

#### Verify Deployment
- Visit your Vercel project URL
- Test the `/analyze` page with the backend
- Check Network tab in DevTools for `/api/predict` calls

---

### Backend Deployment (Render.com)

#### Configuration Details
The `render.yaml` file is already configured for automatic deployment:
```yaml
services:
  - type: web
    name: krishimind-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn cloud.api.app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### Step-by-Step Deployment

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```

2. **Connect Repository to Render**:
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select `KrishiMind_SustainAi` repository
   - Choose "Python" runtime
   - Accept auto-detected settings from `render.yaml`

3. **Configure Environment Variables** (if not in render.yaml):
   - `PYTHON_VERSION` = `3.11.0`
   - Any AWS credentials if using S3/Lambda (optional)

4. **Deploy**:
   - Click "Create Web Service"
   - Render will auto-deploy on push to `main`

5. **Get Your API URL**:
   - After deployment, Render provides a URL like: `https://krishimind-api.onrender.com`
   - This URL will be your `BACKEND_URL` in the frontend

#### Common Render Issues

**"Python version unavailable"**:
- Try `3.12.0` instead of `3.11.0`
- Update `render.yaml` → `PYTHON_VERSION`

**"Timeout on startup"**:
- Render's free tier may have slow startup
- Use paid tier or paid tier for guaranteed uptime

**"API responds slowly after period of inactivity"**:
- Free tier services spin down after 15 minutes
- Upgrade to "Standard" tier (paid) for always-on

**"Models failed to load"**:
- Ensure `artifacts/` directory with model files is in git repository
- Check startup logs for specific errors: `logs` tab in Render dashboard

---

## Connecting Frontend to Backend

After deploying both services, update the frontend's `BACKEND_URL`:

### Via Vercel Dashboard
1. Go to your Vercel project
2. Settings → Environment Variables
3. Update `BACKEND_URL` to your Render URL: `https://krishimind-api.onrender.com`
4. Redeploy: Deployments → Redeploy with existing Build Cache

### Via Git + Auto-Deploy
1. Update `frontend/.env.production` locally:
   ```bash
   BACKEND_URL=https://your-render-api-url.onrender.com
   ```
2. Commit and push (Vercel auto-deploys)

---

## Verification Checklist

After deployment, verify:

- [ ] **Frontend loads**: Visit your Vercel URL
- [ ] **Health check**: `https://your-render-api-url.onrender.com/health` returns `{"status": "ok"}`
- [ ] **Predictions work**: Submit form on `/analyze` page
- [ ] **No CORS errors**: Check browser DevTools Console
- [ ] **API response**: Open Network tab, submit form, check `/api/predict` response

---

## Troubleshooting

### CORS Errors
**Symptom**: "Access to XMLHttpRequest blocked by CORS policy"

**Solution**:
- Backend already has CORS configured for any origin
- Verify `BACKEND_URL` environment variable is correct
- Check browser console for exact URL being called

### 502 Bad Gateway
**Symptom**: API returns 502 error

**Solution**:
- Check Render logs: https://dashboard.render.com/web/[service-id]/logs
- Verify models are loaded: Check startup log for "✅ API ready"
- Restart the service in Render dashboard

### Models Not Loading
**Symptom**: "Models failed to load" during startup

**Solution**:
- Ensure `artifacts/` folder is committed to git
- Verify files exist:
  ```bash
  ls -la artifacts/
  # Should show: price_features.json, yield_features.json
  ```
- Check Render build logs for import errors

### Environment Variables Not Working
**Symptom**: Backend uses localhost URL instead of production URL

**Solution - Frontend**:
- Verify in Vercel dashboard: Settings → Environment Variables
- Trigger redeploy after updating
- Wait for redeploy to complete before testing

**Solution - Backend**:
- Verify in Render dashboard: Settings → Environment
- Restart the service after updating

---

## Monitoring & Debugging

### View Logs

**Vercel**:
- Go to Deployments tab
- Click any deployment
- View Function Logs (realtime)

**Render**:
- Go to Web Service page
- Click "Logs" tab
- View service logs (realtime)

### Performance Monitoring

- **Vercel Analytics**: Included, view in Vercel dashboard
- **API Performance**: Check response times in browser DevTools
- **Backend Health**: Periodically call `/health` endpoint

---

## CI/CD Pipeline

The repository is configured for automatic deployment:

1. **Push to main** → GitHub
2. **Vercel** automatically deploys frontend changes
3. **Render** automatically deploys backend changes (if render.yaml present)

No manual steps needed after initial setup.

---

## Environment Variables Reference

### Frontend (Next.js)
Located in: `frontend/.env.local` (dev) and Vercel dashboard (production)

| Variable | Value | Required |
|----------|-------|----------|
| `BACKEND_URL` | `https://your-render-api-url.onrender.com` | ✅ Yes |

### Backend (FastAPI)
Located in: `render.yaml` or Render dashboard environment variables

| Variable | Value | Required |
|----------|-------|----------|
| `PYTHON_VERSION` | `3.11.0` or `3.12.0` | ✅ Yes |

### Optional (AWS Integration)
| Variable | Value | Required |
|----------|-------|----------|
| `AWS_REGION` | `ap-south-1` | ❌ No |
| `AWS_S3_BUCKET` | Bucket name | ❌ No |
| `AWS_ACCESS_KEY_ID` | Your key | ❌ No |
| `AWS_SECRET_ACCESS_KEY` | Your secret | ❌ No |

---

## Rollback Procedures

### Vercel
1. Go to Deployments tab
2. Find previous working deployment
3. Click menu (•••) → "Promote to Production"

### Render
1. Go to Web Service page
2. Click "Logs" tab → "Deploys" section
3. Find previous deploy → Click → "Redeploy"

---

## Support & Issues

For deployment issues:
1. Check relevant logs (Vercel / Render dashboards)
2. Verify environment variables are set correctly
3. Ensure git repository has all necessary files (especially `artifacts/`)
4. Try restarting the service

---

**Last Updated**: 2025-04-25
**Version**: KrishiMind SustainAI v1.0.0
