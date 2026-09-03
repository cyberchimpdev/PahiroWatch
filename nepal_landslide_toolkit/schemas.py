"""
Nepal Landslide Risk Agent Toolkit — Schemas
Standardized observation, trace, and alert models for community disaster AI.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class RainfallObservation(BaseModel):
    rainfall_1h_mm: float
    rainfall_6h_mm: float
    rainfall_24h_mm: float
    rainfall_72h_mm: float
    timestamp: str
    source: str
    freshness_minutes: int
    data_quality: str
    is_synthetic: bool = False
    is_stale: bool = False

class TerrainProfile(BaseModel):
    elevation_m: float
    slope_deg: float
    aspect_cardinal: str
    terrain_risk_score: float
    hazard_level: str
    source: str
    resolution: str

class SatelliteChangeMetric(BaseModel):
    change_score: float
    vegetation_loss_index: float
    surface_change_indicator: str
    cloud_cover_pct: float
    cloud_quality: str
    imagery_dates: Dict[str, str]
    source: str
    confidence: float
    is_synthetic: bool = False

class RoadExposureProfile(BaseModel):
    nearest_road: str
    road_class: str
    distance_to_road_m: float
    settlements_nearby: List[str]
    schools_nearby: List[str]
    critical_infrastructure: List[str]
    exposure_score: float
    exposure_level: str

class RiskAssessmentRecord(BaseModel):
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

class AgentTraceRecord(BaseModel):
    step_number: int
    event_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str
