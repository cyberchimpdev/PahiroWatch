# PahiroWatch — Architecture Specification

> **"Detect the slope. Protect the road. Alert before the disaster."**  
> Autonomous Landslide-Risk Monitoring & Operational Response Agent for Nepal

---

## 1. Executive Summary & Operational Context

**PahiroWatch** is an autonomous geospatial response agent built specifically for high-risk mountain highway corridors in Nepal. Rather than acting as an unverifiable "black-box" prediction tool, PahiroWatch is a **decision-support and early-warning operations system**. It continuously monitors assigned road corridors, investigates multi-source environmental signals upon trigger, calculates deterministic risk and confidence indices, and enforces a mandatory **Human-in-the-Loop checkpoint** before any official emergency action is dispatched.

### Pilot Deployment
- **Target Corridor:** Narayanghat–Mugling Highway (National Highway 05) & Prithvi Highway Junction.
- **Administrative Jurisdiction:** Ichhyakamana Rural Municipality (Wards 4, 5, and 6: Kurintar, Jalbire, Charkilo, Dahakhani).
- **Target Operator:** Ramesh, Municipal Disaster Management Officer & Road Operations Coordinator.

---

## 2. High-Level Architecture

```mermaid
graph TD
    subgraph Trigger Layer
        SCHED[Scheduled Interval Monitor<br>Every 30m / On-Demand] --> AGENT
        THRESH[Threshold Event Trigger<br>e.g. 24h Rainfall > 100mm] --> AGENT
    end

    subgraph PahiroWatch Agent Core
        AGENT[Agentic Controller<br>Max 10 Bounded Steps]
        STATE[Agent State & Memory Context]
        LLM[Reasoning Model<br>OpenAI-compatible / HACKATHON_KEY]
        FALLBACK[Deterministic Safety Fallback<br>Active in Bad-Day / Resilience Mode]
        
        AGENT <--> STATE
        AGENT <--> LLM
        AGENT -. Failover .-> FALLBACK
    end

    subgraph Tool & Provider Abstraction Layer
        T1[get_weather_rainfall] --> P_WX[WeatherProvider<br>DHM / Open-Meteo / Demo]
        T2[get_terrain_risk] --> P_DEM[TerrainProvider<br>SRTM / ALOS DEM / Slope Model]
        T3[get_satellite_change] --> P_SAT[SatelliteProvider<br>Copernicus S2 / Synthetic Demo]
        T4[get_road_exposure] --> P_EXP[ExposureProvider<br>OSM Road & Settlement Network]
        T5[get_incident_memory] --> P_MEM[MemoryProvider<br>SQLite Incident History]
        T6[create_incident_report] --> DB[(SQLite Database)]
        T7[request_human_approval] --> GATE{Human Checkpoint}
        T8[send_alert] --> DISPATCH[Simulated SMS / Broadcast / Low-BW]
        
        AGENT --> T1
        AGENT --> T2
        AGENT --> T3
        AGENT --> T4
        AGENT --> T5
        AGENT --> T6
        AGENT --> T7
        AGENT --> T8
    end

    subgraph Human Oversight & Action
        GATE -->|Review Evidence & Risk| HUMAN[Ramesh: Disaster Officer]
        HUMAN -->|APPROVE| T8
        HUMAN -->|REJECT| STATE
        HUMAN -->|REQUEST MORE EVIDENCE| AGENT
    end

    subgraph Observability & Storage
        AGENT --> TRACE_LOG[Agent Trace Engine<br>Step, Latency, Tokens, NPR Cost]
        TRACE_LOG --> DB
    end
```

---

## 3. Core Architectural Principles

1. **Strict Separation Between Observation and Inference:**  
   The LLM agent is strictly prohibited from inventing numerical readings. Rainfall, slope degrees, change indices, and distance measurements are supplied exclusively by deterministic tools.
2. **Deterministic Evidence Aggregation (Risk Engine):**  
   The quantitative risk score (0–100) is calculated via a transparent, weighted formula with explicit prototype calibration disclaimers. The LLM performs synthesis, context reasoning, and action recommendations.
3. **Resilience & Graceful Degradation (Bad Day Architecture):**  
   If an external API (such as weather or satellite) times out or returns corrupted data, the system implements exponential backoff, records data freshness, degrades confidence honestly, and continues with remaining evidence. If the LLM itself is unreachable, a hardcoded rule-based fallback safeguards operational continuity.
4. **Mandatory Human-in-the-Loop Checkpoint:**  
   `send_alert()` enforces an unbypassable backend constraint: execution is rejected with an HTTP 403 / AgentSecurityError unless `approval_status == 'APPROVED'`.
5. **Radical Data Honesty:**  
   Every data point in the UI and trace is tagged with its provenance: `REAL`, `SYNTHETIC DEMO DATA`, `STALE (X hrs)`, or `DATA UNAVAILABLE`.

---

## 4. Technology Stack

- **Backend Framework:** FastAPI (Python 3.10+)
- **Database:** SQLite 3 with Foreign Keys enabled & WAL mode
- **Geospatial Engine:** Shapely, PyProj, GeoJSON
- **LLM Integration:** OpenAI-compatible API client via standard `httpx` with `HACKATHON_KEY` / `OPENAI_API_KEY`
- **Frontend Framework:** React 18, Vite, TypeScript
- **Styling:** Vanilla CSS & Tailwind CSS for emergency operations center design system
- **Geospatial Visualization:** Leaflet / React-Leaflet with custom tile styling and topographic overlays
- **Analytical Charts:** Recharts for rainfall trends and risk component breakdowns
