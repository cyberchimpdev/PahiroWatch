import uuid
from django.db import models


class SensorNode(models.Model):
    sensor_id = models.CharField(max_length=50, unique=True)
    location_name = models.CharField(max_length=100)
    latitude = models.FloatField(default=27.842)
    longitude = models.FloatField(default=84.521)
    slope_deg = models.FloatField(default=45.0)
    ndvi = models.FloatField(default=0.18)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sensor_id} - {self.location_name}"


class TelemetryLog(models.Model):
    sensor = models.ForeignKey(SensorNode, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    rain_72h = models.FloatField(default=0.0)
    soil_moisture = models.FloatField()
    acoustic_vib = models.FloatField()
    is_critical = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']


class AgentRun(models.Model):
    STATUS_CHOICES = [
        ("RUNNING", "Running"),
        ("AWAITING_APPROVAL", "Awaiting Human Approval"),
        ("EXECUTED", "Action Executed"),
        ("REJECTED", "Action Rejected"),
        ("FAILED", "Failed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="RUNNING")
    triggering_sensor = models.ForeignKey(
        SensorNode, on_delete=models.SET_NULL, null=True
    )
    proposed_action = models.JSONField(null=True, blank=True)
    confidence_score = models.FloatField(default=0.0)
    total_tokens = models.IntegerField(default=0)
    cost_npr = models.FloatField(default=0.0)

    def __str__(self):
        return f"Run {self.id} - {self.status}"


class AgentTraceStep(models.Model):
    run = models.ForeignKey(AgentRun, related_name="traces", on_delete=models.CASCADE)
    step_index = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    step_type = models.CharField(max_length=20)  # PLAN, TOOL_CALL, TOOL_RESULT, GATE, ACTION, ERROR
    thought = models.TextField(blank=True, null=True)
    tool_name = models.CharField(max_length=100, blank=True, null=True)
    tool_args = models.JSONField(blank=True, null=True)
    tool_result = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['step_index']