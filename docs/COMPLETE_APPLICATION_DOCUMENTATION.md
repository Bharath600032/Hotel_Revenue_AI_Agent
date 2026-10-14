# Hotel Autonomous Revenue AI Agent (KESH) — Comprehensive System Documentation

---

## 1. Executive Summary & Application Overview

The **Hotel Autonomous Revenue AI Agent** (codenamed **KESH**) is a production-grade, multi-tenant revenue management platform designed for autonomous hotel pricing, demand forecasting, real-time market intelligence, and conversational assistance.

Traditional hotel Revenue Management Systems (RMS) are static rule engines requiring manual intervention. In contrast, this application implements an **Autonomous ReAct Agent Orchestrator** backed by a **3-Tier Memory Manager**, **Hybrid Semantic Vector RAG Engine**, **Multi-Horizon ML Forecasting**, and **Live Parallel Web Scraping of OTA Channels**.

### Key Value Propositions
- **Autonomous Pricing with Hard Safety Guardrails**: Dynamically adjusts daily rates based on 5 core signals while enforcing strict price floors, ceilings, and ±20% daily fluctuation clamps.
- **Explainable Revenue Recommendations**: Every price change traces exact contributing factors (competitor gap, pace velocity, city events, weather, historical pickup).
- **Zero-Latency Single-Agent Architecture**: Replaces fragile multi-agent meshes with a deterministic, tool-augmented single agent (KESH) capable of calling 22+ domain tools.
- **Multi-Tenant Property Auto-Provisioning**: Automatically isolates memory, vector document stores, inventory, and competitor sets per property.
- **Enterprise-Ready Auditing & RBAC**: Strict role-based permissions (Super Admin, Administrator, Revenue Manager, Analyst, Read-only) with immutable audit logging.

---

## 2. End-to-End System Architecture

```
                    +-----------------------------------------+
                    |             React Frontend              |
                    |   (Vite, React 18, Tailwind CSS, UI)    |
                    +--------------------+--------------------+
                                         |
                                    HTTP / REST
                                         v
                    +-----------------------------------------+
                    |           FastAPI Web Gateway           |
                    |  (Security Headers, JWT RBAC, Auditing) |
                    +--------------------+--------------------+
                                         |
                                         v
                    +-----------------------------------------+
                    |    Single Autonomous AI Orchestrator   |
                    |     (ReAct Loop, Memory Manager, RAG)   |
                    +----+---------------+---------------+----+
                         |               |               |
       +-----------------+               |               +-----------------+
       |                                 v                                 |
+------+------------------+   +----------+-----------+   +-----------------+--------+
| 22 Domain Tools Registry|   | Dynamic Pricing Engine|   |  ML Forecasting Pipeline|
| (Calculators, Scraping) |   | (Multi-Signal Logic) |   | (SARIMAX, XGBoost, Naive)|
+------+------------------+   +----------+-----------+   +-----------------+--------+
       |                                 |                                 |
       +-----------------+               |               +-----------------+
                         |               v               |
                    +----+---------------+---------------+----+
                    |  Deterministic Guardrails Service       |
                    | (Min/Max Floors, ±20% Daily Clamp)      |
                    +--------------------+--------------------+
                                         |
                                         v
                    +-----------------------------------------+
                    |        SQL Engine / Persistence         |
                    |  (SQLite / SQL Server 2022 + Audit Logs)|
                    +--------------------+--------------------+
```

---

## 3. Core Modules & Subsystems

### 3.1 Single ReAct Agent Orchestrator & Memory Manager
- **File**: `backend/app/agents/orchestrator.py`
- **Concept**: Employs an iterative **Thought -> Action (Tool Call) -> Observation -> Synthesis** execution cycle.
- **3-Tier Memory Architecture**:
  1. **Short-Term Memory**: Holds rolling multi-turn conversation dialogue (last 20 turns) to resolve contextual and follow-up queries (e.g., *"give me the list"* or *"who are our rivals?"*).
  2. **Operational Memory**: Real-time property specifications, total room allocations, active rate plans, and city baselines loaded directly from the database.
  3. **RAG Semantic Memory**: Vector similarity retrieval from scraped official hotel website pages and uploaded SOP/strategy documents.
