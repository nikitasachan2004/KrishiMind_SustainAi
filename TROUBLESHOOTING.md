# Troubleshooting Guide

Common issues and solutions for KrishiMind SustainAI development and deployment.

## Local Development Issues

### Frontend Build Issues

#### Error: "Module not found: Can't resolve '@/components/...'"
**Cause**: Path aliases not configured correctly or component file doesn't exist

**Solution**:
1. Verify `tsconfig.json` has the correct path configuration:
   ```json
   "paths": {
     "@/*": ["./*"]
   }
   ```
2. Check component file exists in `components/` folder
3. Clear Next.js cache:
   ```bash
   rm -rf frontend/.next
   npm run build
   ```

#### Error: "ENOENT: no such file or directory"
**Cause**: File or directory doesn't exist or path is wrong

**Solution**:
1. Check the exact file path mentioned in error
2. Verify working directory: `pwd` should show project root
3. Verify case sensitivity (macOS is case-insensitive, Linux is not)

#### Error: "Port 3000 already in use"
**Cause**: Another process is using port 3000

**Solution**:
```bash
# Find and kill the process
lsof -ti:3000 | xargs kill -9

# OR use a different port
npm run dev -- -p 3001
```

#### Error: "npm ERR! code ERESOLVE"
**Cause**: Dependency version conflict

**Solution**:
```bash
npm cache clean --force
rm package-lock.json
npm install
```

---

### Backend Build Issues

#### Error: "ModuleNotFoundError: No module named 'fastapi'"
**Cause**: Virtual environment not activated

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

#### Error: "scikit-learn version mismatch"
**Cause**: Installed scikit-learn version doesn't match training version (1.6.1)

**Solution**:
```bash
pip uninstall scikit-learn
pip install scikit-learn==1.6.1
```

#### Error: "Models failed to load: FileNotFoundError"
**Cause**: Model artifact files missing

**Solution**:
1. Verify artifacts exist:
   ```bash
   ls -la artifacts/
   ```
2. Expected files:
   - `artifacts/price_features.json`
   - `artifacts/yield_features.json`

#### Error: "Port 8000 already in use"
**Cause**: Another process running on port 8000

**Solution**:
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

### Integration Issues

#### Error: "CORS policy: Cross-Origin Request Blocked"
**Cause**: Frontend and backend on different origins (ports), but CORS not properly configured

**Solution**:
1. Verify `BACKEND_URL` in frontend/.env.local:
   ```bash
   cat frontend/.env.local
   # Should show: BACKEND_URL=http://127.0.0.1:8000
   ```
2. Restart frontend after changing .env:
   ```bash
   npm run dev
   ```
3. Verify backend is running and returns health check:
   ```bash
   curl http://localhost:8000/health
   ```

#### Error: "Failed to fetch from /api/predict"
**Cause**: Backend not running or wrong URL

**Solution**:
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"ok","models_loaded":true}
   ```
2. Check browser DevTools Network tab for exact error
3. Verify environment variable: `echo $BACKEND_URL`

#### Error: "Form submission hangs or times out"
**Cause**: Backend processing is slow or backend crashed

**Solution**:
1. Check backend terminal for errors
2. Verify models loaded successfully at startup
3. Try with a smaller image (large uploads take longer)
4. Check free disk space (feature extraction may need space)

---

## Production Deployment Issues

### Vercel Deployment

#### Error: "Build failed: Command not found: next"
**Cause**: Next.js not installed or wrong directory

**Solution**:
1. In Vercel dashboard, verify:
   - Root Directory: `frontend` (or empty if using root package.json)
   - Build Command: `npm run build`
   - Output Directory: `.next`
2. Ensure `frontend/package.json` exists

#### Error: "Deployment successful but page shows 404"
**Cause**: Vercel deployed wrong directory

**Solution**:
1. Go to Vercel dashboard → Settings → General
2. Verify "Build Output Settings" shows `.next` folder
3. Check if Root Directory is set to `frontend`
4. Redeploy: Deployments → Redeploy

#### Error: "Environment variables not working in production"
**Cause**: Variables not set in Vercel or not updated after setting

**Solution**:
1. Go to Vercel dashboard → Settings → Environment Variables
2. Add/update `BACKEND_URL` = your Render API URL
3. Redeploy: Deployments → Redeploy with existing Build Cache
4. Wait for deployment to complete before testing

#### Error: "502 Bad Gateway when calling backend"
**Cause**: Backend is down or unreachable

**Solution**:
1. Verify backend is running on Render:
   - Go to https://dashboard.render.com
   - Check service status
   - Check logs for errors
2. Verify BACKEND_URL is correct (no trailing slash):
   - Should be: `https://krishimind-api.onrender.com`
   - Not: `https://krishimind-api.onrender.com/`
3. Test health endpoint directly:
   ```bash
   curl https://your-render-api.onrender.com/health
   ```

---

### Render Deployment

#### Error: "Build failed: Could not find requirements.txt"
**Cause**: render.yaml looking in wrong directory

**Solution**:
1. Ensure `requirements.txt` exists in repo root:
   ```bash
   ls -la requirements.txt
   ```
2. Verify render.yaml has correct buildCommand:
   ```yaml
   buildCommand: pip install -r requirements.txt
   ```

