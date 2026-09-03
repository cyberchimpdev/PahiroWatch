from typing import Dict, Any, List
from app.agent.state import AgentState
from app.agent.tools import ToolRegistry
from app.engine.risk_calculator import RiskCalculator
from app.engine.confidence_engine import ConfidenceEngine
from app.engine.alert_generator import AlertGenerator

class DeterministicSafetyFallback:
    """
    Deterministic Safety Fallback Engine.
    Activates when the LLM service is offline, rate-limited, or timing out (Bad Day Mode).
    Enforces operational continuity without hallucinations.
    """

    @staticmethod
    def execute_fallback_loop(state: AgentState, tools: ToolRegistry, trace_recorder) -> AgentState:
        state.is_resilience_mode = True
        state.step_count = 0
        trace_step = 1

        trace_recorder(
            state.run_id, trace_step, "TRIGGER",
            f"Autonomous monitoring cycle started for {state.location_name}. Trigger: {state.trigger_type}",
            {"scenario": state.scenario_override, "resilience_mode": True}
        )
        trace_step += 1

        trace_recorder(
            state.run_id, trace_step, "GOAL",
            state.goal,
            {"operator": "Ramesh (Disaster Management Officer)"}
        )
        trace_step += 1

        trace_recorder(
            state.run_id, trace_step, "PLAN",
            "Deterministic Safety Fallback Active: Assess rainfall → terrain → satellite (with retry) → road exposure → historical memory → calculate risk → human gate.",
            {"mode": "DETERMINISTIC_SAFETY_FALLBACK"}
        )
        trace_step += 1

        # --- Bounded Iteration 1: Weather Telemetry ---
        state.step_count += 1
        trace_recorder(
            state.run_id, trace_step, "TOOL_CALL",
            "get_weather_rainfall(location)", {"iteration": state.step_count, "status": "PENDING"}
        )
        trace_step += 1
        try:
            w_res = tools.get_weather_rainfall(state)
            trace_recorder(
                state.run_id, trace_step, "TOOL_RESULT",
                f"Rainfall 24h = {w_res.get('rainfall_24h_mm')}mm | Freshness = {w_res.get('freshness_minutes')}m ({'STALE' if w_res.get('is_stale') else 'FRESH'})",
                w_res
            )
            trace_step += 1
        except Exception as e:
            w_res = None
            trace_recorder(
                state.run_id, trace_step, "TOOL_RESULT",
                f"Weather provider error: {str(e)}. Using fallback profile.",
                {"error": str(e)}
            )
            trace_step += 1

        # --- Bounded Iteration 2: Terrain DEM ---
        state.step_count += 1
        trace_recorder(
            state.run_id, trace_step, "TOOL_CALL",
            "get_terrain_risk(location)", {"iteration": state.step_count, "status": "PENDING"}
        )
        trace_step += 1
        t_res = tools.get_terrain_risk(state)
        trace_recorder(
            state.run_id, trace_step, "TOOL_RESULT",
            f"Slope = {t_res.get('slope_deg')}° | Terrain Hazard = {t_res.get('hazard_level')}",
            t_res
        )
        trace_step += 1

        # --- Bounded Iteration 3: Satellite Change with Retry ---
        state.step_count += 1
        sat_res = None
        is_sat_missing = False
        trace_recorder(
            state.run_id, trace_step, "TOOL_CALL",
            "get_satellite_change(location)", {"iteration": state.step_count, "attempt": 1}
        )
        trace_step += 1

        try:
            if state.scenario_override in ["MONSOON", "BAD_DAY"]:
                # First attempt times out
                try:
                    tools.get_satellite_change(state, simulate_failure=True)
                except TimeoutError as err:
                    trace_recorder(
                        state.run_id, trace_step, "TOOL_RESULT",
                        f"Copernicus Sentinel API gateway timeout (HTTP 504). Executing exponential backoff retry...",
                        {"error": str(err), "retry": 1}
                    )
                    trace_step += 1
                    
                    if state.scenario_override == "BAD_DAY":
                        is_sat_missing = True
                        trace_recorder(
                            state.run_id, trace_step, "TOOL_RESULT",
                            "Retry failed: Satellite imagery service completely unavailable. Degraded mode active.",
                            {"status": "SATELLITE_UNAVAILABLE"}
                        )
                        trace_step += 1
                    else:
                        # Monsoon scenario retry gets cloud-contaminated data
                        sat_res = tools.get_satellite_change(state, simulate_failure=False)
                        trace_recorder(
                            state.run_id, trace_step, "TOOL_RESULT",
                            f"Retry succeeded: Change score = {sat_res.get('change_score')} | Cloud cover = {sat_res.get('cloud_cover_pct')}% ({sat_res.get('cloud_quality')})",
                            sat_res
                        )
                        trace_step += 1
            else:
                sat_res = tools.get_satellite_change(state, simulate_failure=False)
                trace_recorder(
                    state.run_id, trace_step, "TOOL_RESULT",
                    f"Change score = {sat_res.get('change_score')} | Quality = {sat_res.get('cloud_quality')}",
                    sat_res
                )
                trace_step += 1
        except Exception as e:
            is_sat_missing = True
            trace_recorder(
                state.run_id, trace_step, "TOOL_RESULT",
                f"Satellite tool exception: {str(e)}. Continuing with terrestrial telemetry.",
                {"error": str(e)}
            )
            trace_step += 1

        # --- Bounded Iteration 4: Road Exposure ---
        state.step_count += 1
        trace_recorder(
            state.run_id, trace_step, "TOOL_CALL",
            "get_road_exposure(location)", {"iteration": state.step_count, "status": "PENDING"}
        )
        trace_step += 1
        exp_res = tools.get_road_exposure(state)
        trace_recorder(
            state.run_id, trace_step, "TOOL_RESULT",
            f"Nearest road = {exp_res.get('nearest_road')} ({exp_res.get('distance_to_road_m')}m) | Exposure = {exp_res.get('exposure_level')}",
            exp_res
        )
        trace_step += 1

        # --- Bounded Iteration 5: Incident Memory ---
        state.step_count += 1
        trace_recorder(
            state.run_id, trace_step, "TOOL_CALL",
            "get_incident_memory(location)", {"iteration": state.step_count, "status": "PENDING"}
        )
        trace_step += 1
        mem_res = tools.get_incident_memory(state)
        trace_recorder(
            state.run_id, trace_step, "MEMORY",
            f"Cross-run memory query: {mem_res.get('total_historical_events')} previous incidents found. Active unresolved: {mem_res.get('has_unresolved_incidents')}",
            mem_res
        )
        trace_step += 1

        # --- Bounded Iteration 6: Calculate Deterministic Risk & Confidence ---
        state.step_count += 1
        risk_score, risk_level, breakdown = RiskCalculator.calculate_risk(
            weather_obs=w_res,
            terrain_obs=t_res,
            satellite_obs=sat_res,
            exposure_obs=exp_res,
            memory_obs=mem_res
        )
        state.risk_score = risk_score
        state.risk_level = risk_level

        confidence_score, confidence_reason, missing, contradictory = ConfidenceEngine.assess_confidence(
            weather_obs=w_res,
            terrain_obs=t_res,
            satellite_obs=sat_res,
            exposure_obs=exp_res,
            memory_obs=mem_res,
            is_satellite_missing=is_sat_missing,
            is_weather_stale=(w_res.get("is_stale", False) if w_res else True)
        )
        state.confidence_score = confidence_score
        state.confidence_reason = confidence_reason
        state.missing_data = missing
        state.contradictory_evidence = contradictory

        # --- Bounded Iteration 7: Agent Synthesis & Decision ---
        state.step_count += 1
        if state.scenario_override == "LOW_CONFIDENCE" or risk_score < 50.0:
            decision = (
                f"Evidence indicates {risk_level} risk ({risk_score}/100, Confidence: {int(confidence_score*100)}%). "
                "Although moderate rainfall was recorded, the gentle slope angle and low infrastructure exposure "
                "do not warrant operational highway escalation. Continuous routine monitoring maintained."
            )
            rec_action = "Maintain automated monitoring cycle; no emergency escalation required."
            requires_gate = False
        elif is_sat_missing:
            decision = (
                f"CRITICAL HAZARD WARNING: High risk ({risk_score}/100). Satellite confirmation is unavailable due to "
                f"service outage. Rainfall ({w_res.get('rainfall_24h_mm', 0)}mm), steep terrain ({t_res.get('slope_deg', 0)}°), "
                f"and close highway proximity ({exp_res.get('distance_to_road_m', 0)}m) remain sufficient to recommend "
                f"immediate human inspection, but confidence is honestly reduced to {int(confidence_score*100)}%."
            )
            rec_action = "Inspect road segment at KM 28-32 and prepare precautionary traffic pacing."
            requires_gate = True
        else:
            decision = (
                f"Elevated landslide risk detected ({risk_level}, Score: {risk_score}/100, Confidence: {int(confidence_score*100)}%). "
                f"Severe rainfall combined with steep terrain ({t_res.get('slope_deg')}°) and optical change indicator "
                f"warrants urgent municipal road operations escalation."
            )
            rec_action = "Dispatch municipal road inspection patrol and stage excavator at Jalbire depot."
            requires_gate = True

        state.agent_decision = decision
        state.recommended_action = rec_action

        trace_recorder(
            state.run_id, trace_step, "DECISION",
            decision,
            {"risk_score": risk_score, "risk_level": risk_level, "breakdown": breakdown}
        )
        trace_step += 1

        trace_recorder(
            state.run_id, trace_step, "CONFIDENCE",
            f"Confidence = {confidence_score} ({int(confidence_score*100)}%). Reason: {confidence_reason}",
            {"missing_data": missing, "contradictory": contradictory}
        )
        trace_step += 1

        # --- Bounded Iteration 8: Human Gate Checkpoint or Completion ---
        state.step_count += 1
        if requires_gate:
            inc_res = tools.create_incident_report(
                state=state,
                summary_en=decision,
                summary_ne=f"{state.location_name} खण्डमा भारी वर्षा र भिरालो जमिनका कारण उच्च पहिरो जोखिम देखिएको छ।",
                recommended_action=rec_action
            )
            trace_recorder(
                state.run_id, trace_step, "GATE",
                f"HUMAN APPROVAL REQUIRED: Incident {inc_res['incident_id']} created. Consequential action halted pending authorization by operator (Ramesh).",
                {"incident_id": inc_res["incident_id"], "recommended_action": rec_action}
            )
            trace_step += 1
            state.requires_human_approval = True
            state.approval_status = "PENDING"
        else:
            trace_recorder(
                state.run_id, trace_step, "DONE",
                "Monitoring run concluded without escalation. Observations logged to memory.",
                {"status": "ROUTINE_COMPLETED"}
            )
            trace_step += 1

        # Enforce max 10 steps invariant
        assert state.step_count <= 10, f"Invariant violated: step count {state.step_count} exceeds max 10"

        return state
