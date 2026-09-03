# PAHIROWATCH (पहिरोवाच)
### *"Detect the slope. Protect the road. Alert before the disaster."*

> **Startup Innovation Hackathon Vol. III:** *"Agentic AI in Nepal’s Digital Age Transformation"*  
> **Mission:** Build an autonomous landslide-risk monitoring and operational response agent specifically for high-risk mountain road corridors in Nepal.

---

## 1. Executive Summary

**PahiroWatch** is an autonomous geospatial response agent engineered for Nepal's critical lifeline highway corridors. It is **not** an opaque prediction oracle or passive dashboard; rather, it is an **operational decision-support system** that continuously investigates multi-source environmental signals, reasons over physical hazard indicators, synthesizes evidence-backed incident reports, and enforces an unbypassable **Human Checkpoint** before any official emergency action is dispatched.

---

## 2. The Problem

Every monsoon season (June–September), landslides sever Nepal's vital highway arteries, causing loss of life, stranding thousands of travelers, and halting national freight. Current municipal disaster offices face two fatal extremes:
1. **Infrequent Manual Reports:** Warning notices arrive only *after* mass debris has collapsed onto the highway.
2. **False Alarm Fatigue:** Generic regional warnings lack hyper-local slope, drainage, and road proximity context, leading operators to ignore them.

---

## 3. The Specific User

- **Designated Operator:** **Ramesh, Municipal Disaster Management Officer** & Road Operations Coordinator.
- **Administrative Jurisdiction:** Ichhyakamana Rural Municipality (Wards 4, 5, and 6), Chitwan District, Bagmati Province.
- **Operational Need:** *"Which highway segment needs my emergency inspection crew right now, why, how confident are we, and what action should I authorize?"*

*(Note: Ramesh is a concrete synthetic persona designed specifically for this operational decision-support demonstration).*

---

## 4. Why Nepal? (The Pilot Corridor)

PahiroWatch focuses specifically on the **Narayanghat–Mugling Highway (National Highway 05)**, spanning the steep Trishuli river canyon (KM 24 to KM 38: Kalikhola, Jalbire, Charkilo, Kurintar, Mugling). 
- This corridor connects Kathmandu and Pokhara to the southern plains and handles over 20,000 vehicles daily.
- It suffers from fractured phyllite/schist bedrock, intense monsoon cloudbursts, and fragile engineered cut-slopes.

---

## 5. What the Agent Does

Rather than passively waiting for user queries, PahiroWatch:
1. **Autonomously Wakes:** Triggered by scheduled cycles (every 30 mins) or environmental precipitation thresholds (>100mm/24h).
2. **Investigates via Tools:** Dispatches bounded queries to DHM rainfall telemetry, SRTM topographic slope models, Copernicus optical change detectors, and OpenStreetMap highway networks.
3. **Recalls Historical Memory:** Inquires SQLite cross-run state to evaluate ground saturation history and past unresolved slides.
4. **Calculates Deterministic Risk:** Aggregates multi-source metrics into an honest 0–100 risk score and transparent confidence index.
5. **Enforces Human Gate:** If high risk is detected, generates a bilingual incident report and halts execution until operator Ramesh explicitly approves or rejects the action.
6. **Dispatches Alerts:** Only after human authorization, sends simulated emergency broadcasts, official Nepali municipal advisories, and ultra-compact Low-Bandwidth SMS payloads (<160 chars).

---

## 6. Agent Architecture

```
                       [SCHEDULED TIMER / RAINFALL THRESHOLD TRIGGER]
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     PAHIROWATCH AGENT     │
                               │   Bounded Loop (<=10)     │
                               └─────────────┬─────────────┘
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               ▼                             ▼                             ▼
       [TOOL 1: Weather]             [TOOL 2: Terrain]            [TOOL 3: Satellite]
      DHM / Open-Meteo              SRTM 30m DEM Slope           Sentinel-2 Change
               │                             │                             │
               └─────────────────────────────┼─────────────────────────────┘
                                             │
               ┌─────────────────────────────┴─────────────────────────────┐
               ▼                                                           ▼
       [TOOL 4: Exposure]                                         [TOOL 5: Memory]
       OSM Highway Network                                      SQLite Cross-Run DB
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ DETERMINISTIC RISK ENGINE │
                               │  0-100 Score + Confidence │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │  HUMAN CHECKPOINT GATE    │
                               │  Operator Ramesh Reviews  │
                               └─────────────┬─────────────┘
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
                 [APPROVED]                                    [REJECTED]
                       │                                           │
         ┌─────────────┴─────────────┐                     ┌───────┴───────┐
         ▼                           ▼                     ▼               ▼
 [TOOL 6: Incident]          [TOOL 8: Alert]          [Record Notes]  [Close Cycle]
 SQLite Persistent DB      Bilingual / Low-BW SMS
```

