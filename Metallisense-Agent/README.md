# MetalliSense AI Service

🤖 **Production-Grade AI Agent System for Industrial Metal Quality Control**

## Overview

MetalliSense AI Service implements a **production-grade agentic architecture** that wraps trained ML models into advisory AI agents. This system provides intelligent decision support for spectrometer analysis and alloy correction in industrial metallurgy.

### 🎯 Core Agents

1. **Anomaly Detection Agent**: Detects abnormal spectrometer behavior
2. **Alloy Correction Agent**: Recommends corrective alloy additions
3. **🆕 Explainable AI Copilot**: Natural language explanations with voice interface

### 🔐 Safety Principles

- ✅ **Advisory Only**: Agents never take autonomous actions
- ✅ **Stateless**: Each prediction is independent
- ✅ **Deterministic**: Same input always produces same output
- ✅ **Explainable**: Every decision includes reasoning
- ✅ **Human-in-Loop**: All actions require human approval

## Features

- 🤖 Production-grade agent orchestration
- 🧠 Agent Manager for coordinated decision-making
- 📋 Policy-based agent invocation
- 🔒 Safety constraints and governance
- ⚡ FastAPI with async support
- 🔄 Seamless Node.js integration
- 📊 Physics-aware synthetic data generation
- 🚫 No LLM dependencies for core ML
- 📝 Comprehensive logging and audit trails
- **🆕 Explainable AI Copilot**:
  - 💬 Natural language explanations via Groq LLM
  - 🎤 Voice input (Speech-to-Text)
  - 🔊 Voice output (Text-to-Speech)
  - 🌍 Multi-language support (12 languages)
  - 💭 Interactive chatbot with conversation history

## Architecture

### Agent-Based Architecture with Explainable AI

```
┌─────────────────────────────────────────────────────────┐
│                 Incoming Spectrometer Data              │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│         Deterministic Rule Engine (Node.js)             │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│          EXPLAINABLE AI COPILOT (NEW) 🆕                │
│  • Groq LLM (llama-3.3-70b-versatile)                   │
│  • Natural Language Explanations                        │
│  • Interactive Chatbot                                  │
│  • Voice Interface (STT/TTS)                            │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│              AGENT MANAGER (Python)                     │
│  • Orchestration Logic                                  │
│  • Decision Policy Enforcement                          │
│  • Safety Rules                                         │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│  Anomaly    │  │   Alloy     │
│   Agent     │  │  Correction │
│             │  │   Agent     │
│  (Always)   │  │ (Conditional)│
└─────────────┘  └─────────────┘
```

### Project Structure

```
ai-service/
├── app/
│   ├── main.py                      # FastAPI with agent & copilot endpoints
│   ├── config.py                    # Configuration (with Groq API key)
│   ├── schemas.py                   # Request/response schemas
│   │
│   ├── copilot/                     # 🆕 Explainable AI Copilot
│   │   ├── groq_explainer.py        # LLM integration
│   │   ├── voice_service.py         # STT/TTS services
│   │   └── schemas.py               # Copilot schemas
│   │
│   ├── agents/
│   │   ├── anomaly_agent.py         # ML model (trained)
│   │   ├── alloy_agent.py           # ML model (trained)
│   │   ├── anomaly_agent_wrapper.py # Agent 1 wrapper ✨
│   │   ├── alloy_agent_wrapper.py   # Agent 2 wrapper ✨
│   │   └── agent_manager.py         # Orchestration ✨
│   │
│   ├── policies/
│   │   └── decision_policy.py       # Decision rules ✨
│   │
│   ├── data/
│   │   ├── grade_specs.py           # Grade specifications
│   │   ├── synthetic_gen.py         # Data generator
│   │   └── dataset.csv              # Generated dataset
│   │
│   ├── training/
│   │   ├── train_anomaly.py         # Train Agent 1 model
│   │   └── train_alloy_agent.py     # Train Agent 2 model
│   │
│   ├── inference/
│   │   ├── anomaly_predict.py       # Model inference
│   │   └── alloy_predict.py         # Model inference
│   │
│   └── models/
│       ├── anomaly_model.pkl        # Trained model
│       └── alloy_model.pkl          # Trained model
│
└── requirements.txt

✨ = New agent architecture components
```

