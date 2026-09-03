import time
import json
import uuid
import httpx
from typing import Dict, Any, Optional
from backend.app.config import HACKATHON_KEY, OPENAI_API_BASE, MODEL_NAME
from backend.app.agent.state import AgentState
from backend.app.agent.tools import ToolRegistry, AgentSecurityError
from backend.app.agent.fallback import DeterministicSafetyFallback
from backend.app.agent.react_agent import ReActAgentEngine
from backend.app.agent.cost_tracker import CostTracker
from backend.app.engine.llm_client import HackathonLLMClient
from backend.app.db.database import get_db_connection

class AgentController:
    """
    PahiroWatch Bounded Agent Controller.
    Governs goal decomposition, LLM reasoning, tool execution, safety gates, and trace streaming.
    """
    def __init__(self):
        self.tools = ToolRegistry()

    def record_trace(self, run_id: str, step_number: int, event_type: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_traces (run_id, step_number, event_type, content, metadata_json)
            VALUES (?, ?, ?, ?, ?)
        """, (run_id, step_number, event_type, content, json.dumps(metadata) if metadata else None))
        conn.commit()
        conn.close()

    def run_monitoring_cycle(
        self,
        location_id: str,
        trigger_type: str = "SCHEDULED",
        scenario_override: Optional[str] = None
    ) -> AgentState:
        
        start_time = time.time()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Load location details
        cursor.execute("SELECT * FROM locations WHERE id = ?", (location_id,))
        loc = cursor.fetchone()
        if not loc:
            # Fallback default if not found
            cursor.execute("SELECT * FROM locations LIMIT 1")
            loc = cursor.fetchone()

        run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
        
        # Initialize run in database
        cursor.execute("""
            INSERT INTO monitoring_runs (id, location_id, trigger_type, status, started_at)
            VALUES (?, ?, ?, 'RUNNING', CURRENT_TIMESTAMP)
        """, (run_id, loc["id"], trigger_type))
        conn.commit()
        conn.close()

        state = AgentState(
            run_id=run_id,
            location_id=loc["id"],
            location_name=loc["name"],
            latitude=loc["latitude"] if loc["latitude"] is not None else 27.8182,
            longitude=loc["longitude"] if loc["longitude"] is not None else 84.5381,
            baseline_slope=loc["baseline_slope_deg"] if loc["baseline_slope_deg"] is not None else 35.0,
            elevation_m=loc["elevation_m"] if loc["elevation_m"] is not None else 300.0,
            goal="Monitor assigned Nepal highway corridor for emerging landslide risk, determine whether environmental signals warrant human inspection, and stop before official warning dispatch.",
            trigger_type=trigger_type,
            scenario_override=scenario_override
        )

        # Attempt to run via LLM if HACKATHON_KEY is provided and not in BAD_DAY scenario
        use_live_llm = bool(HACKATHON_KEY and HACKATHON_KEY not in ["", "mock-or-live-key"] and scenario_override != "BAD_DAY")

        if use_live_llm:
            try:
                state = ReActAgentEngine.execute_react_loop(state, self.tools, self.record_trace)
            except Exception as e:
                # LLM failed/timed out -> fall back to deterministic safety engine
                state.is_resilience_mode = True
                self.record_trace(
                    state.run_id, state.step_count + 1, "TRIGGER",
                    f"LLM Reasoning Error ({str(e)}). Switching immediately to Deterministic Safety Fallback Engine.",
                    {"error": str(e), "fallback": True}
                )
                state = DeterministicSafetyFallback.execute_fallback_loop(state, self.tools, self.record_trace)
        else:
            # Execute Deterministic Safety Fallback Engine directly
            state = DeterministicSafetyFallback.execute_fallback_loop(state, self.tools, self.record_trace)

        # Calculate metrics
        end_time = time.time()
        state.latency_ms = int((end_time - start_time) * 1000)
        state.cost_npr = CostTracker.calculate_cost_npr(state.tokens_used, max(0, state.tokens_used // 4))

        # Update monitoring_runs and risk_assessments in DB
        conn = get_db_connection()
        cursor = conn.cursor()
        
        run_status = "PAUSED_HUMAN_GATE" if state.requires_human_approval else "COMPLETED"
        cursor.execute("""
            UPDATE monitoring_runs 
            SET status = ?, completed_at = CURRENT_TIMESTAMP, step_count = ?, 
                total_latency_ms = ?, total_tokens = ?, estimated_cost_npr = ?, is_resilience_mode = ?
            WHERE id = ?
        """, (
            run_status, state.step_count, state.latency_ms, 
            state.tokens_used, state.cost_npr, state.is_resilience_mode, run_id
        ))

        if state.risk_score is not None:
            cursor.execute("""
                INSERT OR REPLACE INTO risk_assessments
                (id, run_id, risk_score, risk_level, confidence_score, confidence_reason, 
                 rainfall_component, terrain_component, satellite_component, exposure_component, history_component, missing_data, contradictory_evidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"RSK-{run_id[:8]}", run_id, state.risk_score, state.risk_level or "LOW",
                state.confidence_score or 0.5, state.confidence_reason or "Assessed",
                state.observations.get("weather", {}).get("rainfall_24h_mm", 0.0),
                state.observations.get("terrain", {}).get("slope_deg", 0.0),
                state.observations.get("satellite", {}).get("change_score", 0.0),
                state.observations.get("exposure", {}).get("exposure_score", 0.0),
                10.0,
                json.dumps(state.missing_data),
                state.contradictory_evidence
            ))

        conn.commit()
        conn.close()

        return state

    def _execute_llm_loop(self, state: AgentState) -> AgentState:
        """
        Execute bounded LLM loop against OpenAI-compatible endpoint with live geotechnical synthesis.
        """
        # Step 1: Run sensor data collection through tools
        state = DeterministicSafetyFallback.execute_fallback_loop(state, self.tools, self.record_trace)

        # Step 2: Live LLM Operational Synthesis using Azure OpenAI DeepSeek-V4-Flash
        obs = state.observations
        rf = obs.get("weather", {}).get("rainfall_24h_mm", 0.0)
        slp = obs.get("terrain", {}).get("slope_deg", state.baseline_slope)
        cld = obs.get("satellite", {}).get("cloud_cover_pct", 0.0)
        dist = obs.get("exposure", {}).get("highway_distance_m", 100.0)

        prompt = (
            f"Location: {state.location_name}\n"
            f"24h Precipitation: {rf} mm\n"
            f"Terrain Slope: {slp} degrees\n"
            f"Satellite Cloud Cover: {cld}%\n"
            f"Proximity to Highway: {dist} meters\n"
            f"Computed Risk Index: {state.risk_score}/100 ({state.risk_level})\n\n"
            f"In 2 concise, professional sentences, provide an operational geotechnical synthesis "
            f"and state clearly whether municipal field patrol / road staging is required."
        )

        llm_res = HackathonLLMClient.complete(prompt, max_tokens=150)
        if llm_res.get("success"):
            state.tokens_used += llm_res.get("total_tokens", 0)
            state.is_resilience_mode = False
            self.record_trace(
                state.run_id, state.step_count + 1, "REASONING",
                f"[Live {llm_res.get('model')} Synthesis]: {llm_res.get('content')}",
                {
                    "provider": "Azure OpenAI (Nexalaris Tech API)",
                    "model": llm_res.get("model"),
                    "tokens": llm_res.get("total_tokens"),
                    "latency_ms": llm_res.get("latency_ms")
                }
            )
            state.step_count += 1
        else:
            # If live LLM had an error, trace the resilience note
            state.is_resilience_mode = True
            self.record_trace(
                state.run_id, state.step_count + 1, "TRIGGER",
                f"LLM Reasoning note: {llm_res.get('error')}. Fallback heuristics active.",
                {"resilience": True}
            )

        return state

    def process_human_approval(
        self,
        incident_id: str,
        operator_name: str,
        action_type: str, # 'APPROVE', 'REJECT', 'REQUEST_MORE_EVIDENCE'
        operator_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mandatory Human Gate: Processes operator decision and only calls send_alert() on APPROVE.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        inc = cursor.fetchone()
        if not inc:
            conn.close()
            raise ValueError(f"Incident {incident_id} not found")

        run_id = inc["run_id"]
        approval_id = f"APP-{uuid.uuid4().hex[:8]}"

        cursor.execute("""
            INSERT INTO approvals (id, incident_id, run_id, operator_name, action_type, operator_notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (approval_id, incident_id, run_id, operator_name, action_type, operator_notes))

        # Record human trace
        cursor.execute("SELECT MAX(step_number) as max_step FROM agent_traces WHERE run_id = ?", (run_id,))
        row = cursor.fetchone()
        next_step = (row["max_step"] or 0) + 1

        cursor.execute("""
            INSERT INTO agent_traces (run_id, step_number, event_type, content, metadata_json)
            VALUES (?, ?, 'HUMAN', ?, ?)
        """, (
            run_id, next_step,
            f"Human Operator ({operator_name}) decision: {action_type}. Notes: {operator_notes or 'None'}",
            json.dumps({"operator": operator_name, "decision": action_type})
        ))
        
        conn.commit()
        conn.close()

        if action_type == "APPROVE":
            # Reconstruct minimal state to dispatch alert safely
            state = AgentState(
                run_id=run_id,
                location_id=inc["location_id"],
                location_name=inc["title"].replace("Active Hazard Escalation: ", ""),
                latitude=27.8182,
                longitude=84.5381,
                baseline_slope=38.5,
                elevation_m=340.0,
                goal="Execute approved emergency alert dispatch",
                incident_id=incident_id,
                approval_status="APPROVED",
                risk_level=inc["severity"],
                recommended_action=inc["recommended_action"]
            )
            # Execute dispatch
            alert_res = self.tools.send_alert(state)
            
            # Record ACTION trace
            self.record_trace(
                run_id, next_step + 1, "ACTION",
                f"Action dispatched: Incident verified and bilingual notification sent ({alert_res['channel']}).",
                alert_res
            )
            self.record_trace(
                run_id, next_step + 2, "DONE",
                "Cycle closed with human approval and logged action.",
                {"status": "DISPATCHED_AND_CLOSED"}
            )
            return {
                "status": "APPROVED_AND_DISPATCHED",
                "approval_id": approval_id,
                "alert": alert_res
            }
        else:
            # Mark incident dismissed/rejected
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE incidents SET status = 'DISMISSED', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (incident_id,))
            cursor.execute("UPDATE monitoring_runs SET status = 'REJECTED_BY_HUMAN', completed_at = CURRENT_TIMESTAMP WHERE id = ?", (run_id,))
            conn.commit()
            conn.close()

            self.record_trace(
                run_id, next_step + 1, "DONE",
                f"Action suppressed by operator ({action_type}). Run archived to memory.",
                {"status": "HUMAN_REJECTED"}
            )
            return {
                "status": f"HUMAN_{action_type}",
                "approval_id": approval_id
            }
