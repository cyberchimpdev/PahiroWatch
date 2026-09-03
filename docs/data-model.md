# PahiroWatch — Data Model Specification

This document details the persistent SQLite relational schema and in-memory AgentState contracts.

---

## 1. Relational Database Schema (SQLite)

```sql
-- 1. Monitored Locations (Corridors, Segments, Municipalities)
CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    corridor_code TEXT NOT NULL, -- e.g., 'NH05-MUG'
    district TEXT NOT NULL,      -- e.g., 'Chitwan'
    municipality TEXT NOT NULL,  -- e.g., 'Ichhyakamana Rural Municipality'
    ward INTEGER NOT NULL,       -- e.g., 5
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    elevation_m REAL,
    baseline_slope_deg REAL,
    road_name TEXT NOT NULL,
    critical_infrastructure TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Monitoring Runs (Execution cycles triggered by scheduler, threshold, or human)
CREATE TABLE IF NOT EXISTS monitoring_runs (
    id TEXT PRIMARY KEY,
    location_id TEXT NOT NULL,
    trigger_type TEXT NOT NULL, -- 'SCHEDULED', 'THRESHOLD_EVENT', 'MANUAL_DISPATCH', 'DEMO_SCENARIO'
    status TEXT NOT NULL,       -- 'RUNNING', 'COMPLETED', 'PAUSED_HUMAN_GATE', 'FAILED'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    step_count INTEGER DEFAULT 0,
    total_latency_ms INTEGER,
    total_tokens INTEGER,
    estimated_cost_npr REAL,
    is_resilience_mode BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- 3. Environmental Observations (Raw data collected strictly via tools)
CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    source_type TEXT NOT NULL,  -- 'WEATHER', 'TERRAIN', 'SATELLITE', 'EXPOSURE'
    provider_name TEXT NOT NULL, -- 'DHM_OpenMeteo', 'SRTM_DEM', 'Sentinel2_Synthetic', 'OSM'
    is_synthetic BOOLEAN DEFAULT FALSE,
    is_stale BOOLEAN DEFAULT FALSE,
    data_freshness_minutes INTEGER,
    payload_json TEXT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES monitoring_runs(id)
);

-- 4. Risk Assessments (Deterministic aggregation + confidence scoring)
CREATE TABLE IF NOT EXISTS risk_assessments (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    risk_score REAL NOT NULL,      -- 0 to 100
    risk_level TEXT NOT NULL,      -- 'LOW', 'MODERATE', 'HIGH', 'CRITICAL'
    confidence_score REAL NOT NULL,-- 0.0 to 1.0
    confidence_reason TEXT NOT NULL,
    rainfall_component REAL NOT NULL,
    terrain_component REAL NOT NULL,
    satellite_component REAL NOT NULL,
    exposure_component REAL NOT NULL,
    history_component REAL NOT NULL,
    missing_data TEXT,             -- JSON array of missing source names
    contradictory_evidence TEXT,   -- Notes on conflicting signals
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES monitoring_runs(id)
);

-- 5. Incidents (Escalated events requiring operational tracking)
CREATE TABLE IF NOT EXISTS incidents (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    location_id TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,          -- 'PENDING_APPROVAL', 'ACTIVE_MONITORING', 'ACTION_DISPATCHED', 'RESOLVED', 'DISMISSED'
    severity TEXT NOT NULL,        -- 'HIGH', 'CRITICAL', 'MODERATE'
    summary_en TEXT NOT NULL,
    summary_ne TEXT NOT NULL,      -- Nepali summary
    recommended_action TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES monitoring_runs(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- 6. Human Approvals (Mandatory gate records)
CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    operator_name TEXT NOT NULL,   -- e.g., 'Ramesh (Disaster Management Officer)'
    action_type TEXT NOT NULL,     -- 'APPROVE', 'REJECT', 'REQUEST_MORE_EVIDENCE'
    operator_notes TEXT,
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(id),
    FOREIGN KEY (run_id) REFERENCES monitoring_runs(id)
);

-- 7. Actions & Outbound Alerts (Executed only after approval)
CREATE TABLE IF NOT EXISTS actions (
    id TEXT PRIMARY KEY,
    approval_id TEXT NOT NULL,
    incident_id TEXT NOT NULL,
    action_type TEXT NOT NULL,     -- 'DISPATCH_ROAD_CREW', 'EMERGENCY_SMS', 'HIGHWAY_WARNING'
    channel TEXT NOT NULL,         -- 'SIMULATED_SMS', 'INTERNAL_DISPATCH', 'LOW_BW_TEXT'
    payload_en TEXT NOT NULL,
    payload_ne TEXT NOT NULL,
    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,          -- 'SENT', 'FAILED'
    FOREIGN KEY (approval_id) REFERENCES approvals(id),
    FOREIGN KEY (incident_id) REFERENCES incidents(id)
);

-- 8. Agent Memory & Historical Corridors (Cross-run memory)
CREATE TABLE IF NOT EXISTS agent_memory (
    id TEXT PRIMARY KEY,
    location_id TEXT NOT NULL,
    memory_key TEXT NOT NULL,
    memory_value TEXT NOT NULL,
    importance_weight REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(id)
);
```

---

## 2. Agent State Model (Pydantic / Python In-Memory)

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentState(BaseModel):
    run_id: str
    location_id: str
    goal: str
    step_count: int = 0
    max_steps: int = 10
    trigger_type: str
    plan: List[str] = Field(default_factory=list)
    observations: Dict[str, Any] = Field(default_factory=dict)
    tool_history: List[Dict[str, Any]] = Field(default_factory=list)
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    confidence_score: Optional[float] = None
    confidence_reason: Optional[str] = None
    missing_data: List[str] = Field(default_factory=list)
    contradictory_evidence: Optional[str] = None
    historical_context: List[Dict[str, Any]] = Field(default_factory=list)
    agent_decision: Optional[str] = None
    recommended_action: Optional[str] = None
    requires_human_approval: bool = False
    approval_status: str = "PENDING"  # 'PENDING', 'APPROVED', 'REJECTED'
    incident_id: Optional[str] = None
    alert_sent: bool = False
    tokens_used: int = 0
    cost_npr: float = 0.0
    latency_ms: int = 0
    resilience_mode: bool = False
```
