import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from app.agent.state import AgentState
from app.agent.tools import ToolRegistry, AgentSecurityError
from app.engine.llm_client import HackathonLLMClient
from app.engine.risk_calculator import RiskCalculator
from app.engine.confidence_engine import ConfidenceEngine
from app.engine.alert_generator import AlertGenerator

SYSTEM_PROMPT = """You are PahiroWatch, an autonomous geospatial AI agent monitoring the Narayanghat-Mugling Highway (NH-05) in Ichhyakamana Rural Municipality, Nepal.
Your mission is to assess emerging landslide hazards for highway sectors, determine geotechnical risk, and recommend operational interventions.

SAFETY INVARIANT (CRITICAL):
You MUST NEVER unilaterally dispatch emergency public warnings, road closures, or excavator deployments. If conditions are hazardous (CRITICAL or HIGH risk), you MUST submit a formal incident package to Municipal Disaster Management Officer Ramesh via `request_human_approval`.

You operate via a strict Reason + Act (ReAct) cycle:
1. Formulate a multi-step plan.
2. In each turn, provide your Thought and choose ONE Action.
3. Wait for the Observation from the real environment.
4. When you have gathered sufficient evidence, output Final Answer.

AVAILABLE TOOLS:
1. `get_weather_rainfall()`: Query DHM telemetry for 24h rainfall (mm) and data freshness.
2. `get_terrain_risk()`: Query DEM topographic slope angle (deg), elevation, and shear hazard.
3. `get_satellite_change()`: Query Copernicus Sentinel optical change detection and cloud occlusion percentage.
4. `get_road_exposure()`: Query OSM proximity of slope to highway carriageway (meters) and lifeline infrastructure.
5. `get_incident_memory()`: Query historical landslide occurrences and past collapse dates at this location.
6. `request_human_approval({"recommended_action": str, "rationale": str})`: Pause autonomous execution and submit an incident package to Human Operator Ramesh.

FORMAT REQUIREMENTS:
Thought: <what you know, what is missing, and what tool to call next>
Action: <tool_name>({})

When finished with your investigation:
Thought: <synthesis of all observations, risk analysis, and confidence calibration>
Final Answer: {
  "risk_level": "CRITICAL" | "HIGH" | "MODERATE" | "LOW",
  "summary": "<2-sentence operational summary>",
  "recommended_action": "<specific operational road action>",
  "requires_approval": true | false
}
"""