## Installation

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
cd ai-service
setup.bat
```

**Linux/Mac:**
```bash
cd ai-service
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Create a Python virtual environment
- ✅ Install all dependencies
- ✅ Generate synthetic dataset (30,000 samples)
- ✅ Train both AI models

### Option 2: Manual Setup

**1. Create Virtual Environment:**
```bash
cd ai-service

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3.11 -m venv venv
source venv/bin/activate
```

**2. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run Complete Setup:**
```bash
python setup.py
```

## Quick Start

> **Important:** Always activate the virtual environment before running any commands!

**Activate Virtual Environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 1. Generate Synthetic Dataset (if not using automated setup)

```bash
python -c "
import sys
sys.path.append('app')
from data.grade_specs import GradeSpecificationGenerator
from data.synthetic_gen import SyntheticDataGenerator
from config import DATASET_PATH, SYNTHETIC_DATASET_SIZE, NORMAL_RATIO

grade_gen = GradeSpecificationGenerator()
data_gen = SyntheticDataGenerator(grade_gen)
df = data_gen.generate_dataset(SYNTHETIC_DATASET_SIZE, NORMAL_RATIO)
df.to_csv(DATASET_PATH, index=False)
print(f'Dataset saved to {DATASET_PATH}')
"
```

### 2. Train AI Agents

**Initial Training (First Time):**
```bash
# Train Anomaly Detection Agent
python app/training/train_anomaly.py

# Train Alloy Correction Agent
python app/training/train_alloy_agent.py
```

**OR use the complete setup script:**
```bash
python setup.py
```

### 3. Retraining Models with New Data

When you add new data to `app/data/dataset.csv`, retrain the models:

**Quick Retrain (Recommended):**
```bash
python retrain_models.py
```

**OR use setup.py:**
```bash
python setup.py
```

Both scripts will:
- ✅ Load existing dataset.csv
- ✅ Retrain both models with new data
- ✅ Save updated models
- ✅ Verify system is ready

> **Note:** `setup.py` has been updated to skip data generation and use existing data only.

### 4. Start API Service

```bash
python app/main.py
```

The API will be available at `http://localhost:8000`

### 5. Deactivate Virtual Environment (when done)

```bash
deactivate
```
python app/training/train_alloy_agent.py
```

### 3. Start API Service

**Standard Start:**
```bash
python app/main.py
```

**With Explainable AI Copilot (🆕 NEW):**

First, set your Groq API key:
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key_here"

# Windows CMD
set GROQ_API_KEY=your_groq_api_key_here

# Linux/Mac
export GROQ_API_KEY="your_groq_api_key_here"
```

Then start the service:
```bash
python app/main.py
```

The API will be available at `http://localhost:8001`

**Copilot Features:**
- 💬 Natural language explanations
- 🎤 Voice input (Speech-to-Text)
- 🔊 Voice output (Text-to-Speech)
- 💭 Interactive chatbot

> **Get Groq API Key:** https://console.groq.com/keys (free tier available)
> 
> **Full Setup Guide:** See [DOCS/COPILOT_SETUP.md](DOCS/COPILOT_SETUP.md)

## API Endpoints

### 🤖 Agent Analysis (Production Endpoint)

**The primary endpoint for production use:**

```http
POST /agents/analyze
Content-Type: application/json

{
  "composition": {
    "Fe": 81.2,
    "C": 4.4,
    "Si": 3.1,
    "Mn": 0.4,
    "P": 0.05,
    "S": 0.02
  },
  "grade": "SG-IRON"
}
```

### 🆕 Explainable AI Copilot Endpoints

#### Get Explanation
```http
POST /copilot/explain
Content-Type: application/json

{
  "composition": {"Fe": 94.5, "C": 3.2, "Si": 2.0, "Mn": 0.4, "P": 0.05, "S": 0.10},
  "grade": "GREY-IRON"
}
```

Response:
```json
{
  "explanation": "Analysis shows HIGH severity anomaly (score: 0.87)...",
  "summary": "HIGH severity anomaly. Immediate correction required.",
  "action_items": [
    "Add 0.22% Silicon",
    "Add 0.15% Manganese",
    "Re-test after additions"
  ],
  "risk_level": "HIGH",
  "confidence": 0.93
}
```