- **Core Principles Enforced**:
  - *Accuracy First*: Strict fallback to live DB entities over generative guesses.
  - *Strict Temporal Accuracy*: Precise calendar boundary filtering (e.g., querying November strictly bounds dates between Nov 1 and Nov 30).
  - *Scope Isolation*: Distinguishes public holidays from city festivals and conferences.

### 3.2 22+ Domain Tool Suite
All agent operations execute through a unified tool registry (`backend/app/tools/registry.py`):

| Tool Name | Category | Primary Function |
|---|---|---|
| `get_hotel_profile` | Property Core | Retrieves total rooms, star rating, city, floor/ceiling rates |
| `get_room_types` | Inventory | Fetches room categories, master allocations, and base tariffs |
| `get_inventory` | Inventory | Date-range availability, sellable counts, out-of-order rooms |
| `get_reservations` | Booking Pace | Ingested reservations, check-in dates, booking status |
| `get_booking_pace` | Booking Pace | 1d, 3d, 7d, 14d, and 30d pickup pace velocity |
| `calculate_occupancy` | Metrics | Occupancy percentage calculation for stay dates |
| `calculate_adr` | Metrics | Average Daily Rate computation across stay intervals |
| `calculate_revpar` | Metrics | Revenue Per Available Room calculation |
| `get_events_holidays` | Signals | Temporal & scope-aware search for festivals and holidays |
| `get_competitor_rates` | Market Intel | Live competitor rates, market median, price gap index |
| `get_weather` | Signals | Temperature, precipitation, and demand multiplier factors |
| `run_demand_forecast` | Forecasting | Projected occupancy % and target RevPAR trajectory |
| `calculate_pricing_recommendation` | Dynamic Pricing | 5-stage rate recommendation with explainable reasons |
| `validate_price_guardrails` | Compliance | Enforces floors, ceilings, and ±20% change clamps |
| `request_human_approval` | Workflow | Flags rate shifts >10% for manager sign-off |
| `calculate_group_displacement` | Group Booking | Calculates breakeven rates and net displacement impact |
| `get_los_restrictions` | Length of Stay | MLOS (Min Length of Stay), CTA, CTD restrictions |
| `calculate_trevpar_analytics` | Non-Room | Total RevPAR including F&B, spa, and ancillary revenue |
| `generate_ancillary_upsell_packages` | Upsell | Dynamic bundles (Airport Transfer, Spa, Buffet) |
| `dispatch_multi_channel_alert` | Alerts | Real-time Slack, Webhook, and In-App notifications |
| `push_two_way_channel_rates` | Channel Sync | 2-way rate parity push to OTAs (Booking, Agoda, STAAH) |
| `run_multi_agent_swarm_consensus` | Multi-Agent | Consensus pricing across 4 specialized agent roles |

### 3.3 Hybrid Semantic Vector RAG Engine & Crawler
- **Files**: `backend/app/rag/vector_store.py`, `backend/app/rag/embeddings.py`, `backend/app/rag/website_scraper.py`
- **Deterministic Semantic Hashing & Concept Clusters**:
  Instead of unweighted character hashing, the embedding engine projects word tokens into a 384-dimensional normalized vector space with dedicated concept clusters:
  - `amenities` *(pool, gym, wifi, concierge, spa, valet)*
  - `dining` *(restaurant, buffet, cuisine, breakfast)*
  - `rooms` *(deluxe, suite, king, inventory, capacity)*
  - `pricing` *(rate, tariff, competitor, median, floor, ceiling)*
  - `holidays` *(national holiday, observance, Diwali, Pongal, Christmas)*
  - `policies` *(SOP, cancellation, check-in, deposit, guardrails)*
- **Hybrid Similarity Algorithm**:
  `Score = 0.50 * CosineSimilarity + 0.35 * LexicalOverlap + ConceptBoost + PropertyAffinity`
  - Cross-topic penalties filter out irrelevant records (e.g., public holidays are penalized when querying hotel facilities).
- **Recursive Web Crawler**: Crawls hotel website roots and sublinks (Rooms, Dining, Facilities, Contact), vectorizing chunks and associating them with the active property.

### 3.4 5-Stage Autonomous Pricing Pipeline
- **File**: `backend/app/pricing/engine.py`