#### Error: "Python version unavailable"
**Cause**: Python 3.11.0 not available on Render

**Solution**:
1. Try Python 3.12.0:
   ```bash
   # Update render.yaml
   PYTHON_VERSION=3.12.0
   git push origin main
   ```
2. Or try without specific version:
   ```yaml
   runtime: python
   # Render will choose default version
   ```

#### Error: "Deployment successful but API returns 503"
**Cause**: Models failed to load at startup

**Solution**:
1. Check Render logs:
   - Dashboard → Web Service → Logs
   - Look for "Models failed to load" or import errors
2. Verify model artifacts in git:
   ```bash
   git ls-files | grep artifacts/
   ```
3. If artifacts missing from git, add them:
   ```bash
   git add artifacts/
   git commit -m "Add model artifacts"
   git push origin main
   ```

#### Error: "Timeout on first request"
**Cause**: Cold start or slow model loading

**Solution**:
1. Render free tier has slow startup, this is normal
2. Upgrade to Render "Standard" tier for faster cold starts
3. Or try making initial request again after ~30 seconds

#### Error: "API works locally but not on Render"
**Cause**: Environment variables or paths different on Render

**Solution**:
1. Check Render environment variables in dashboard
2. Verify no hardcoded absolute paths in code
3. Check logs for import errors: `PYTHONPATH` issues
4. Try using full import paths:
   ```python
   sys.path.insert(0, str(Path(__file__).parent.parent.parent))
   ```

#### Error: "Service spins down after 15 minutes of inactivity"
**Cause**: Render free tier auto-spindown feature

**Solution**:
1. Upgrade to "Standard" tier (paid)
2. Or set up a monitor to keep service alive:
   - Use external service like UptimeRobot
   - Configure to ping `/health` endpoint every 5 minutes

---

## Database/File Issues

#### Error: "Cannot write to /tmp: Permission denied"
**Cause**: Temporary file permissions issue in container

**Solution**:
1. Ensure temp file handling is correct:
   ```python
   import tempfile
   with tempfile.TemporaryFile() as f:
       # Write to temp file
   ```
2. Use `os.tmpdir()` or similar for temp paths

#### Error: "Model files too large for free tier"
**Cause**: Render free tier has storage limits

**Solution**:
1. Move large files to cloud storage (S3)
2. Download at startup from S3
3. Or upgrade to paid tier

---

## Network/DNS Issues

#### Error: "Failed to resolve hostname 'krishimind-api.onrender.com'"
**Cause**: DNS issue or Render service URL incorrect

**Solution**:
1. Verify correct Render URL:
   - Go to Render dashboard
   - Copy exact URL from service page
2. Test DNS resolution:
   ```bash
   nslookup krishimind-api.onrender.com
   curl -I https://krishimind-api.onrender.com/health
   ```
3. Check firewall/VPN isn't blocking Render

#### Error: "HTTPS certificate error in production"
**Cause**: Certificate not properly configured

**Solution**:
1. Render provides free SSL/TLS certificates
2. Wait 5-10 minutes after deployment for certificate to be issued
3. Force HTTPS by updating BACKEND_URL to use `https://`
4. Verify in browser: https://your-service.onrender.com

---

## Memory/Performance Issues

#### Error: "Process killed: OutOfMemory"
**Cause**: Running out of memory during model loading or inference

**Solution**:
1. Reduce model size or batch size
2. Upgrade to tier with more memory
3. Load models lazily instead of at startup
4. Check for memory leaks:
   ```python
   import tracemalloc
   tracemalloc.start()
   # ... code ...
   current, peak = tracemalloc.get_traced_memory()
   print(f"Memory: {peak / 1024 / 1024:.1f} MB")
   ```

#### Error: "Request times out after 60 seconds"
**Cause**: Long-running prediction or network latency

**Solution**:
1. Optimize prediction code
2. Add progress logging to monitor execution
3. Consider breaking into smaller chunks
4. Increase timeout in frontend if needed

---

## Debugging Tools

### Enable Debug Logging

**Backend**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Debug info: {variable}")
```

**Frontend**:
```javascript
// In browser console
localStorage.debug = '*'  // Enable all logs
```

### Use Render Logs

1. Go to https://dashboard.render.com
2. Select your service
3. Click "Logs" tab
4. View real-time logs from deployment

### Use Vercel Logs

1. Go to https://vercel.com/dashboard
2. Select your project
3. Click on a deployment
4. View "Function Logs" (real-time) or "Build Logs"

### Test API Endpoints Locally

```bash
# Install REST client
npm install -g rest-client  # Or use Insomnia/Postman

# Test health endpoint
curl -X GET http://localhost:8000/health

# Test prediction endpoint
curl -X POST http://localhost:8000/predict/crop-plan \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Guntur",
    "season": "Kharif",
    "area": 10,
    "scenario": {"rainfall_delta": 0, "temp_delta": 0}
  }'
```

---

## Getting More Help

1. **Check logs first**: Always look at error logs in terminal or dashboard
2. **Search issues**: GitHub Issues or Stack Overflow
3. **Community support**: Check project discussions
4. **Read documentation**: [SETUP.md](./SETUP.md), [DEPLOYMENT.md](./DEPLOYMENT.md)

---

**Last Updated**: 2025-04-25
