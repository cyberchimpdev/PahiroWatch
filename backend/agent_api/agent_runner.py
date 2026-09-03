import os
import json
import logging
from openai import OpenAI
from .models import AgentRun, AgentTraceStep, SensorNode
from .tools import TOOLS_SCHEMA, execute_tool
from .ml_detector import evaluate_landslide_risk

logger = logging.getLogger(__name__)

AZURE_ENDPOINT = os.environ.get(
    "HACKATHON_ENDPOINT",
    "https://hackathon-2026-2-resource.openai.azure.com/openai/v1/"
)
AZURE_KEY = os.environ.get("HACKATHON_KEY", "")
MODEL = os.environ.get("HACKATHON_MODEL", "gpt-5.5")
MAX_STEPS = 10
HUMAN_GATE = "tool_stage_emergency_dispatch"


def _get_client():
    if not AZURE_KEY:
        return None
    return OpenAI(base_url=AZURE_ENDPOINT, api_key=AZURE_KEY)


def run_disaster_agent(sensor, telemetry_data):
    run = AgentRun.objects.create(status="RUNNING", triggering_sensor=sensor)

    messages = [
        {
            "role": "system",
            "content": (
                "You are BhumiSense Coordinator, an autonomous geo-disaster intelligence agent "
                "for Nepal's Narayanghat-Mugling highway corridor. You monitor 3 highway geo-sensors "
                "along the corridor (Jalbire KM24, Char Kilo KM36, Mugling Bazar KM42). "
                "Your workflow:\n"
                "1. Call tool_run_landslide_susceptibility_model to verify physical slope failure probability.\n"
                "2. Call tool_check_highway_traffic to measure human exposure in the corridor sector.\n"
                "3. If slope probability exceeds 0.70, IMMEDIATELY invoke tool_stage_emergency_dispatch with "
                "target_ward set to the appropriate Rural Municipality ward, a Nepali SMS advisory, "
                "and a recommended detour route.\n"
                "4. If probability is below 0.70, report findings and recommend continued monitoring.\n"
                "Always reference specific landmarks (Jalbire, Char Kilo, Mugling, Mugling-Narayanghat corridor). "
                "Write actionable Nepali advisories. Keep steps minimal and bounded."
            )
        },
        {
            "role": "user",
            "content": (
                "INCIDENT: Sensor " + sensor.sensor_id + " (" + sensor.location_name + ") reports critical movement.\n"
                "Slope=" + str(telemetry_data.get("slope_deg", 45.0)) + " degrees\n"
                "72h Rain=" + str(telemetry_data.get("rain_72h", 160.0)) + "mm\n"
                "Moisture=" + str(telemetry_data.get("moisture", 90.0)) + "%\n"
                "NDVI=" + str(telemetry_data.get("ndvi", 0.18)) + "\n"
                "Vibration=" + str(telemetry_data.get("acoustic_vib", 55.0)) + "Hz\n\n"
                "Investigate the risk level, check traffic exposure, and stage emergency response if warranted."
            )
        }
    ]

    total_tokens = 0
    client = _get_client()

    if client is None:
        return _execute_offline_fallback(run, telemetry_data, 0, "No API key configured")

    for step in range(MAX_STEPS):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=1024
            )
        except Exception as e:
            logger.warning("Cloud API error at step %d: %s", step, str(e))
            return _execute_offline_fallback(run, telemetry_data, step, str(e))

        usage = response.usage
        if usage:
            total_tokens += usage.total_tokens

        choice = response.choices[0].message

        if choice.content:
            AgentTraceStep.objects.create(
                run=run, step_index=step, step_type="PLAN",
                thought=choice.content
            )

        if not choice.tool_calls:
            run.status = "EXECUTED"
            run.total_tokens = total_tokens
            run.cost_npr = round(total_tokens * 0.0003, 2)
            run.save()
            AgentTraceStep.objects.create(
                run=run, step_index=step, step_type="ACTION",
                thought="Agent concluded analysis. No emergency dispatch required."
            )
            return str(run.id)

        for tool_call in choice.tool_calls:
            t_name = tool_call.function.name
            t_args = json.loads(tool_call.function.arguments)

            AgentTraceStep.objects.create(
                run=run, step_index=step, step_type="TOOL_CALL",
                tool_name=t_name, tool_args=t_args
            )

            if t_name == HUMAN_GATE:
                run.status = "AWAITING_APPROVAL"
                run.proposed_action = t_args
                run.confidence_score = float(t_args.get("confidence_score", 0.88))
                run.total_tokens = total_tokens
                run.cost_npr = round(total_tokens * 0.0003, 2)
                run.save()
                AgentTraceStep.objects.create(
                    run=run, step_index=step, step_type="GATE",
                    thought="HUMAN CHECKPOINT: High-consequence dispatch halted for Incident Commander authorization."
                )
                return str(run.id)

            result_str = execute_tool(t_name, json.dumps(t_args))
            AgentTraceStep.objects.create(
                run=run, step_index=step, step_type="TOOL_RESULT",
                tool_name=t_name, tool_args=t_args, tool_result=result_str
            )
            messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result_str})

    run.status = "EXECUTED"
    run.total_tokens = total_tokens
    run.cost_npr = round(total_tokens * 0.0003, 2)
    run.save()
    AgentTraceStep.objects.create(
        run=run, step_index=MAX_STEPS, step_type="ACTION",
        thought="Agent reached step limit. Analysis complete."
    )
    return str(run.id)