```
[Base Room Rate]
       │
       ▼
[Stage 1: Occupancy & Pace Adjustment] (+5% to +25% based on pace thresholds)
       │
       ▼
[Stage 2: Competitor Positioning] (Maintains target price gap vs. market median)
       │
       ▼
[Stage 3: Event & Holiday Multipliers] (Demand surge factors e.g., 1.40x Diwali)
       │
       ▼
[Stage 4: Weather & Macro Modifiers] (Depressed demand on heavy rain alerts)
       │
       ▼
[Stage 5: Deterministic Safety Clamping]
       ├── Lower Floor: max(Base * 0.80, Hotel.min_price_floor)
       ├── Upper Ceiling: min(Base * 1.20, Hotel.max_price_ceiling)
       └── Daily Clamping: ±20% max single-day rate change
```

- **Approval Guardrails**: Rate changes exceeding 10% automatically trigger `requires_approval = True`, routing to the human manager's review queue.

### 3.5 Live Multi-Threaded Competitor Intelligence
- **File**: `backend/app/competitors/scraper.py`
- **Live OTA Scraping**: Concurrently queries Google Hotel Search for active property rivals across major OTAs (Booking.com, MakeMyTrip, Agoda, Goibibo, Expedia).
- **Metrics Computed**:
  - `Market Median Rate`
  - `Price Gap Percentage`: `(Rate_hotel - Rate_median) / Rate_median * 100`
  - `OTA Parity Integrity`: Detects rate discrepancies across distribution channels.

### 3.6 Multi-Horizon Demand & Price Forecasting
- **File**: `backend/app/forecasting/engine.py`
- **Dual Forecasting Horizons**:
  1. **Room Demand Horizon**: Projected occupancy %, pickup velocity, and corporate midweek vs. weekend peak indicators.
  2. **Competitor Price Forecasting**: Multi-day horizons (7, 14, and 30 days) benchmarking the main property rate against individual named competitor trajectories.

---

## 4. Database Schema & Data Models

The system supports SQLite (development/demo) and Microsoft SQL Server 2022 / PostgreSQL (enterprise).

- **Hotels (`hotels`)**: Master hotel properties with city, star rating, total room capacity, price floors, ceilings, and currency.
- **Room Types (`room_types`)**: Room categories, baseline rates, allocation counts, and occupancy limits.
- **Daily Inventory (`inventory`)**: Daily stay date inventory tracking total, available, sellable, and booked rooms.
- **Reservations (`reservations`)**: Ingested reservation records with check-in, check-out, rate, and status.
- **Competitor Hotels & Rates (`competitor_hotels`, `competitor_rates`)**: Active rival set with OTA source, timestamp, and rate history.
- **Pricing Recommendations (`pricing_recommendations`)**: Generated dynamic tariffs, reasoning trace, confidence score, and approval flags.
- **Agent Runs & Tool Calls (`agent_runs`, `agent_tool_calls`)**: Complete execution telemetry and execution latencies.
- **Audit Logs (`audit_logs`)**: Immutable security trail recording actor, action, old value, and new value.

---

## 5. REST API Specifications

The backend exposes an interactive OpenAPI specification accessible at `/docs` or `/redoc`:

### 5.1 Authentication & Property Selection
- `POST /api/v1/auth/login`: Authenticates user credentials and issues a signed JWT bearer token.
- `GET /api/v1/hotels/`: Lists hotels assigned to the authenticated user.
- `GET /api/v1/hotels/{id}`: Retrieves profile, room categories, and price guardrails for a specific hotel.

### 5.2 AI Assistant & Multi-Agent Swarm
- `POST /api/v1/agent/chat`: Primary natural language interface executing intent routing, 22-tool execution, and explainable responses.
- `GET /api/v1/agent/runs`: Retrieves execution logs, latency metrics, and tool execution traces.
- `POST /api/v1/agent-swarm/evaluate`: Runs 4-agent consensus (Macro, Micro, Comp-Intel, Risk-Guardrail).

### 5.3 Forecasting & Pricing Automation
- `GET /api/v1/forecasts/occupancy`: Returns 30-day projected occupancy pace.
- `GET /api/v1/forecasts/price`: Returns 7, 14, and 30-day price forecast trajectories for main and competitor properties.
- `POST /api/v1/pricing/recommendations`: Triggers the 5-stage pricing engine over a date range.
- `POST /api/v1/pricing/recommendations/{id}/approve`: Approves a flagged recommendation and commits rate to inventory.

