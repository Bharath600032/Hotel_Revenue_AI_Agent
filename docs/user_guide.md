# Hotel Autonomous Revenue AI Agent — User & Manager Guide

## Executive Overview
The **Hotel Autonomous Revenue AI Agent** is an enterprise-grade, AI-driven revenue management platform designed to automate hotel pricing, demand forecasting, competitor rate monitoring, and inventory optimization. The system operates using a single autonomous AI agent equipped with 22 specialized hotel revenue tools, backed by non-bypassable pricing guardrails and a mandatory human approval workflow for high-delta rate recommendations.

---

## Key Features & Capabilities

### 1. Dual Operating Modes
- **DEMO MODE**: Runs 100% out-of-the-box locally with zero external paid API keys. Uses local SQLite, simulated LLM provider (`MockLLMProvider`), and pre-seeded synthetic hotel data across 5 properties.
- **PRODUCTION MODE**: Connects to enterprise infrastructure (SQL Server 2022, Redis, ChromaDB, Claude 3.5 Sonnet / Gemini 1.5 Pro) for live multi-property hotel chains.

### 2. Autonomous Revenue AI Agent
- Natural language chat interface (`/assistant`) allowing revenue managers to ask natural questions like:
  - *"What is our occupancy forecast for next weekend in Goa?"*
  - *"Optimize prices for Deluxe Ocean View rooms from Oct 1 to Oct 10."*
  - *"Generate competitor price gap analysis report for Mumbai property."*

### 3. Non-Bypassable Pricing Guardrails
- **Minimum Price Floor**: Rates can never drop below the property's configured floor (e.g. ₹4,500).
- **Maximum Price Ceiling**: Rates can never exceed the property's ceiling (e.g. ₹35,000).
- **Daily Variation Cap**: Daily rate adjustments are hard-clamped to maximum $\pm 20\%$.
- **Human Approval Threshold**: Any recommended rate change exceeding $\pm 10\%$ is automatically locked into `Pending` status and routed to human revenue managers.

---

## Step-by-Step User Instructions

### Step 1: Authentication & Role Selection
1. Navigate to `http://localhost:3000` (or `http://localhost:8000/docs` for API testing).
2. Log in using pre-configured system roles:
   - **Administrator**: `admin@revenueagent.ai` / `Admin123!Pass`
   - **Revenue Manager**: `manager@revenueagent.ai` / `Manager123!Pass`
   - **Analyst**: `analyst@revenueagent.ai` / `Analyst123!Pass`

### Step 2: Revenue Dashboard Overview
- Access `/dashboard` to view real-time property KPIs:
  - **Occupancy %**: Total Sold Rooms / Total Physical Rooms.
  - **ADR (Average Daily Rate)**: Total Room Revenue / Total Sold Rooms.
  - **RevPAR (Revenue Per Available Room)**: Occupancy % $\times$ ADR.
  - **Pickup**: 1-day, 7-day, and 30-day net booking velocity.
  - **Competitor Rate Comparison**: Real-time market median rates and price gap index.

### Step 3: Interacting with AI Revenue Assistant
1. Navigate to `/assistant` in the navigation sidebar.
2. Select your target property from the hotel dropdown selector.
3. Type natural language instructions or select quick action prompts:
   - *"Analyze upcoming holiday weekend demand and propose rate strategy."*
   - *"Show competitor rates vs our current BAR rate for Deluxe Ocean View."*
4. View the agent's step-by-step tool execution trace, latency breakdown, and structured recommendation cards.

### Step 4: Reviewing & Approving Pending Recommendations
1. When the AI agent generates rate suggestions with $>10\%$ variation, they appear under **Pending Approvals**.
2. Click **Review Recommendation** to inspect:
   - Base Price vs Recommended Rate.
   - Percentage Change.
   - Natural Language AI Reasoning (e.g., *"Event uplift + 78% occupancy forecast"*).
3. Click **Approve** to commit the new rate immediately to room inventory, or click **Reject** with an optional override note.

### Step 5: Exporting Revenue & Financial Reports
1. Go to the Reports section or send request to `POST /api/v1/reports/revenue-export`.
2. Select target property and date range (e.g., 30-day forecast window).
3. Download formatted `.xlsx` workbook containing occupancy tabs, pickup tables, and competitor benchmark matrices.

---

## Role-Based Access Control (RBAC) Matrix

| User Role | View Dashboard | Execute AI Agent | Approve Rates | Manage Hotels & Users |
| :--- | :---: | :---: | :---: | :---: |
| **Administrator** | ✅ | ✅ | ✅ | ✅ |
| **Revenue Manager** | ✅ | ✅ | ✅ | ❌ |
| **Hotel Manager** | ✅ | ✅ | ✅ | ❌ |
| **Analyst** | ✅ | ✅ | ❌ | ❌ |
| **Read-Only User** | ✅ | ❌ | ❌ | ❌ |
