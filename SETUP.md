# Local Development Setup Guide

This guide will help you set up KrishiMind SustainAI for local development.

## System Requirements

- **macOS/Linux/Windows**
- **Node.js**: 18+ (for frontend)
- **Python**: 3.11+ (for backend)
- **Git**: Latest version
- **npm**: Comes with Node.js
- **pip**: Comes with Python

## Step 1: Clone the Repository

```bash
git clone https://github.com/nikitasachan2004/KrishiMind_SustainAi.git
cd KrishiMind_SustainAi
```

## Step 2: Set Up Python Backend

### 2a. Create Virtual Environment

```bash
# Using Python 3.11 (recommended)
python3.11 -m venv venv

# Activate the environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### 2b. Install Backend Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Troubleshooting**:
- If scikit-learn installation fails, ensure you have build tools:
  - macOS: `xcode-select --install`
  - Linux: `apt-get install build-essential`
  - Windows: Install Microsoft C++ Build Tools

### 2c. Verify Backend Setup

```bash
# Check if all modules are installed
python -c "import torch, sklearn, fastapi, uvicorn; print('✓ All dependencies installed')"

# Check model artifacts exist
ls -la artifacts/
# Should show: price_features.json, yield_features.json
```

## Step 3: Start the Backend Server

```bash
# With activated venv
uvicorn cloud.api.app:app --host 0.0.0.0 --port 8000 --reload

# Expected output:
# Uvicorn running on http://0.0.0.0:8000
# ✓ API ready to serve requests
```

**Keep this terminal open** while developing.

Test the backend:
```bash
# In another terminal
curl http://localhost:8000/health
# Should return: {"status":"ok","models_loaded":true}
```

## Step 4: Set Up Next.js Frontend

### 4a. Install Frontend Dependencies

```bash
cd frontend
npm install
```

**Troubleshooting**:
- Clear npm cache if you encounter issues:
  ```bash
  npm cache clean --force
  npm install
  ```

### 4b. Create Environment File

```bash
# Copy example to .env.local
cp .env.example .env.local

# Edit if needed (defaults should work for local development)
cat .env.local
# BACKEND_URL=http://127.0.0.1:8000
```

### 4c. Verify Frontend Build

```bash
# Check if it compiles without errors
npm run build

# Expected output should show routes compiling successfully
# If there are errors, check TypeScript imports
```

## Step 5: Start the Frontend Server

```bash
# With current directory still in 'frontend'
npm run dev

# Expected output:
# ▲ Next.js 15.5.14
# Local:        http://localhost:3000
```

**Keep this terminal open** while developing.

## Step 6: Test the Full Integration

### Test in Browser

1. Open http://localhost:3000 in your browser
2. Navigate to `/analyze` page
3. Fill in the form:
   - Select a district (e.g., "Guntur")
   - Select a season (e.g., "Kharif")
   - Enter farm area (e.g., "10" hectares)
   - Optionally upload a leaf image
   - Click "Analyze"

4. Expected result: You should see crop recommendations and optionally disease predictions

### Check Network Traffic

1. Open **DevTools** (F12 or Cmd+Option+I)
2. Go to **Network** tab
3. Submit the form again
4. Look for `/api/predict` request
5. Check response for crop recommendations

### Verify API Health

```bash
# Terminal 1 (if not already running)
curl http://localhost:8000/health
# Response: {"status":"ok","models_loaded":true,"api_version":"1.0.0"}

# Terminal 2 (test prediction endpoint structure)
curl -X GET http://localhost:8000/docs
# Opens interactive Swagger documentation
```

## Development Workflow

### Making Changes

**Backend Changes**:
- Edit files in `cloud/api/` or `src/`
- Server auto-reloads with `--reload` flag
- Test via http://localhost:8000/docs (Swagger UI)

**Frontend Changes**:
- Edit files in `frontend/app/` or `frontend/components/`
- Server auto-reloads changes
- Test in browser at http://localhost:3000

### Debugging

**Frontend Debugging**:
- Use DevTools (F12)
- Check Console for errors
- Use React DevTools extension
- Check Network tab for API calls

**Backend Debugging**:
- Check terminal output for logs
- Use `print()` statements (visible in terminal)
- Check request/response in browser DevTools Network tab

### Running Tests

```bash
# Backend tests
pytest tests/

# Frontend linting
cd frontend && npm run lint
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Activate virtual environment
```bash
source venv/bin/activate  # macOS/Linux
```

### Issue: "CORS error: Access-Control-Allow-Origin missing"
**Solution**: Ensure `BACKEND_URL` in frontend/.env.local matches your running backend
```bash
cat frontend/.env.local
# Should show: BACKEND_URL=http://127.0.0.1:8000
```

### Issue: "Port 8000 already in use"
**Solution**: Kill the process using port 8000
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: "Port 3000 already in use"
**Solution**: Use a different port
```bash
npm run dev -- -p 3001
```

### Issue: "Module scikit-learn has no attribute..."
**Solution**: The environment may have the wrong sklearn version
```bash
pip uninstall scikit-learn
pip install scikit-learn==1.6.1
```

### Issue: Models not loading (API returns 503)
**Solution**: Verify model artifacts exist
```bash
ls -la artifacts/
# Must contain: price_features.json, yield_features.json
```

## Project Structure

```
KrishiMind_SustainAi/
├── frontend/                 # Next.js application (port 3000)
│   ├── app/                  # App router pages
│   ├── components/           # React components
│   ├── package.json
│   └── .env.local            # Environment (don't commit)
├── cloud/api/                # FastAPI application
│   ├── app.py                # Main FastAPI app
│   ├── schemas.py            # Request/response schemas
│   └── model_loader.py       # Model loading logic
├── src/                      # Python source code
│   ├── crop_optimizer.py     # Crop optimization
│   ├── feature_builder.py    # Feature engineering
│   └── plant_disease_detection/  # Disease detection models
├── artifacts/                # Pre-trained model files
│   ├── price_features.json
│   └── yield_features.json
├── requirements.txt          # Python dependencies
├── render.yaml              # Render deployment config
├── vercel.json              # Vercel deployment config
└── DEPLOYMENT.md            # Production deployment guide
```

## Next Steps

After setting up locally:

1. **Read** [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment
2. **Review** [README.md](./README.md) for project overview
3. **Explore** API documentation at http://localhost:8000/docs
4. **Check** code in `src/` and `cloud/api/` for understanding the architecture

## Getting Help

If you encounter issues:

1. Check the error message carefully
2. Search existing GitHub issues
3. Review logs in terminal
4. Check DevTools Console (browser)
5. Verify all dependencies are installed with correct versions

---

**Happy developing!** 🌾✨