### 5.4 Competitor Intelligence & Market Intel
- `GET /api/v1/competitors/`: Lists active competitors in the property's competitive set.
- `POST /api/v1/competitors/scrape-live`: Triggers multi-threaded live OTA scraper across Google Hotel Search.
- `GET /api/v1/competitors/benchmark`: Fetches market median, price gap index, and channel parity.

### 5.5 RAG Knowledge Base
- `POST /api/v1/rag/search`: Hybrid semantic vector search over hotel strategy documents and crawled website sublinks.
- `POST /api/v1/rag/documents/upload`: Vectorizes and stores SOP/policy documents.
- `POST /api/v1/rag/documents/scrape-url`: Crawls and indexes official hotel websites.
- `POST /api/v1/rag/sync`: Synchronizes live database entities directly into vector space.

---

## 6. Frontend Architecture & User Interface

Built with **React 18**, **TypeScript**, **Vite**, and **Tailwind CSS**, featuring dark-mode glassmorphism, glowing accents, and micro-animations.

### Page Directory Overview

| Page Component | Path | Primary Purpose |
|---|---|---|
| `Dashboard.tsx` | `/` | Executive overview: RevPAR, ADR, Occupancy pace, live rate ticker |
| `Assistant.tsx` | `/assistant` | KESH AI Assistant with tool badge traces and structured recommendations |
| `Forecasting.tsx` | `/forecasting` | 7/14/30d interactive pricing graphs and room demand horizon |
| `Pricing.tsx` | `/pricing` | Dynamic rate matrix, guardrail status, approval workflow queue |
| `Competitors.tsx` | `/competitors` | Live OTA rate scraper, price gap benchmark, and competitor management |
| `RAG.tsx` | `/rag` | Semantic similarity tester with structured points formatting and website crawler |
| `AgentSwarmArchitecture.tsx` | `/swarm` | 4-agent consensus weights, confidence meters, and deliberation logs |
| `GroupDisplacement.tsx` | `/group-displacement` | Group booking evaluator with breakeven rates and counter-offers |
| `OTAChannelManager.tsx` | `/channel-manager` | 2-way PMS & OTA sync status and rate distribution monitor |
| `ExecutiveReportsBI.tsx` | `/executive-bi` | Automated executive PDF generation and Excel/PowerBI dataset exports |

---

## 7. Security, Auditing & Role-Based Access Control (RBAC)

### 7.1 Role Hierarchy & Permissions
- **Super Administrator**: Full multi-tenant configuration, global user management, system audit logs, and developer API key creation.
- **Administrator**: Property creation, hotel profile updates, competitive set management, and strategy ingestion.
- **Revenue Manager**: Pricing recommendation approval, guardrail overrides, demand forecast execution, and channel rate pushes.
- **Pricing Analyst**: Read-access to all metrics, draft pricing generation, and report exports.
- **Read-only User**: View-only access to dashboards, forecasting graphs, and event calendars.

### 7.2 Security Hardening
- **JWT Authentication**: Signed bearer tokens with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Password Security**: Passlib with Bcrypt cryptographic salt hashing.
- **Multi-Tenant Property Isolation**: In every API route, `verify_hotel_access` verifies the user's assigned hotel permissions before returning property data.
- **Immutable Audit Logging**: Every critical action (rate approvals, overrides, crawling, manual pricing updates) writes an audit record with timestamp, user ID, IP address, old value, and new value.

---

## 8. Deployment & Operational Runbooks

### 8.1 Single-Command Quick Start
- **Windows Batch**:
  ```cmd
  run_demo.bat
  ```
- **Windows PowerShell**:
  ```powershell
  .\run_demo.ps1
  ```
- **Docker Compose**:
  ```bash
  docker-compose up --build
  ```

### 8.2 Default Demo Credentials
- **Super Admin**: `superadmin@cuteorange.in` / `SuperAdmin123!`
- **Revenue Manager**: `manager@revenueagent.ai` / `Manager123!Pass`
- **Analyst**: `analyst@revenueagent.ai` / `Analyst123!Pass`

### 8.3 Operational Health Checks
- **Liveness Probe**: `GET /health` returns `{ "status": "healthy", "service": "Hotel Autonomous Revenue AI Agent", "version": "1.0.0" }`
- **Tool Readiness**: Verified via `single_agent_orchestrator.run(db, user_message="status")`.