---

## 7. Key Agentic Signals Demonstrated

| Agentic Quality | How PahiroWatch Demonstrates It |
|---|---|
| **Goal-Driven Behavior** | The agent decomposes a high-level operational goal into purposeful investigative subgoals instead of following a brittle linear script. |
| **Tool Calling** | Uses 8 independent tools covering atmospheric, topographic, remote sensing, and infrastructure domains. |
| **Bounded Multi-Step Loop** | Never enters an infinite loop; strictly capped at 10 tool iterations per cycle with internal progress tracking. |
| **Persistent Memory** | Run #002 queries Run #001's assessments and human approval outcomes from SQLite to adjust risk weights for prior unresolved incidents. |
| **Autonomous Trigger** | Operates on periodic scheduling and precipitation threshold triggers (>100mm/24h). |
| **Consequential Action** | Issues emergency road-crew dispatch orders and prepares bilingual broadcast alerts. |
| **Human Checkpoint** | **Hard gate in backend code:** `send_alert()` fails closed with `AgentSecurityError` unless `approval_status == 'APPROVED'`. |
| **Honest Agent Trace** | Real-time stream detailing timestamped thoughts, tool inputs, raw payloads, confidence penalties, and execution costs. |

---

## 8. Tool Registry

1. `get_weather_rainfall(location, time_window)`: DHM rainfall telemetry (1h, 6h, 24h, 72h).
2. `get_terrain_risk(location)`: SRTM/ALOS DEM elevation, slope degrees, and aspect.
3. `get_satellite_change(location, before_date, after_date)`: Sentinel-2 optical spectral difference and cloud contamination index.
4. `get_road_exposure(location)`: OpenStreetMap distance to lifeline highway, bridges, and settlements.
5. `get_incident_memory(location)`: SQLite historical recall of previous slides and unresolved events.
6. `create_incident_report(summary_en, summary_ne, action)`: Records active hazard incident in the database.
7. `request_human_approval(prompt, action_proposed)`: Halts automated execution at the human checkpoint.
8. `send_alert(channel)`: Dispatches bilingual and low-bandwidth alerts (*strictly protected by human approval gate*).

---

## 9. Persistent SQLite Memory Schema

- `locations`: Monitored highway sectors, coordinates, baseline slope, and critical infrastructure.
- `monitoring_runs`: Run execution logs, trigger types, step counts, token usage, latency, and cost in NPR.
- `observations`: Immutable raw tool outputs tagged with data freshness and provenance.
- `risk_assessments`: Deterministic component breakdown (rainfall, terrain, satellite, exposure, history).
- `incidents`: Escalated operational records requiring human review.
- `approvals`: Audit trail of operator decisions, notes, and authorization timestamps.
- `actions`: Dispatched outbound alerts and simulated SMS records.
- `agent_memory`: Cross-run associative memory and historical event counts.
- `agent_traces`: Real-time execution events for auditability.

---

## 10. Autonomous Triggers

1. **Scheduled Interval Monitor:** Simulates a periodic 30-minute / hourly background surveillance job.
2. **Environmental Threshold Trigger:** If DHM 24h precipitation exceeds 100mm, the agent automatically awakens to assess corridor vulnerability.
3. **On-Demand Dispatch:** Operators can trigger immediate cycles via "Run Monitoring Cycle Now".

---

## 11. The Human Checkpoint (Mandatory Safety Gate)

PahiroWatch enforces a strict safety boundary: **the AI never directly declares a public disaster or closes a highway autonomously.**

