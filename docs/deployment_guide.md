# Hotel Autonomous Revenue AI Agent — Production Deployment Guide

## 1. System Requirements & Prerequisites

| Subsystem | Development / DEMO Mode | Enterprise Production Mode |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11, macOS, Linux | Ubuntu 22.04 LTS / RHEL 9 / Windows Server 2022 |
| **Python** | Python 3.11+ | Python 3.11+ |
| **Node.js** | Node.js 18 LTS | Node.js 18 LTS |
| **Database** | SQLite (Embedded) | Microsoft SQL Server 2022 / Azure SQL Database |
| **Cache / Queue** | In-Memory Memory Cache | Redis 7.0+ |
| **Vector DB** | Local ChromaDB | ChromaDB Service / Pinecone / Azure AI Search |
| **LLM Provider** | `MockLLMProvider` (Local Offline) | Anthropic Claude 3.5 Sonnet / Google Gemini 1.5 Pro |

---

## 2. Quick Start: Local DEMO MODE Deployment

DEMO MODE requires **zero paid external API keys** and runs completely offline.

### Step 1: Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-org/hotel-revenue-ai-agent.git
cd hotel-revenue-ai-agent/backend

python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Seed Demo Synthetic Dataset
```bash
python ../scripts/seed_demo_data.py
```
This populates 5 hotel properties, 365 inventory dates, competitor pricing feeds, local events, and national holidays.

### Step 3: Launch FastAPI Backend Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend API will be accessible at `http://localhost:8000`.

### Step 4: Launch React Frontend Application
Open a second terminal window:
```bash
cd hotel-revenue-ai-agent/frontend
npm install
npm run dev
```
Frontend web application will be accessible at `http://localhost:3000`.

---

## 3. Docker Compose Deployment

To deploy both backend and frontend using containerization:

```bash
cd hotel-revenue-ai-agent
docker-compose up -d --build
```

Verify running containers:
```bash
docker-compose ps
```

- **Frontend Application**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000/docs`

---

## 4. Enterprise PRODUCTION MODE Deployment

### Step 1: Environment Variables Configuration
Create `/etc/hotel-revenue/app.env` or `.env`:
```env
APP_MODE=PRODUCTION
LOG_LEVEL=INFO

# Security
JWT_SECRET_KEY=prod-super-secret-key-must-be-at-least-64-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Production Database (SQL Server 2022)
DATABASE_URL=mssql+pyodbc://sa:YourStrongPassword123!@sqlserver2022:1433/HotelRevenueDB?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes

# Redis Caching
REDIS_URL=redis://redis-cluster:6379/0

# LLM API Credentials
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-...

# Pricing Guardrail Rules
GLOBAL_MIN_PRICE_FLOOR=2000.0
GLOBAL_MAX_PRICE_CEILING=50000.0
GLOBAL_MAX_DAILY_CHANGE_PCT=20.0
GLOBAL_REQUIRE_APPROVAL_PCT=10.0
```

### Step 2: Running System Readiness Probe
```bash
curl -f http://localhost:8000/readiness
```

---

## 5. Troubleshooting & FAQ

### Issue 1: Database Locking in SQLite (DEMO Mode)
- **Symptom**: `sqlite3.OperationalError: database is locked`
- **Solution**: SQLite handles single-writer concurrency. Ensure WAL mode is active or switch `DATABASE_URL` to PostgreSQL / SQL Server for heavy parallel testing.

### Issue 2: Tool Latency Spikes
- **Symptom**: Agent response takes > 3 seconds.
- **Solution**: Ensure Redis caching is enabled for competitor scraping tools and SARIMAX model parameters are cached.
