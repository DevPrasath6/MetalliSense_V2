# 🚀 MetalliSense AI Service - Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. System Requirements
- [ ] Python 3.11 installed (check: `python --version` or `python3.11 --version`)
- [ ] pip package manager available
- [ ] 2GB free disk space
- [ ] Network access to Node.js backend (if separate servers)

### 2. Installation
- [ ] Navigate to `ai-service` directory
- [ ] Run setup script (`setup.bat` or `./setup.sh`)
- [ ] Verify virtual environment created (`venv/` directory exists)
- [ ] Confirm dependencies installed (check for errors)
- [ ] Verify dataset generated (`app/data/dataset.csv` exists)
- [ ] Verify models trained (`app/models/*.pkl` files exist)

### 3. Testing
- [ ] Start the service (`start.bat` or `./start.sh`)
- [ ] Access health endpoint: http://localhost:8000/health
- [ ] Verify both models loaded (check health response)
- [ ] Run API tests: `python test_api.py`
- [ ] Test anomaly detection endpoint
- [ ] Test alloy recommendation endpoint
- [ ] Check API documentation: http://localhost:8000/docs

### 4. Integration
- [ ] Note AI service URL (default: http://localhost:8000)
- [ ] Update Node.js backend with AI service endpoint
- [ ] Test Node.js → Python AI service communication
- [ ] Verify response parsing in Node.js
- [ ] Test error handling (AI service down scenario)

## 🔧 Configuration Checklist

### API Settings (app/config.py)
- [ ] `API_HOST` - Set to appropriate host (0.0.0.0 for external access)
- [ ] `API_PORT` - Default 8000, change if port conflict
- [ ] Review anomaly severity thresholds
- [ ] Review safety constraints (MAX_ADDITION_PERCENTAGE)

### Production Settings
- [ ] Set `reload=False` in uvicorn configuration
- [ ] Configure CORS origins in `main.py` for security
- [ ] Set up logging configuration
- [ ] Consider using Gunicorn with Uvicorn workers

## 🔒 Security Checklist

- [ ] Virtual environment activated before running
- [ ] No hardcoded credentials in code
- [ ] CORS configured appropriately (not wildcard in production)
- [ ] API accessible only from Node.js backend (firewall rules)
- [ ] Models and dataset not exposed via web endpoints
- [ ] Rate limiting configured (if needed)
- [ ] Input validation through Pydantic schemas

## 📊 Monitoring Checklist

- [ ] Health endpoint monitored regularly
- [ ] Model loading verified on startup
- [ ] API response times tracked
- [ ] Error rates monitored
- [ ] Disk space monitored (logs, temp files)
- [ ] Memory usage tracked

## 🐛 Troubleshooting Checklist

### If Models Don't Load
- [ ] Check if .pkl files exist in `app/models/`
- [ ] Re-run training scripts
- [ ] Verify dataset exists and is valid
- [ ] Check Python 3.11 is being used (not 3.12 or 3.10)

### If API Doesn't Start
- [ ] Verify virtual environment is activated
- [ ] Check if port 8000 is available
- [ ] Review dependencies installation
- [ ] Check Python version is 3.11 (run `python --version`)
- [ ] Review terminal output for errors

### If Predictions Fail
- [ ] Verify input data format matches schema
- [ ] Check if all required elements are present (Fe, C, Si, Mn, P, S)
- [ ] Validate grade name (use /grades endpoint)
- [ ] Check model files integrity
- [ ] Review API logs for error details

## 📝 Documentation Checklist

- [ ] README.md reviewed
- [ ] QUICKSTART.md instructions followed
- [ ] API documentation accessible
- [ ] Team trained on endpoints
- [ ] Integration examples provided to Node.js team
- [ ] Error codes documented

## 🔄 Maintenance Checklist

### Daily
- [ ] Check service status (health endpoint)
- [ ] Monitor error logs
- [ ] Verify API response times

### Weekly
- [ ] Review anomaly detection accuracy
- [ ] Check alloy recommendation feedback
- [ ] Monitor disk space usage

### Monthly
- [ ] Review and update dependencies
- [ ] Retrain models if needed (with updated data)
- [ ] Analyze prediction patterns
- [ ] Update documentation if needed

## 🚀 Deployment Commands

### Start Service (Development)
```bash
cd ai-service
# Windows
start.bat

# Linux/Mac
./start.sh
```

### Start Service (Production)
```bash
cd ai-service
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Background Service (Linux)
```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ai-service.log 2>&1 &
```

### As System Service (Linux - systemd)
Create `/etc/systemd/system/metallisense-ai.service`:
```ini
[Unit]
Description=MetalliSense AI Service
After=network.target

[Service]
Type=simple
User=<your-user>
WorkingDirectory=/path/to/ai-service
Environment="PATH=/path/to/ai-service/venv/bin"
ExecStart=/path/to/ai-service/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable metallisense-ai
sudo systemctl start metallisense-ai
sudo systemctl status metallisense-ai
```

## 🔗 Integration Test Checklist

### Test from Node.js Backend
```javascript
// Test 1: Health Check
const health = await axios.get('http://localhost:8000/health');
console.assert(health.status === 200);
console.assert(health.data.models_loaded.anomaly_model === true);
console.assert(health.data.models_loaded.alloy_model === true);

// Test 2: Anomaly Detection
const anomaly = await axios.post('http://localhost:8000/anomaly/predict', {
  composition: { Fe: 85.5, C: 3.2, Si: 2.1, Mn: 0.6, P: 0.04, S: 0.02 }
});
console.assert(anomaly.status === 200);
console.assert('anomaly_score' in anomaly.data);
console.assert('severity' in anomaly.data);

// Test 3: Alloy Correction
const alloy = await axios.post('http://localhost:8000/alloy/recommend', {
  grade: 'SG-IRON',
  composition: { Fe: 81.2, C: 4.4, Si: 3.1, Mn: 0.4, P: 0.05, S: 0.02 }
});
console.assert(alloy.status === 200);
console.assert('recommended_additions' in alloy.data);
console.assert('confidence' in alloy.data);
```

## 📦 Backup Checklist

- [ ] Trained models backed up (`app/models/*.pkl`)
- [ ] Configuration files backed up (`app/config.py`)
- [ ] Dataset backed up (`app/data/dataset.csv`)
- [ ] Grade specifications backed up (`app/data/grade_specs.py`)
- [ ] Custom modifications documented

## ✅ Final Verification

Before going live, verify:

1. **Service Running**: http://localhost:8000/health returns 200
2. **Models Loaded**: Health check shows both models = true
3. **API Documentation**: http://localhost:8000/docs accessible
4. **Test Predictions**: Both endpoints return valid responses
5. **Node.js Integration**: Backend can successfully call AI service
6. **Error Handling**: Service handles invalid inputs gracefully
7. **Performance**: Response times < 100ms for predictions
8. **Virtual Environment**: Service runs in isolated venv

## 🎉 Go Live Checklist

- [ ] All tests passing
- [ ] Documentation complete
- [ ] Team trained
- [ ] Monitoring in place
- [ ] Backup strategy defined
- [ ] Rollback plan prepared
- [ ] Service started and stable
- [ ] Integration verified
- [ ] Performance benchmarked
- [ ] Stakeholders notified

---

**Status Check**: [  ] Ready for Production

Date: _______________
Deployed By: _______________
Verified By: _______________