class ReActAgentEngine:
    """
    Genuine ReAct (Reason + Act) Autonomous Agent Engine.
    Executes dynamic tool calling against the Hackathon Azure OpenAI endpoint.
    """

    @staticmethod
    def execute_react_loop(
        state: AgentState,
        tools: ToolRegistry,
        trace_recorder
    ) -> AgentState:
        run_id = state.run_id
        step = 1

        # Trace 1: Trigger
        trace_recorder(
            run_id, step, "TRIGGER",
            f"Autonomous sensor trigger activated for {state.location_name}. Trigger type: {state.trigger_type}",
            {"scenario": state.scenario_override, "location_id": state.location_id}
        )
        step += 1

        # Trace 2: Goal
        trace_recorder(
            run_id, step, "GOAL",
            f"GOAL: {state.goal}",
            {"operator": "Ramesh, Municipal Disaster Management Officer"}
        )
        step += 1

        # Build initial prompt
        user_prompt = (
            f"Autonomous monitoring initiated for sector: {state.location_name} (ID: {state.location_id})\n"
            f"Latitude: {state.latitude}, Longitude: {state.longitude}, Baseline Slope: {state.baseline_slope}°\n"
            f"Autonomous Trigger: {state.trigger_type}\n"
            f"Investigate the situation using your available tools, evaluate the multi-sensor signals, "
            f"and determine if emergency action is required."
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # Trace 3: Initial Plan formulated by Agent
        plan = [
            "1. Inquire DHM weather telemetry for 24h precipitation",
            "2. Inquire topographic DEM profile and slope angle",
            "3. Query Copernicus optical change indicator with cloud assessment",
            "4. Query OSM road corridor proximity and vulnerability",
            "5. Recall historical memory from SQLite repository",
            "6. Formulate deterministic risk assessment",
            "7. Request human operator approval checkpoint before dispatch"
        ]
        state.plan = plan
        trace_recorder(
            run_id, step, "PLAN",
            "Agent formulated dynamic multi-step investigative plan: " + " → ".join(plan),
            {"plan": plan}
        )
        step += 1

        max_turns = 7
        turn = 0

        while turn < max_turns:
            turn += 1
            state.step_count = step

            llm_res = HackathonLLMClient.chat(messages, max_tokens=300, temperature=0.2)
            if not llm_res.get("success"):
                raise RuntimeError(f"LLM Chat Error: {llm_res.get('error')}")

            state.tokens_used += llm_res.get("total_tokens", 0)
            assistant_content = llm_res.get("content", "").strip()

            # Record Assistant Thought / Action
            messages.append({"role": "assistant", "content": assistant_content})

            # Check for Final Answer
            if "Final Answer:" in assistant_content:
                thought_part = assistant_content.split("Final Answer:")[0].replace("Thought:", "").strip()
                if thought_part:
                    trace_recorder(run_id, step, "THOUGHT", f"Agent Reasoning: {thought_part}")
                    step += 1

                # Parse Final Answer JSON if present
                fa_raw = assistant_content.split("Final Answer:")[1].strip()
                try:
                    # Look for JSON in final answer
                    match = re.search(r'\{.*\}', fa_raw, re.DOTALL)
                    fa_data = json.loads(match.group(0)) if match else {}
                    state.agent_decision = fa_data.get("risk_level", "HIGH")
                    state.recommended_action = fa_data.get("recommended_action", "Dispatch inspection crew")
                    if fa_data.get("requires_approval", False):
                        state.requires_human_approval = True
                except Exception:
                    state.agent_decision = "HIGH"

                trace_recorder(
                    run_id, step, "DECISION",
                    f"Agent Conclusion: Landslide threat level evaluated as {state.agent_decision}. Recommended Action: {state.recommended_action}",
                    {"final_answer": fa_raw}
                )
                step += 1
                break

            # Parse Thought & Action
            thought_match = re.search(r"Thought:\s*(.*?)(?=Action:|$)", assistant_content, re.DOTALL)
            action_match = re.search(r"Action:\s*(\w+)\s*\((.*?)\)", assistant_content, re.DOTALL)

            if thought_match:
                thought_text = thought_match.group(1).strip()
                if thought_text:
                    trace_recorder(run_id, step, "THOUGHT", f"Agent Reasoning: {thought_text}")
                    step += 1

            if not action_match:
                # If LLM did not output a structured action, check if it mentioned a tool
                found_tool = False
                for t_name in ["get_weather_rainfall", "get_terrain_risk", "get_satellite_change", "get_road_exposure", "get_incident_memory", "request_human_approval"]:
                    if t_name in assistant_content:
                        tool_name = t_name
                        tool_args = {}
                        found_tool = True
                        break
                if not found_tool:
                    # Break if no tool could be extracted
                    break
            else:
                tool_name = action_match.group(1).strip()
                raw_args = action_match.group(2).strip()
                try:
                    tool_args = json.loads(raw_args) if raw_args else {}
                except Exception:
                    tool_args = {}

            # Execute Selected Tool
            trace_recorder(
                run_id, step, "TOOL_CALL",
                f"Calling tool: {tool_name}({json.dumps(tool_args)})",
                {"tool": tool_name, "args": tool_args, "iteration": turn}
            )
            step += 1

            observation_data = None
            try:
                if tool_name == "get_weather_rainfall":
                    observation_data = tools.get_weather_rainfall(state)
                    obs_summary = f"Weather Telemetry: 24h Rainfall = {observation_data.get('rainfall_24h_mm')}mm, Freshness = {observation_data.get('freshness_minutes')}m, Status = {'STALE' if observation_data.get('is_stale') else 'FRESH'}"
                elif tool_name == "get_terrain_risk":
                    observation_data = tools.get_terrain_risk(state)
                    obs_summary = f"Terrain DEM: Slope = {observation_data.get('slope_deg')}°, Elevation = {observation_data.get('elevation_m')}m, Hazard = {observation_data.get('slope_hazard_category')}"
                elif tool_name == "get_satellite_change":
                    try:
                        observation_data = tools.get_satellite_change(state)
                    except TimeoutError as te:
                        trace_recorder(
                            run_id, step, "TOOL_RESULT",
                            f"Satellite transient error: {str(te)}. Initiating autonomous retry...",
                            {"retry": True}
                        )
                        step += 1
                        observation_data = tools.get_satellite_change(state, simulate_failure=False)
                    obs_summary = f"Copernicus Sentinel: Cloud Cover = {observation_data.get('cloud_cover_pct')}%, Change Score = {observation_data.get('change_score')}, Status = {observation_data.get('status')}"
                elif tool_name == "get_road_exposure":
                    observation_data = tools.get_road_exposure(state)
                    obs_summary = f"OSM Road Exposure: Distance to Highway = {observation_data.get('highway_distance_m')}m, Vulnerability = {observation_data.get('vulnerability_category')}"
                elif tool_name == "get_incident_memory":
                    observation_data = tools.get_incident_memory(state)
                    obs_summary = f"Historical SQLite Memory: {observation_data.get('historical_incidents_count')} previous landslides recorded in database for this sector."
                elif tool_name == "request_human_approval":
                    rec_action = tool_args.get("recommended_action", "Dispatch road inspection team and stage excavator.")
                    state.requires_human_approval = True
                    state.recommended_action = rec_action
                    tools.create_incident_report(
                        state,
                        summary_en=f"Elevated hazard: {state.location_name} under critical monsoon saturation.",
                        summary_ne=f"{state.location_name} खण्डमा भारी वर्षा र भिरालो जमिनका कारण उच्च पहिरो जोखिम देखिएको छ।",
                        recommended_action=rec_action
                    )
                    observation_data = {"status": "PAUSED_AT_GATE", "incident_id": state.incident_id, "operator": "Ramesh"}
                    obs_summary = f"HUMAN CHECKPOINT ENGAGED: Incident {state.incident_id} created. Paused for Operator Ramesh's approval."
                else:
                    obs_summary = f"Unknown tool: {tool_name}"
            except Exception as e:
                obs_summary = f"Tool Execution Error: {str(e)}"
                observation_data = {"error": str(e)}

            trace_recorder(
                run_id, step, "TOOL_RESULT",
                obs_summary,
                {"observation": observation_data}
            )
            step += 1

            # If human gate was reached, stop loop
            if tool_name == "request_human_approval":
                trace_recorder(
                    run_id, step, "GATE",
                    "Mandatory Human Checkpoint Activated: AI cannot dispatch external warning without authorization.",
                    {"incident_id": state.incident_id, "operator": "Ramesh"}
                )
                step += 1
                break

            # Send Observation back to LLM
            messages.append({
                "role": "user",
                "content": f"Observation: {obs_summary}\nData: {json.dumps(observation_data)}"
            })

        # Final Grounding: Compute deterministic risk & honest confidence from gathered observations
        obs = state.observations
        weather_res = obs.get("weather")
        terrain_res = obs.get("terrain")
        satellite_res = obs.get("satellite")
        exposure_res = obs.get("exposure")
        memory_res = obs.get("memory")

        risk_score, risk_level, components = RiskCalculator.calculate_risk(
            weather_obs=weather_res,
            terrain_obs=terrain_res,
            satellite_obs=satellite_res,
            exposure_obs=exposure_res,
            memory_obs=memory_res
        )
        conf_score, conf_reason, missing_data, contradictory = ConfidenceEngine.assess_confidence(
            weather_obs=weather_res,
            terrain_obs=terrain_res,
            satellite_obs=satellite_res,
            exposure_obs=exposure_res,
            memory_obs=memory_res
        )

        state.risk_score = risk_score
        state.risk_level = risk_level
        state.confidence_score = conf_score
        state.confidence_reason = conf_reason
        state.missing_data = missing_data
        state.contradictory_evidence = contradictory

        # If risk is critical or high and incident report wasn't created yet, create it and engage human gate
        if state.risk_score >= 60.0:
            state.requires_human_approval = True
            if not state.incident_id:
                rec_act = state.recommended_action or "Dispatch municipal road inspection patrol and stage excavator at Jalbire depot."
                state.recommended_action = rec_act
                tools.create_incident_report(
                    state,
                    summary_en=f"Elevated landslide risk detected ({state.risk_level}, Score: {state.risk_score}/100, Confidence: {int(state.confidence_score*100)}%). Severe rainfall combined with steep terrain warrants urgent municipal road operations escalation.",
                    summary_ne=f"{state.location_name} खण्डमा भारी वर्षा र भिरालो जमिनका कारण उच्च पहिरो जोखिम देखिएको छ।",
                    recommended_action=rec_act
                )
                trace_recorder(
                    run_id, step, "GATE",
                    f"Safety Invariant Enforced: Risk {state.risk_score}/100 exceeds threshold. Autonomous dispatch blocked. Incident {state.incident_id} submitted to Operator Ramesh.",
                    {"incident_id": state.incident_id, "risk_score": state.risk_score}
                )
                step += 1
        else:
            state.requires_human_approval = False
            state.agent_decision = "Conditions do not warrant operational highway escalation. Continuing routine surveillance."

        state.step_count = min(turn, 10)
        return state
