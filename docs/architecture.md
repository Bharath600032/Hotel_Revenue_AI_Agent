# Hotel Autonomous Revenue AI Agent — Technical Architecture Specification

## 1. System Philosophy & Architecture Principles

The **Hotel Autonomous Revenue AI Agent** is architected as a **Single Autonomous AI Agent** equipped with 22 specialized hotel domain tools, rather than a fragmented multi-agent mesh. This ensures deterministic control flow, transparent auditability, single-point tool selection tracing, and zero inter-agent communication latency.

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
                    +-----------------------------------------+
```

---

## 2. Core Subsystems

### 2.1 Single ReAct Agent Orchestrator & Memory Manager
- **ReAct Loop**: Iterative **Thought $\rightarrow$ Action (Tool Call) $\rightarrow$ Observation $\rightarrow$ Synthesis** cycle.
- **3-Tier Memory Manager**:
  1. *Short-Term Memory*: Active user session state and message history buffer (up to 20 messages).
  2. *Operational Memory*: Hotel master parameters, active rate plans, and room inventory baselines.
  3. *RAG Strategy Context*: Vector similarity search against hotel revenue policy documents, cancellation rules, and pricing playbooks.

### 2.2 22 Domain Tool Suite

| # | Tool Name | Category | Description |
|---|---|---|---|
| 1 | `get_hotel_performance` | Revenue Metrics | Calculates Occupancy %, ADR, RevPAR, TRevPAR |
| 2 | `get_pickup_analytics` | Booking Pace | Calculates 1d, 7d, 14d, 30d pickup velocity |
| 3 | `get_occupancy_forecast` | Demand Forecasting | Generates 30-day occupancy predictions |
| 4 | `get_competitor_rate_comparison` | Market Intel | Fetches competitor median, price gap %, rank |
| 5 | `get_event_demand_impact` | External Signals | Calculates event attendance & holiday multipliers |
| 6 | `get_weather_impact` | External Signals | Retrieves weather forecasts and demand impact |
| 7 | `generate_dynamic_price_recommendations` | Dynamic Pricing | Computes optimal rates across date ranges |
| 8 | `validate_pricing_guardrails` | Compliance | Enforces min/max floors & daily variation limits |
| 9 | `submit_approval_request` | Approval Workflow | Routes rate changes >10% to human managers |
| 10 | `approve_price_recommendation` | Approval Workflow | Commits approved price recommendations |
| 11 | `reject_price_recommendation` | Approval Workflow | Rejects recommendation with user override notes |
| 12 | `query_revenue_knowledge_base` | RAG Search | Vector search across revenue policy documents |
| 13 | `import_reservation_data` | Data Import | Parses and ingests CSV/JSON reservation feeds |
| 14 | `update_room_inventory_rate` | Inventory | Updates room inventory rate directly |
| 15 | `get_rate_plan_breakdown` | Pricing | Returns meal plan & multiplier configurations |
| 16 | `calculate_channel_yield` | Analytics | Computes net revenue contribution by channel |
| 17 | `detect_pricing_anomalies` | Market Intel | Identifies outlier competitor rate spikes |
| 18 | `generate_excel_revenue_report` | Reporting | Generates styled .xlsx spreadsheet exports |
| 19 | `get_audit_logs` | Security & Audit | Retrieves immutable system audit logs |
| 20 | `evaluate_forecast_accuracy` | Forecasting | Calculates MAE, RMSE, MAPE forecast error |
| 21 | `get_guest_segmentation` | Analytics | Analyzes corporate vs leisure booking mix |
| 22 | `get_system_health_status` | Observability | Returns sub-component health & readiness |

---

## 3. Mathematical Foundations & Guardrail Logic

### 3.1 Revenue Metrics
$$\text{Occupancy \%} = \frac{\text{Rooms Sold}}{\text{Total Available Rooms}} \times 100$$

$$\text{ADR} = \frac{\text{Total Room Revenue}}{\text{Rooms Sold}}$$

$$\text{RevPAR} = \text{Occupancy \%} \times \text{ADR} = \frac{\text{Total Room Revenue}}{\text{Total Available Rooms}}$$

### 3.2 Dynamic Rate Clamping Equation
For any recommended raw rate $R_{\text{raw}}$, current rate $R_{\text{curr}}$, floor $F$, ceiling $C$, and daily change limit $\delta_{\text{max}} = 0.20$:

$$R_{\text{bounded\_change}} = \text{clamp}\left(R_{\text{raw}}, R_{\text{curr}} \times (1 - \delta_{\text{max}}), R_{\text{curr}} \times (1 + \delta_{\text{max}})\right)$$

$$R_{\text{final}} = \text{clamp}\left(R_{\text{bounded\_change}}, F, C\right)$$

$$\text{Requires Approval} = \begin{cases} \text{True} & \text{if } \left|\frac{R_{\text{final}} - R_{\text{curr}}}{R_{\text{curr}}}\right| > \theta_{\text{approval}} \text{ (e.g., 10\%)} \\ \text{False} & \text{otherwise} \end{cases}$$

---

## 4. Database Schema Structure
The system utilizes 20 SQLAlchemy ORM entities:
`users`, `hotels`, `room_types`, `rate_plans`, `room_inventory`, `reservations`, `daily_booking_snapshots`, `historical_rates`, `competitor_hotels`, `competitor_rates`, `holidays`, `events`, `weather`, `forecasts`, `price_recommendations`, `agent_runs`, `agent_tool_calls`, `model_registry`, `feedback`, `audit_logs`.