When the risk engine flags a High or Critical hazard:
1. The agent creates a `PENDING_APPROVAL` incident record.
2. The UI presents Ramesh with the complete multi-sensor evidence breakdown, plain-language reasoning, and recommended action.
3. Ramesh has three options:
   - `[APPROVE ACTION & DISPATCH ALERT]`
   - `[REJECT / SUPPRESS]`
   - `[REQUEST MORE EVIDENCE]`
4. If an agent attempts to execute `send_alert()` without approval, the tool **fails closed** and throws an uncatchable `AgentSecurityError`.

---

## 12. "Bad Day" Resilience & Graceful Degradation

During severe Himalayan monsoons, sensors and networks fail. PahiroWatch implements explicit graceful degradation:

- **Case 1: Weather Telemetry Failure:** Implements exponential backoff retry. Falls back to cached data, flags it as `STALE`, reduces confidence by 0.15, and continues.
- **Case 2: Satellite Cloud Contamination / API Outage:** Detects heavy monsoon clouds (>70% cover) or gateway timeouts. Continues using rainfall + terrain + road exposure. Honestly drops confidence to 0.50–0.70 and explicitly informs the operator:  
  *"Satellite confirmation is unavailable. Terrestrial rainfall and steep terrain remain sufficient to recommend inspection, but confidence is reduced."*
- **Case 3: LLM Outage / Timeout:** The system immediately fails over to the **Deterministic Safety Fallback Engine**, displaying `"RESILIENCE MODE ACTIVE"`. Operational safety continues without interruption.
- **Case 4: Conflicting Evidence:** If severe rain occurs on gentle terrain (<15°), the agent detects contradictory evidence, flags potential localized flooding rather than landslide shear, and suppresses false alarms.

---

## 13. Data Provenance: Real vs. Synthetic vs. Mocked

In accordance with strict disaster-response ethics, PahiroWatch never fakes live data:

| Component | Status | Provenance & Source Notes |
|---|---|---|
| **Highway Corridor Cadastre** | **REAL** | Narayanghat–Mugling Highway (NH05) alignment, wards, and settlements. |
| **Topographic DEM & Slope** | **CALIBRATED SYNTHETIC** | Pre-calculated from SRTM 30m / ALOS World 3D DEM profile for Ichhyakamana. |
| **Rainfall Observations** | **CALIBRATED SYNTHETIC** | Calibrated against DHM Trishuli river basin monsoon thresholds (>140mm cloudburst curves). |
| **Satellite Optical Change** | **SYNTHETIC DEMO ADAPTER** | Simulates Sentinel-2 MSI band ratios (B4/B8/B11) with visible label: *"Demo data — replace with live Sentinel/Copernicus pipeline."* |
| **SQLite Memory & Audit** | **REAL** | Real local database with WAL mode and cross-run persistence. |
| **Outbound SMS & Radio** | **SIMULATED** | Validated payload formatting; simulated dispatch channel. |

---

## 14. Model Usage & Cost Accounting

- **LLM Reasoning:** OpenAI-compatible model endpoint (configured via `HACKATHON_KEY` and `OPENAI_API_BASE` in `.env`).
- **Token & Cost Tracking:** Every run calculates prompt tokens, completion tokens, latency (ms), and estimated cost in **Nepali Rupees (NPR)** (exchange rate: 1 USD ≈ 135 NPR).
- **Average Cost Per Run:** ~0.024 NPR (~$0.00018 USD), demonstrating high economic scalability for cash-constrained rural municipalities.

---

## 15. How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js v18+ and npm

### 1. Clone & Configure Environment
```bash
git clone https://github.com/your-org/pahirowatch.git
cd pahirowatch
cp .env.example .env
# Add your HACKATHON_KEY in .env (if left blank, Deterministic Safety Fallback activates automatically)
```

### 2. Run Backend
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Run Frontend
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### 4. Run Automated Test Suite
```bash
PYTHONPATH=. backend/venv/bin/pytest backend/tests -v
```
*(13 tests verifying 0-100 risk scoring, honest confidence penalties, human checkpoint enforcement, bounded loop <=10 steps, memory persistence, and Nepali alerts).*

---

## 16. Demo Scenarios (Interactive Walkthrough)