#### Interactive Chat
```http
POST /copilot/chat
Content-Type: application/json

{
  "message": "Why do we need to add Manganese?",
  "include_context": true
}
```

#### Voice Transcription (Speech-to-Text)
```http
POST /copilot/voice/transcribe
Content-Type: multipart/form-data

audio=@recording.wav
language=en
```

#### Voice Synthesis (Text-to-Speech)
```http
POST /copilot/voice/synthesize
Content-Type: application/json

{
  "text": "Silicon addition is recommended",
  "language": "en",
  "slow": false
}
```

**Complete API Documentation:** See [DOCS/COPILOT_API_REFERENCE.md](DOCS/COPILOT_API_REFERENCE.md)

---     

**Response:**
```json
{
  "anomaly_agent": {
    "agent": "AnomalyDetectionAgent",
    "anomaly_score": 0.87,
    "severity": "HIGH",
    "confidence": 0.93,
    "explanation": "High anomaly detected - composition significantly deviates..."
  },
  "alloy_agent": {
    "agent": "AlloyCorrectionAgent",
    "recommended_additions": {
      "Si": 0.22,
      "Mn": 0.15
    },
    "confidence": 0.91,
    "explanation": "Adjusting elements toward SG-IRON grade midpoint..."
  },
  "final_note": "Human approval required before action",
  "timestamp": "2025-12-22T10:30:00.000Z"
}
```

**Agent Workflow:**
1. ✅ Anomaly Detection Agent **ALWAYS** runs
2. ✅ If severity is **HIGH**, Alloy Correction Agent runs
3. ✅ If severity is **MEDIUM/LOW**, Alloy Agent is **SKIPPED**
4. ✅ All outputs require **human approval**
5. ✅ No autonomous actions

---

### Health Check
```http
GET /health
```

---

### Legacy Endpoints (Backward Compatibility)

These endpoints are maintained for backward compatibility but the `/agents/analyze` endpoint is recommended for production use.

#### Anomaly Detection
```http
POST /anomaly/predict
Content-Type: application/json

{
  "composition": {
    "Fe": 81.2,
    "C": 4.4,
    "Si": 3.1,
    "Mn": 0.4,
    "P": 0.05,
    "S": 0.02
  }
}
```

Response:
```json
{
  "anomaly_score": 0.86,
  "severity": "HIGH",
  "message": "High anomaly detected. Potential sensor drift or unstable melt chemistry."
}
```

#### Alloy Correction Recommendation
```http
POST /alloy/recommend
Content-Type: application/json

{
  "grade": "SG-IRON",
  "composition": {
    "Fe": 81.2,
    "C": 4.4,
    "Si": 3.1,
    "Mn": 0.4,
    "P": 0.05,
    "S": 0.02
  }
}
```

Response:
```json
{
  "recommended_additions": {
    "Si": 0.22,
    "Mn": 0.15
  },
  "confidence": 0.91,
  "message": "High confidence recommendation. Additions should bring composition into spec.",
  "warning": null
}
```

#### Get Available Grades
```http
GET /grades
```

#### Get Grade Specification
```http
GET /grades/{grade}
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Integration with Node.js Backend

The AI service is designed to be called from the existing Node.js backend via HTTP.

### Production Integration (Agent-Based)

**Recommended approach using the Agent Manager:**

```javascript
const axios = require('axios');

// Agent-based analysis (RECOMMENDED)
const agentAnalysis = await axios.post('http://localhost:8000/agents/analyze', {
  composition: {
    Fe: 81.2,
    C: 4.4,
    Si: 3.1,
    Mn: 0.4,
    P: 0.05,
    S: 0.02
  },
  grade: 'SG-IRON'
});

// Access agent results
const anomalyAgent = agentAnalysis.data.anomaly_agent;
const alloyAgent = agentAnalysis.data.alloy_agent;

console.log(`Anomaly Severity: ${anomalyAgent.severity}`);
console.log(`Anomaly Score: ${anomalyAgent.anomaly_score}`);