def _execute_offline_fallback(run, telemetry_data, step, error_msg):
    local_eval = evaluate_landslide_risk(
        slope=telemetry_data.get("slope_deg", 45.0),
        rain_72h=telemetry_data.get("rain_72h", 160.0),
        moisture=telemetry_data.get("moisture", 90.0),
        ndvi=telemetry_data.get("ndvi", 0.18),
        vib=telemetry_data.get("acoustic_vib", 55.0)
    )
    run.status = "AWAITING_APPROVAL"
    run.confidence_score = 0.50
    run.proposed_action = {
        "target_ward": "Ichhyakamana Rural Municipality Ward 4",
        "sms_payload_nepali": "आपतकालीन सूचना: चार किलो क्षेत्रमा पहिरोको उच्च जोखिम छ। मुग्लिन-नारायणगढ सडक तत्काल बन्द गरिएको छ।",
        "divert_checkpoints": True,
        "recommended_detour": "Hetauda - Kanti Lokpath",
        "confidence_score": 0.50
    }
    run.total_tokens = 0
    run.cost_npr = 0.0
    run.save()
    AgentTraceStep.objects.create(
        run=run, step_index=step, step_type="ERROR",
        thought="Cloud API unreachable (" + error_msg + "). Offline Random Forest fallback executed. Probability: " + str(local_eval["probability"])
    )
    AgentTraceStep.objects.create(
        run=run, step_index=step + 1, step_type="GATE",
        thought="HUMAN CHECKPOINT [OFFLINE FAILSAFE]: Fallback action staged for approval. Severity: " + local_eval["severity"]
    )
    return str(run.id)


def resolve_human_gate(run_id, approved):
    run = AgentRun.objects.get(id=run_id)
    if approved:
        run.status = "EXECUTED"
        run.save()
        action = run.proposed_action or {}
        ward = str(action.get("target_ward", "Ward 4"))
        detour = str(action.get("recommended_detour", "Hetauda"))
        AgentTraceStep.objects.create(
            run=run, step_index=99, step_type="ACTION",
            thought="CONSEQUENCE EXECUTED: SMS broadcast dispatched to " + ward + ". Checkpoint barriers closed for " + detour + " route."
        )
        return True
    else:
        run.status = "REJECTED"
        run.save()
        AgentTraceStep.objects.create(
            run=run, step_index=99, step_type="ACTION",
            thought="ACTION CANCELLED: Incident Commander rejected emergency dispatch."
        )
        return False