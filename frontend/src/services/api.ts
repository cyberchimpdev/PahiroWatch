const API_BASE = import.meta.env.VITE_API_BASE || '/api';

export async function fetchJson(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`API Error ${res.status}: ${errorBody || res.statusText}`);
  }
  return res.json();
}

export const api = {
  getLocations: () => fetchJson('/locations'),
  getCorridorStatus: () => fetchJson('/corridor/status'),
  getIncidents: (status?: string) => fetchJson(`/incidents${status ? `?status=${status}` : ''}`),
  getIncidentDetail: (id: string) => fetchJson(`/incidents/${id}`),
  approveIncident: (id: string, operator_name: string, operator_notes?: string) =>
    fetchJson(`/incidents/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ operator_name, operator_notes }),
    }),
  rejectIncident: (id: string, operator_name: string, operator_notes?: string) =>
    fetchJson(`/incidents/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ operator_name, operator_notes }),
    }),
  getTrace: (run_id?: string) => fetchJson(`/agent/trace${run_id ? `?run_id=${run_id}` : ''}`),
  getMetrics: () => fetchJson('/agent/metrics'),
  getPastRuns: () => fetchJson('/agent/runs'),
  
  // Scenarios
  runMonsoonScenario: (location_id?: string) =>
    fetchJson(`/scenarios/monsoon${location_id ? `?location_id=${location_id}` : ''}`, { method: 'POST' }),
  runLowConfidenceScenario: (location_id?: string) =>
    fetchJson(`/scenarios/low-confidence${location_id ? `?location_id=${location_id}` : ''}`, { method: 'POST' }),
  runBadDayScenario: (location_id?: string) =>
    fetchJson(`/scenarios/bad-day${location_id ? `?location_id=${location_id}` : ''}`, { method: 'POST' }),
  triggerRun: (location_id: string) =>
    fetchJson(`/monitor/run?location_id=${location_id}&trigger_type=MANUAL_DISPATCH`, { method: 'POST' }),
};