if (alloyAgent.recommended_additions && Object.keys(alloyAgent.recommended_additions).length > 0) {
  console.log('Alloy Recommendations:', alloyAgent.recommended_additions);
  console.log('Confidence:', alloyAgent.confidence);
}

console.log('Safety Note:', agentAnalysis.data.final_note);
```

### Legacy Integration (Backward Compatibility)

```javascript
// Legacy approach - individual endpoints
const anomalyResponse = await axios.post('http://localhost:8000/anomaly/predict', {
  composition: {
    Fe: 81.2,
    C: 4.4,
    Si: 3.1,
    Mn: 0.4,
    P: 0.05,
    S: 0.02
  }
});

const alloyResponse = await axios.post('http://localhost:8000/alloy/recommend', {
  grade: 'SG-IRON',
  composition: {
    Fe: 81.2,
    C: 4.4,
    Si: 3.1,
    Mn: 0.4,
    P: 0.05,
    S: 0.02
  }
});
```

### 🔐 Integration Safety Guidelines

1. **Always require human approval** before acting on agent recommendations
2. **Log all agent decisions** for audit trail
3. **Never execute corrections automatically** without operator confirmation
4. **Display confidence scores** to operators
5. **Show explanations** for transparency

## Supported Grades

- **SG-IRON**: Spheroidal Graphite Cast Iron (Ductile Iron)
- **GREY-IRON**: Grey Cast Iron (General Purpose)
- **LOW-CARBON-STEEL**: Mild Steel (Carbon < 0.3%)
- **MEDIUM-CARBON-STEEL**: Medium Carbon Steel (0.3-0.6% C)
- **HIGH-CARBON-STEEL**: High Carbon Steel (0.6-1.4% C)

## Safety Features

### 🔐 Agent Safety Constraints

1. **Advisory Only**: Agents NEVER take autonomous actions
2. **Human-in-Loop**: All recommendations require explicit approval
3. **Stateless Operation**: No memory between predictions
4. **Deterministic**: Same input always produces same output
5. **Explainable**: Every decision includes reasoning
6. **Confidence Scoring**: Uncertainty is quantified
7. **Policy-Based**: Decision logic is centralized and auditable
8. **No Override**: Agents cannot override metallurgical rules

### Metallurgical Constraints

- Maximum addition limit: 5% per element
- Confidence thresholds for recommendations
- Warnings for large corrections
- No negative additions (cannot remove elements)
- Physics-aware constraints
- Grade specification validation

## Agent Usage in MetalliSense

### ✅ What Agents ARE Used For

- Detect hidden anomalies in spectrometer data
- Suggest corrective alloy actions
- Assist operators with decision support
- Improve process reliability
- Prevent false PASS approvals
- Provide confidence scores for recommendations

### ❌ What Agents ARE NOT Used For

- Automate furnace control
- Override metallurgical rules
- Make safety-critical decisions
- Autonomous actions without approval
- PASS/FAIL determination (handled by rule engine)

## Important Notes

- **AI does NOT decide PASS/FAIL**: The decision logic remains in the Node.js backend
- **No OPC UA in Python**: All industrial communication is handled by Node.js
- **Deterministic & Explainable**: All models use scikit-learn (no LLMs)
- **Safety-First**: Built-in constraints prevent unsafe recommendations
- **Models Are Pre-Trained**: This service wraps existing trained models
- **Agent Architecture**: Production-grade wrapper around ML models

## Development

### Running Tests

```bash
# Test grade specifications
python app/data/grade_specs.py

# Test synthetic data generation
python app/data/synthetic_gen.py

# Test inference modules
python app/inference/anomaly_predict.py
python app/inference/alloy_predict.py
```

### Configuration

Edit `app/config.py` to customize:
- Model parameters
- Severity thresholds
- Dataset size
- API settings

## Troubleshooting

### Models not loading

Ensure models are trained before starting the API:
```bash
python app/training/train_anomaly.py
python app/training/train_alloy_agent.py
```

### Import errors

Make sure you're in the correct directory and have installed dependencies:
```bash
cd ai-service
pip install -r requirements.txt
```

## License

Part of the MetalliSense project.
