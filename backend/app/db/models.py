from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class LocationModel(BaseModel):
    id: str
    name: str
    corridor_code: str
    district: str
    municipality: str
    ward: int
    latitude: float
    longitude: float
    elevation_m: float
    baseline_slope_deg: float
    road_name: str
    critical_infrastructure: List[str] = Field(default_factory=list)

class ObservationModel(BaseModel):
    id: str
    run_id: str
    source_type: str
    provider_name: str
    is_synthetic: bool = False
    is_stale: bool = False
    data_freshness_minutes: int = 0
    payload: Dict[str, Any]
    recorded_at: Optional[str] = None

class RiskAssessmentModel(BaseModel):
    id: str
    run_id: str
    risk_score: float
    risk_level: str
    confidence_score: float
    confidence_reason: str
    rainfall_component: float
    terrain_component: float
    satellite_component: float
    exposure_component: float
    history_component: float
    missing_data: List[str] = Field(default_factory=list)
    contradictory_evidence: Optional[str] = None

class IncidentModel(BaseModel):
    id: str
    run_id: str
    location_id: str
    title: str
    status: str
    severity: str
    summary_en: str
    summary_ne: str
    recommended_action: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ApprovalRequest(BaseModel):
    operator_name: str
    action_type: str  # 'APPROVE', 'REJECT', 'REQUEST_MORE_EVIDENCE'
    operator_notes: Optional[str] = None

class TraceEventModel(BaseModel):
    step_number: int
    event_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str

class RunSummaryModel(BaseModel):
    run_id: str
    location: LocationModel
    trigger_type: str
    status: str
    step_count: int
    risk_assessment: Optional[RiskAssessmentModel] = None
    incident: Optional[IncidentModel] = None
    traces: List[TraceEventModel] = Field(default_factory=list)
    total_latency_ms: int = 0
    total_tokens: int = 0
    estimated_cost_npr: float = 0.0
    is_resilience_mode: bool = False
