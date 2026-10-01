# Hotel Autonomous Revenue AI Agent — REST API Reference Guide

## Base URLs
- **Local Development**: `http://localhost:8000/api/v1`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`
- **ReDOC Documentation**: `http://localhost:8000/redoc`

---

## 1. Authentication & Identity Management

### `POST /api/v1/auth/login`
Authenticates a user and issues a JWT access token.
- **Request Body**:
  ```json
  {
    "email": "admin@revenueagent.ai",
    "password": "Admin123!Pass"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
    "token_type": "bearer",
    "expires_in": 28800,
    "user": {
      "user_id": 1,
      "email": "admin@revenueagent.ai",
      "full_name": "Chief Revenue Administrator",
      "role": "Administrator"
    }
  }
  ```

---

## 2. Hotel Property & Master Data APIs

### `POST /api/v1/hotels`
Creates a new hotel property.
- **Headers**: `Authorization: Bearer <JWT_TOKEN>`
- **Request Body**:
  ```json
  {
    "hotel_code": "HTL_GOA",
    "hotel_name": "Grand Azure Beach Resort",
    "city": "Goa",
    "country": "India",
    "total_rooms": 120,
    "min_price_floor": 4500.0,
    "max_price_ceiling": 35000.0,
    "max_daily_price_change_pct": 20.0,
    "require_approval_above_change_pct": 10.0
  }
  ```

### `GET /api/v1/hotels`
Returns all hotel properties accessible to the authenticated user.

---

## 3. Inventory & Ingestion APIs

### `GET /api/v1/inventory/{hotel_id}`
Returns daily room inventory, occupancy, and rates for a hotel within a date range.
- **Query Parameters**: `start_date` (YYYY-MM-DD), `end_date` (YYYY-MM-DD)

### `POST /api/v1/inventory/import`
Parses and imports reservation batches via CSV, Excel, or JSON.

---

## 4. AI Autonomous Agent API

### `POST /api/v1/agent/chat`
Submits a natural language query or instruction to the Single ReAct Revenue Agent.
- **Request Body**:
  ```json
  {
    "message": "Optimize prices for hotel 1 for the next 7 days.",
    "hotel_id": 1,
    "session_id": "sess-9921"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "response": "Based on 82% projected occupancy and competitor rates...",
    "hotel_id": 1,
    "tools_executed": ["get_hotel_performance", "generate_dynamic_price_recommendations"],
    "recommendations": [...]
  }
  ```

---

## 5. Human-in-the-Loop Approval APIs

### `GET /api/v1/approvals/pending`
Returns all pending price recommendations requiring human approval ($>10\%$ variation).

### `POST /api/v1/approvals/{recommendation_id}/action`
Approves or rejects a pending price recommendation.
- **Request Body**:
  ```json
  {
    "action": "APPROVE",
    "override_price": 9200.0,
    "notes": "Approved for upcoming festival weekend."
  }
  ```

---

## 6. Reports & Observability APIs

### `POST /api/v1/reports/revenue-export`
Generates formatted `.xlsx` revenue spreadsheets.

### `GET /health` | `GET /readiness` | `GET /liveness`
Returns system health, database readiness, and liveness probes.
