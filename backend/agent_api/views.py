import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SensorNode, TelemetryLog, AgentRun
from .ml_detector import evaluate_landslide_risk
from .agent_runner import run_disaster_agent, resolve_human_gate

SENSOR_SEEDS = [
    {"sensor_id": "SNS-MUG-01", "location_name": "Jalbire (KM 24)", "latitude": 27.835, "longitude": 84.518, "slope_deg": 28.0, "ndvi": 0.42},
    {"sensor_id": "SNS-MUG-04", "location_name": "Char Kilo (KM 36)", "latitude": 27.842, "longitude": 84.521, "slope_deg": 48.0, "ndvi": 0.18},
    {"sensor_id": "SNS-MUG-09", "location_name": "Mugling Bazar (KM 42)", "latitude": 27.848, "longitude": 84.525, "slope_deg": 22.0, "ndvi": 0.55},
]


def _ensure_sensors():
    for s in SENSOR_SEEDS:
        SensorNode.objects.get_or_create(
            sensor_id=s["sensor_id"],
            defaults=s
        )


@api_view(['POST'])
def ingest_telemetry(request):
    _ensure_sensors()
    sensor_id = request.data.get("sensor_id", "SNS-MUG-04")
    slope = float(request.data.get("slope_deg", 46.0))
    rain_72h = float(request.data.get("rain_72h", 165.0))
    moisture = float(request.data.get("moisture", 92.0))
    ndvi = float(request.data.get("ndvi", 0.18))
    vib = float(request.data.get("acoustic_vib", 58.0))

    sensor, _ = SensorNode.objects.get_or_create(
        sensor_id=sensor_id,
        defaults={
            "location_name": "Char Kilo (KM 36)",
            "latitude": 27.842,
            "longitude": 84.521,
            "slope_deg": slope,
            "ndvi": ndvi
        }
    )

    ml_eval = evaluate_landslide_risk(slope=slope, rain_72h=rain_72h, moisture=moisture, ndvi=ndvi, vib=vib)

    TelemetryLog.objects.create(
        sensor=sensor,
        rain_72h=rain_72h,
        soil_moisture=moisture,
        acoustic_vib=vib,
        is_critical=ml_eval["is_critical"]
    )

    run_id = None
    if ml_eval["is_critical"]:
        active = AgentRun.objects.filter(status__in=["RUNNING", "AWAITING_APPROVAL"])
        if not active.exists():
            payload = {
                "slope_deg": slope,
                "rain_72h": rain_72h,
                "moisture": moisture,
                "ndvi": ndvi,
                "acoustic_vib": vib
            }
            run_id = run_disaster_agent(sensor, payload)

    return Response({
        "status": "ingested",
        "ml_evaluation": ml_eval,
        "agent_triggered": bool(run_id),
        "run_id": run_id
    })


@api_view(['GET'])
def get_run_trace(request, run_id):
    try:
        run = AgentRun.objects.get(id=run_id)
    except AgentRun.DoesNotExist:
        return Response({"error": "Run not found"}, status=404)

    traces = run.traces.order_by("step_index", "timestamp").values(
        "step_index", "step_type", "thought", "tool_name", "tool_args", "tool_result", "timestamp"
    )
    return Response({
        "run_id": str(run.id),
        "status": run.status,
        "confidence": run.confidence_score,
        "proposed_action": run.proposed_action,
        "total_tokens": run.total_tokens,
        "cost_npr": run.cost_npr,
        "traces": list(traces)
    })


@api_view(['POST'])
def resolve_gate(request, run_id):
    try:
        run = AgentRun.objects.get(id=run_id)
    except AgentRun.DoesNotExist:
        return Response({"error": "Run not found"}, status=404)

    approved = bool(request.data.get("approved", False))
    success = resolve_human_gate(run_id, approved)
    run.refresh_from_db()
    return Response({
        "success": success,
        "status": run.status
    })


@api_view(['GET'])
def get_sensors(request):
    _ensure_sensors()
    sensors = SensorNode.objects.filter(
        sensor_id__in=["SNS-MUG-01", "SNS-MUG-04", "SNS-MUG-09"]
    )
    data = []
    for s in sensors:
        last_log = TelemetryLog.objects.filter(sensor=s).order_by("-timestamp").first()
        data.append({
            "id": s.sensor_id,
            "location": s.location_name,
            "slope": s.slope_deg,
            "ndvi": s.ndvi,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "status": "active" if s.sensor_id == "SNS-MUG-04" else "normal",
            "last_moisture": last_log.soil_moisture if last_log else None,
            "last_vibration": last_log.acoustic_vib if last_log else None,
            "last_critical": last_log.is_critical if last_log else False,
        })
    return Response(data)


@api_view(['GET'])
def get_runs(request):
    runs = AgentRun.objects.order_by("-created_at")[:20]
    data = []
    for r in runs:
        data.append({
            "id": str(r.id),
            "status": r.status,
            "confidence": r.confidence_score,
            "total_tokens": r.total_tokens,
            "cost_npr": r.cost_npr,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "sensor": r.triggering_sensor.sensor_id if r.triggering_sensor else None,
        })
    return Response(data)