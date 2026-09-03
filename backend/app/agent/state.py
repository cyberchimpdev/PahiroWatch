from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentState(BaseModel):
    run_id: str
    location_id: str
    location_name: str
    latitude: float
    longitude: float
    baseline_slope: float
    elevation_m: float
    goal: str
    step_count: int = 0
    max_steps: int = 10
    trigger_type: str = "SCHEDULED"
    plan: List[str] = Field(default_factory=list)
    observations: Dict[str, Any] = Field(default_factory=dict)
    tool_history: List[Dict[str, Any]] = Field(default_factory=list)
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    confidence_score: Optional[float] = None
    confidence_reason: Optional[str] = None
    missing_data: List[str] = Field(default_factory=list)
    contradictory_evidence: Optional[str] = None
    historical_context: Optional[Dict[str, Any]] = None
    agent_decision: Optional[str] = None
    recommended_action: Optional[str] = None
    requires_human_approval: bool = False
    approval_status: str = "PENDING"  # 'PENDING', 'APPROVED', 'REJECTED'
    incident_id: Optional[str] = None
    alert_sent: bool = False
    tokens_used: int = 0
    cost_npr: float = 0.0
    latency_ms: int = 0
    retries_count: int = 0
    is_resilience_mode: bool = False
    scenario_override: Optional[str] = None