1. **Scenario 1: Extreme Monsoon Cloudburst (P0 Primary Script)**
   - Click **`1. RUN MONSOON SCENARIO`**
   - Rainfall tool reports 184mm in 24h; slope is 38.5°.
   - Satellite tool initially times out, retries, and returns heavy cloud contamination (82.5%).
   - Agent drops confidence to 0.75, flags Critical Risk (86/100), and creates an incident.
   - **Human Checkpoint Modal pops up:** Ramesh enters verification notes and clicks **`APPROVE ACTION`**.
   - Official Nepali alert and Low-BW SMS payload are generated and dispatched.
2. **Scenario 2: Low Confidence (Suppression of False Alarms)**
   - Click **`2. LOW CONFIDENCE (SUPPRESS FALSE ALARM)`**
   - High rainfall recorded on gentle slope (14°) with low exposure.
   - Agent synthesizes evidence and concludes: *"Monitor only — insufficient evidence for highway escalation."* Proves the agent does not panic blindly.
3. **Scenario 3: Bad Day (Resilience Mode & Graceful Degradation)**
   - Click **`3. BAD DAY (RESILIENCE MODE)`**
   - Weather data is 18h stale; Copernicus satellite is completely down; LLM offline.
   - Deterministic Safety Fallback activates with `"RESILIENCE MODE"` badge. Confidence honestly drops to 50%.

---

## 17. Bilingual & Low-Bandwidth Support

PahiroWatch generates alerts in both English and official **Nepali (नेपाली)**:
```
पहिरोवाच (PahiroWatch) पूर्वसूचना तथा सचेतना सूचना

स्थिति: सम्भावित पहिरो अति उच्च जोखिम (CRITICAL) छ (जोखिम अंक: 86/100, विश्वसनीयता: 75%)
स्थान: Jalbire Waterfall Sector (KM 28) (करिडोर: NH05-MUG)

प्रमुख प्राविधिक कारण:
• पछिल्लो २४ घण्टामा अति भारी वर्षा: 184.0 मि.मि.
• भिरालो कमजोर भूभाग: 38.5 डिग्री
• मुख्य राजमार्गबाट दूरी: 115.0 मिटर नजिक

सिफारिस कार्य:
स्थल निरीक्षण टोली तुरुन्त परिचालन गर्नुहोस् र आवश्यकता अनुसार सवारी आवागमन नियन्त्रण गर्नुहोस्।
```

### Low-Bandwidth SMS Payload (<160 chars)
```
PAHIROWATCH ALERT
CRITICAL RISK (86.0)
Loc: Jalbire Waterfall
Rain24h: 184mm | Slope: 38.5deg
Conf: 75%
Action: Dispatch inspection team
```

---

## 18. Limitations

1. **Synthetic Remote Sensing Pipeline:** Live Copernicus Sentinel-2 Level-2A processing requires high-bandwidth compute and Earth Engine quotas; currently operating with calibrated synthetic adapters.
2. **DEM Resolution:** Uses 30-meter resolution DEM; fine-scale micro-topography (<5m rock fractures) requires drone LiDAR.
3. **Geological Calibration:** Risk thresholds represent an engineering prototype and require formal calibration against 10-year historical landslide inventories from the Department of Mines and Geology (DMG).

---

## 19. Roadmap (What We Would Build in 3 Months)

- **Month 1:** Live DHM telemetry and NASA GPM IMERG satellite precipitation webhooks.
- **Month 2:** Drone photogrammetry & live optical camera feed integration along high-risk highway bridges.
- **Month 3:** Pilot deployment with the Armed Police Force (APF) Disaster Management Training School at Kurintar and Nepal Red Cross Society.

---

## 20. Open-Source Bonus Contribution

We have open-sourced the **Nepal Landslide Risk Agent Toolkit** under the `nepal_landslide_toolkit/` directory:
- `schemas.py`: Pydantic models for precipitation, DEM slopes, Sentinel-2 spectral difference, and immutable agent trace records.
- `interfaces.py`: Clean provider base abstractions for weather, terrain, satellite, and exposure data.
- `simple_risk.py`: Reference 0–100 physical hazard calculator.
- Distributed under the permissive **MIT License** for community adoption across Nepal.
