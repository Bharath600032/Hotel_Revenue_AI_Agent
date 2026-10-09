# Hotel Autonomous Revenue AI Agent

An enterprise AI-powered autonomous hotel revenue management platform that analyzes hotel reservation data, demand, occupancy, booking pace, historical ADR, competitor rates, holidays, events, weather, and seasonality to recommend optimal future room rates up to 365 days in advance.

## Core Features
- **Single Autonomous AI Agent**: ReAct-style agent with 22+ specialized domain tools.
- **Multi-Model Forecasting**: Naive, Moving Average, Seasonal Naive, SARIMAX, and XGBoost demand forecasting pipelines.
- **Multi-Factor Pricing Engine**: Data-driven rate optimization combining forecast demand, pickup pace, competitor positioning, and event multipliers.
- **Deterministic Pricing Guardrails**: Hard min/max price floors/ceilings, max daily % change limits, and human approval threshold triggers.
- **RAG Knowledge Base**: Vectorized strategy documents, SOPs, and contract rate plans powering grounded AI explanations.
- **Human-in-the-Loop Workflow**: Mandatory approval queue for high-impact pricing changes.
- **Dual Execution Modes**: **DEMO MODE** (zero external paid dependencies, SQLite/LocalDB fallback, synthetic dataset) and **PRODUCTION MODE** (SQL Server 2022, Redis, Claude/Gemini, live rate feeds).

## Quick Start (DEMO Mode)

### Option A: One-Click Launcher (Windows)
Double click or run `run_demo.bat` or `run_demo.ps1` from the repository root:
```cmd
.\run_demo.bat
```
This automatically seeds the 5-property demo dataset and launches both the backend API server (`http://localhost:8000`) and React frontend (`http://localhost:3000`).

---

### Option B: Manual Setup

#### 1. Seed Demo Synthetic Dataset
```bash
python scripts/seed_demo_data.py
```

#### 2. Run Backend API Server
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Run Frontend Web UI
```bash
cd frontend
npm install
npm run dev
```

---

## Access Points & Credentials
- **Frontend Web UI**: `http://localhost:3000` (or `http://localhost:5173`)
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`
- **Default Logins**:
  - **Administrator**: `admin@revenueagent.ai` / `Admin123!Pass`
  - **Revenue Manager**: `manager@revenueagent.ai` / `Manager123!Pass`
  - **Analyst**: `analyst@revenueagent.ai` / `Analyst123!Pass`

# Revenue_AI_Agent
# Hotel_Revenue_AI_Agent
