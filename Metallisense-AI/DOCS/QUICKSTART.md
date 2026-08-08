# 🚀 Quick Start Guide - MetalliSense AI Service

## Prerequisites

- **Python 3.11** (required - optimized for ML workloads)
- pip (Python package installer)
- 2GB free disk space (for models and dataset)

## ⚡ Fast Setup (5 minutes)

### Windows

```bash
# 1. Navigate to ai-service directory
cd k:\Metallisense-AI\ai-service

# 2. Run automated setup
setup.bat

# 3. Wait for completion (generates data + trains models)
# This takes ~3-5 minutes

# 4. Start the service
start.bat
```

### Linux/Mac

```bash
# 1. Navigate to ai-service directory
cd /path/to/Metallisense-AI/ai-service

# 2. Make scripts executable
chmod +x setup.sh start.sh

# 3. Run automated setup
./setup.sh

# 4. Wait for completion (generates data + trains models)
# This takes ~3-5 minutes

# 5. Start the service
./start.sh
```

## ✅ Verify Installation

Once the service is running, open your browser:

1. **API Docs**: http://localhost:8000/docs
2. **Health Check**: http://localhost:8000/health

Or use curl:
```bash
curl http://localhost:8000/health
```

## 🧪 Test the APIs

### Test 1: Anomaly Detection

```bash
curl -X POST "http://localhost:8000/anomaly/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "composition": {
      "Fe": 85.5,
      "C": 3.2,
      "Si": 2.1,
      "Mn": 0.6,
      "P": 0.04,
      "S": 0.02
    }
  }'
```

### Test 2: Alloy Correction

```bash
curl -X POST "http://localhost:8000/alloy/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "grade": "SG-IRON",
    "composition": {
      "Fe": 81.2,
      "C": 4.4,
      "Si": 3.1,
      "Mn": 0.4,
      "P": 0.05,
      "S": 0.02
    }
  }'
```

### Or use the test script:

```bash
# Make sure virtual environment is activated!
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

python test_api.py
```

## 📁 What Gets Created

After setup, your directory will have:

```
ai-service/
├── venv/                    # 🆕 Virtual environment (isolated Python)
├── app/
│   ├── data/
│   │   └── dataset.csv      # 🆕 30,000 synthetic samples
│   └── models/
│       ├── anomaly_model.pkl    # 🆕 Trained Agent 3
│       └── alloy_model.pkl      # 🆕 Trained Agent 4
└── ... (other files)
```

## 🔧 Common Issues

### Issue: "Python 3.11 not found"
**Solution:** Install Python 3.11:
- Windows: Download from https://www.python.org/downloads/release/python-3119/
- Ubuntu/Debian: `sudo apt install python3.11 python3.11-venv`
- macOS: `brew install python@3.11`

### Issue: "Virtual environment not found"
**Solution:** Run `setup.bat` (Windows) or `./setup.sh` (Linux/Mac) first

### Issue: "Module not found"
**Solution:** Make sure virtual environment is activated:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

### Issue: "Port 8000 already in use"
**Solution:** Change port in `app/config.py`:
```python
API_PORT = 8001  # or any available port
```

### Issue: "Models not loading"
**Solution:** Re-run training:
```bash
# Activate virtual environment first!
python app/training/train_anomaly.py
python app/training/train_alloy_agent.py
```

## 🔄 Daily Usage

**Starting the service:**
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

**Stopping the service:**
- Press `Ctrl+C` in the terminal

**Checking status:**
```bash
curl http://localhost:8000/health
```

## 🔗 Integration with Node.js

Once the AI service is running, your Node.js backend can call it:

```javascript
const axios = require('axios');

// Anomaly detection
const response = await axios.post('http://localhost:8000/anomaly/predict', {
  composition: { Fe: 85.5, C: 3.2, Si: 2.1, Mn: 0.6, P: 0.04, S: 0.02 }
});

console.log('Anomaly Score:', response.data.anomaly_score);
console.log('Severity:', response.data.severity);
```

## 📚 Next Steps

- ✅ Read [README.md](README.md) for detailed documentation
- ✅ Explore API at http://localhost:8000/docs
- ✅ Check available grades: http://localhost:8000/grades
- ✅ Integrate with your Node.js backend

## 💡 Tips

1. **Always activate the virtual environment** before running Python commands
2. **Keep the AI service running** while your Node.js backend is active
3. **Models persist** - no need to retrain after restart
4. **Dataset is reusable** - generated once during setup

## 🆘 Need Help?

- Check logs in the terminal where the service is running
- Visit http://localhost:8000/docs for API documentation
- Ensure Python 3.8+ is installed: `python --version`
