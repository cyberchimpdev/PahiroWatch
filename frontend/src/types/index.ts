export interface Location {
  id: string;
  name: string;
  corridor_code: string;
  district: string;
  municipality: string;
  ward: number;
  latitude: number;
  longitude: number;
  elevation_m: number;
  baseline_slope_deg: number;
  road_name: string;
  critical_infrastructure: string[];
}

export interface Observation {
  source_type: string;
  provider_name: string;
  is_synthetic: boolean;
  is_stale: boolean;
  data_freshness_minutes?: number;
  payload: Record<string, any>;
}

export interface RiskAssessment {
  id?: string;
  run_id?: string;
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  confidence_score: number;
  confidence_reason: string;
  rainfall_component: number;
  terrain_component: number;
  satellite_component: number;
  exposure_component: number;
  history_component: number;
  missing_data: string[];
  contradictory_evidence?: string | null;
}

export interface Incident {
  id: string;
  run_id: string;
  location_id: string;
  location_name?: string;
  corridor_code?: string;
  latitude?: number;
  longitude?: number;
  title: string;
  status: 'PENDING_APPROVAL' | 'ACTIVE_MONITORING' | 'ACTION_DISPATCHED' | 'RESOLVED' | 'DISMISSED';
  severity: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  summary_en: string;
  summary_ne: string;
  recommended_action: string;
  created_at?: string;
  risk_score?: number;
  risk_level?: string;
  confidence_score?: number;
  confidence_reason?: string;
  observations?: Observation[];
  critical_infrastructure?: string[];
  missing_data?: string[];
  alerts_preview?: {
    payload_en: string;
    payload_ne: string;
    payload_sms_compact: string;
  };
}

export interface TraceEvent {
  id: number;
  step_number: number;
  event_type: 'TRIGGER' | 'GOAL' | 'PLAN' | 'TOOL_CALL' | 'TOOL_RESULT' | 'MEMORY' | 'DECISION' | 'CONFIDENCE' | 'GATE' | 'HUMAN' | 'ACTION' | 'DONE';
  content: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface CorridorStatus {
  corridor_code: string;
  corridor_name: string;
  jurisdiction: string;
  operator: string;
  agent_status: string;
  latest_run?: {
    id: string;
    location_id: string;
    trigger_type: string;
    status: string;
    started_at: string;
    step_count: number;
    total_latency_ms: number;
    total_tokens: number;
    estimated_cost_npr: number;
    is_resilience_mode: boolean;
    risk_score?: number;
    risk_level?: string;
    confidence_score?: number;
    confidence_reason?: string;
  };
  active_incidents: Incident[];
  total_monitored_segments: number;
}

export interface AgentMetrics {
  total_runs: number;
  total_tokens: number;
  total_cost_npr: number;
  avg_latency_ms: number;
  resilience_runs: number;
  total_incidents: number;
  total_human_approvals: number;
  cost_per_run_npr: number;
}
