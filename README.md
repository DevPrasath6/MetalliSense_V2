# MetalliSense

Unified documentation for the full MetalliSense ecosystem: AI services, Node.js backend, and React frontend.

## What This Repository Contains

This workspace contains a multi-service industrial metal quality platform with:

- A production-oriented Python AI service with anomaly detection, alloy correction, and Explainable AI copilot
- A Node.js backend for authentication, business APIs, and orchestration
- A React frontend for operator workflows and dashboard views
- A legacy AI module kept for reference and model-evolution history

## Repository Structure

```text
Metallisense/
|-- README.md                       # Aggregated guide (this file)
|-- Metallisense-Agent/             # Primary AI service (FastAPI + ML agents + Copilot)
|-- Metallisense-AI/                # Legacy ML module and historical model fixes
|-- Metallisense-frontend/          # React + Vite frontend
`-- MetalliSense-Node-BE/           # Express backend and integration layer
```

## High-Level Architecture

```text
[React Frontend :5173]
	|
	v
[Node Backend :3000 or configured PORT]
	|
	v
[Python AI Service :8001]
  |- /agents/analyze
  |- /copilot/explain
  |- /copilot/chat
  |- /copilot/voice/*
```

Data and integrations:

- Firebase auth integration exists in backend startup path
- MongoDB is used by backend models/controllers
- Optional OPC-UA integration exists in backend service layer
- Groq + TTS/STT integrations are used in the AI copilot flow

## Project Roles By Folder

### 1) Metallisense-Agent (Primary AI Service)

Purpose:

- Main production AI layer (FastAPI)
- Agent orchestration for anomaly and alloy recommendations
- Explainable AI Copilot APIs and voice endpoints

Main references:

- `Metallisense-Agent/README.md`
- `Metallisense-Agent/DOCS/QUICKSTART.md`
- `Metallisense-Agent/DOCS/API_ROUTES.md`
- `Metallisense-Agent/DOCS/COPILOT_API_REFERENCE.md`
- `Metallisense-Agent/DOCS/RETRAINING_INSTRUCTIONS.md`

Important notes:

- Current runtime config in `Metallisense-Agent/app/config.py` sets AI API port to `8001`
- Some older docs still mention `8000`; use `8001` as the current default

### 2) Metallisense-AI (Legacy ML Module)

Purpose:

- Earlier ML-focused implementation (training and inference oriented)
- Useful as historical baseline and model-fix reference

Main references:

- `Metallisense-AI/DOCS/QUICKSTART.md`
- `Metallisense-AI/DOCS/IMPLEMENTATION_SUMMARY.md`
- `Metallisense-AI/DOCS/DEPLOYMENT_CHECKLIST.md`
- `Metallisense-AI/MODEL_FIXES.md`

Important notes:

- This folder is useful for understanding prior model behaviors and fix evolution
- Primary active AI service for integration should be `Metallisense-Agent`

### 3) Metallisense-frontend (Web UI)

Purpose:

- React/Vite operator interface
- Pages for anomaly detection, recommendations, grades, dashboard
- Copilot UI integration (explanations + chat + voice)

Main references:

- `Metallisense-frontend/README.md` (currently default Vite template)
- `Metallisense-frontend/AI_COPILOT_CHANGES.md` (actual integration details)

### 4) MetalliSense-Node-BE (Backend/API Gateway)

Purpose:

- Express API layer with route grouping (`/api/v1/*`, `/api/v2/*`)
- Integrates auth, grades, training data, synthetic generation, and AI proxy routes
- Connects to DB and initializes OPC-UA service hooks

Main references:

- `MetalliSense-Node-BE/package.json`
- `MetalliSense-Node-BE/app.js`
- `MetalliSense-Node-BE/server.js`

Important notes:

- This folder currently has no dedicated README
- Default server port is `process.env.PORT || 3000`

## Prerequisites

- Python 3.11 (recommended for AI services)
- Node.js 18+
- npm
- MongoDB connection string for backend
- Optional: Groq API key for copilot explanation/chat/voice workflows
- Optional: Firebase credentials for auth flows

## Recommended Startup Order

Start services in this order to avoid dependency errors:

1. AI service (`Metallisense-Agent`)
2. Node backend (`MetalliSense-Node-BE`)
3. Frontend (`Metallisense-frontend`)

## Quick Start

### A) Start AI Service (Metallisense-Agent)

Windows:

```powershell
cd Metallisense-Agent
setup.bat
start.bat
```

Manual alternative:

```powershell
cd Metallisense-Agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python setup.py
python app/main.py
```

Expected:

- AI API at `http://localhost:8001`
- Swagger docs at `http://localhost:8001/docs`

### B) Start Backend (MetalliSense-Node-BE)

```powershell
cd MetalliSense-Node-BE
npm install
npm start
```

Production-mode script available:

```powershell
npm run start:prod
```

Expected:

- API health route: `GET /api/v1/health`
- Port from `PORT`, fallback `3000`

### C) Start Frontend (Metallisense-frontend)

```powershell
cd Metallisense-frontend
npm install
npm run dev
```

Expected:

- Frontend at Vite default local URL (typically `http://localhost:5173`)

## API Surface (Aggregated)

### AI Service (Metallisense-Agent)

Core endpoints:

- `POST /agents/analyze`
- `POST /anomaly/predict` (legacy compatibility)
- `POST /alloy/recommend` (legacy compatibility)
- `GET /health`
- `GET /grades`
- `GET /grades/{grade}`

Copilot endpoints:

- `POST /copilot/explain`
- `POST /copilot/chat`
- `DELETE /copilot/chat/history`
- `POST /copilot/voice/transcribe`
- `POST /copilot/voice/synthesize`
- `GET /copilot/voice/languages`

### Backend API (MetalliSense-Node-BE)

From route registration in `app.js`:

- `GET /api/v1/health`
- `POST/GET/... /api/v1/users`, `/api/v1/metal-grades`, `/api/v1/spectrometer`
- `POST/GET/... /api/v2/auth`
- `POST/GET/... /api/v2/grades`
- `POST/GET/... /api/v2/training-data`
- `POST/GET/... /api/v2/synthetic`
- `POST/GET/... /api/v2/ai`

## Model Training and Retraining

Primary retraining path:

```powershell
cd Metallisense-Agent
python retrain_models.py
```

What retraining docs describe:

- Dataset verification
- Anomaly model retraining with tightened normal-sample filtering
- Alloy model retraining
- Determinism and inference verification checks

References:

- `Metallisense-Agent/DOCS/RETRAINING_INSTRUCTIONS.md`
- `Metallisense-AI/MODEL_FIXES.md`

## Integration Notes

Frontend copilot integration details are documented in:

- `Metallisense-frontend/AI_COPILOT_CHANGES.md`

This includes:

- Copilot service methods
- Explanation card UI
- Chat/voice UI component behavior
- Expected base URL usage for copilot endpoints

## Known Documentation Gaps and Inconsistencies

- Root README was previously empty and is now aggregated here
- Backend folder currently lacks its own README
- Port references vary in old docs (`8000` vs `8001`) for AI service; current config uses `8001`
- Frontend README is still template-level and not project-specific

## Suggested Next Documentation Improvements

1. Add `MetalliSense-Node-BE/README.md` with env variables and endpoint mapping.
2. Add `.env.example` files for Agent, Backend, and Frontend.
3. Update frontend README to reflect actual pages and API integrations.
4. Standardize all docs to AI port `8001` unless intentionally overridden.

## Detailed Docs Index

### Metallisense-Agent

- `Metallisense-Agent/README.md`
- `Metallisense-Agent/DOCS/AGENT_ARCHITECTURE.md`
- `Metallisense-Agent/DOCS/AGENT_IMPLEMENTATION_SUMMARY.md`
- `Metallisense-Agent/DOCS/AGENT_QUICKSTART.md`
- `Metallisense-Agent/DOCS/API_ROUTES.md`
- `Metallisense-Agent/DOCS/COPILOT_API_REFERENCE.md`
- `Metallisense-Agent/DOCS/COPILOT_SETUP.md`
- `Metallisense-Agent/DOCS/FILE_LISTING.md`
- `Metallisense-Agent/DOCS/FRONTEND_INTEGRATION_GUIDE.md`
- `Metallisense-Agent/DOCS/IMPLEMENTATION_SUMMARY.md`
- `Metallisense-Agent/DOCS/QUICK_REFERENCE.md`
- `Metallisense-Agent/DOCS/QUICKSTART.md`
- `Metallisense-Agent/DOCS/RETRAINING_INSTRUCTIONS.md`

### Metallisense-AI

- `Metallisense-AI/MODEL_FIXES.md`
- `Metallisense-AI/DOCS/DEPLOYMENT_CHECKLIST.md`
- `Metallisense-AI/DOCS/FILE_LISTING.md`
- `Metallisense-AI/DOCS/IMPLEMENTATION_SUMMARY.md`
- `Metallisense-AI/DOCS/QUICKSTART.md`

### Metallisense-frontend

- `Metallisense-frontend/README.md`
- `Metallisense-frontend/AI_COPILOT_CHANGES.md`

### MetalliSense-Node-BE

- `MetalliSense-Node-BE/package.json`
- `MetalliSense-Node-BE/app.js`
- `MetalliSense-Node-BE/server.js`
