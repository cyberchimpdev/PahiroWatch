import sqlite3
import os
from pathlib import Path
from app.config import DB_PATH

def get_db_connection():
    db_target = os.getenv("DATABASE_PATH", DB_PATH)
    db_file = Path(db_target)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file), timeout=30.0)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode and foreign keys for high concurrency & integrity
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.executescript("""
    -- 1. Locations
    CREATE TABLE IF NOT EXISTS locations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        corridor_code TEXT NOT NULL,
        district TEXT NOT NULL,
        municipality TEXT NOT NULL,
        ward INTEGER NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        elevation_m REAL,
        baseline_slope_deg REAL,
        road_name TEXT NOT NULL,
        critical_infrastructure TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 2. Monitoring Runs
    CREATE TABLE IF NOT EXISTS monitoring_runs (
        id TEXT PRIMARY KEY,
        location_id TEXT NOT NULL,
        trigger_type TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        step_count INTEGER DEFAULT 0,
        total_latency_ms INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        estimated_cost_npr REAL DEFAULT 0.0,
        is_resilience_mode BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );

    -- 3. Environmental Observations
    CREATE TABLE IF NOT EXISTS observations (
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        source_type TEXT NOT NULL,
        provider_name TEXT NOT NULL,
        is_synthetic BOOLEAN DEFAULT FALSE,
        is_stale BOOLEAN DEFAULT FALSE,
        data_freshness_minutes INTEGER DEFAULT 0,
        payload_json TEXT NOT NULL,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES monitoring_runs(id)
    );

    -- 4. Risk Assessments
    CREATE TABLE IF NOT EXISTS risk_assessments (
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        risk_score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        confidence_reason TEXT NOT NULL,
        rainfall_component REAL NOT NULL,
        terrain_component REAL NOT NULL,
        satellite_component REAL NOT NULL,
        exposure_component REAL NOT NULL,
        history_component REAL NOT NULL,
        missing_data TEXT,
        contradictory_evidence TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES monitoring_runs(id)
    );

    -- 5. Incidents
    CREATE TABLE IF NOT EXISTS incidents (
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        location_id TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        severity TEXT NOT NULL,
        summary_en TEXT NOT NULL,
        summary_ne TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES monitoring_runs(id),
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );

    -- 6. Approvals (Mandatory Human Gate)
    CREATE TABLE IF NOT EXISTS approvals (
        id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        run_id TEXT NOT NULL,
        operator_name TEXT NOT NULL,
        action_type TEXT NOT NULL,
        operator_notes TEXT,
        decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (incident_id) REFERENCES incidents(id),
        FOREIGN KEY (run_id) REFERENCES monitoring_runs(id)
    );

    -- 7. Actions & Outbound Alerts (Only dispatched after approval)
    CREATE TABLE IF NOT EXISTS actions (
        id TEXT PRIMARY KEY,
        approval_id TEXT NOT NULL,
        incident_id TEXT NOT NULL,
        action_type TEXT NOT NULL,
        channel TEXT NOT NULL,
        payload_en TEXT NOT NULL,
        payload_ne TEXT NOT NULL,
        delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL,
        FOREIGN KEY (approval_id) REFERENCES approvals(id),
        FOREIGN KEY (incident_id) REFERENCES incidents(id)
    );

    -- 8. Agent Memory & Historical Corridors
    CREATE TABLE IF NOT EXISTS agent_memory (
        id TEXT PRIMARY KEY,
        location_id TEXT NOT NULL,
        memory_key TEXT NOT NULL,
        memory_value TEXT NOT NULL,
        importance_weight REAL DEFAULT 1.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );

    -- 9. Agent Trace Log (Real execution timeline)
    CREATE TABLE IF NOT EXISTS agent_traces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        step_number INTEGER NOT NULL,
        event_type TEXT NOT NULL, -- 'TRIGGER', 'GOAL', 'PLAN', 'TOOL_CALL', 'TOOL_RESULT', 'MEMORY', 'DECISION', 'CONFIDENCE', 'GATE', 'HUMAN', 'ACTION', 'DONE'
        content TEXT NOT NULL,
        metadata_json TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES monitoring_runs(id)
    );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
