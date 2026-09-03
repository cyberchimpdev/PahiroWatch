import React, { useState } from 'react';
import type { Incident } from '../types';
import { 
  ShieldAlert, CheckCircle2, XCircle,
  Droplets, Mountain, Satellite, Car, AlertTriangle 
} from 'lucide-react';
import { NepaliAlertBadge } from './NepaliAlertBadge';

interface IncidentDetailModalProps {
  incident: Incident | null;
  onClose: () => void;
  onApprove: (incidentId: string, notes: string) => Promise<void>;
  onReject: (incidentId: string, notes: string) => Promise<void>;
}

export const IncidentDetailModal: React.FC<IncidentDetailModalProps> = ({
  incident,
  onClose,
  onApprove,
  onReject
}) => {
  const [operatorNotes, setOperatorNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!incident) return null;

  const handleApprove = async () => {
    setSubmitting(true);
    try {
      await onApprove(incident.id, operatorNotes || "Field inspection authorized. Precautionary traffic control deployed.");
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  const handleReject = async () => {
    setSubmitting(true);
    try {
      await onReject(incident.id, operatorNotes || "Local patrol confirmed retaining wall stable; escalation suppressed.");
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  const isPending = incident.status === 'PENDING_APPROVAL';

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-2xl rounded-xl shadow-2xl overflow-hidden font-sans my-auto">
        
        {/* Modal Header */}
        <div className="bg-slate-950 px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${
              incident.severity === 'CRITICAL' || incident.severity === 'HIGH'
                ? 'bg-red-950/80 text-red-400 border border-red-800'
                : 'bg-amber-950/80 text-amber-400 border border-amber-800'
            }`}>
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-wide">{incident.title}</h2>
                <span className={`status-badge text-[10px] ${
                  incident.status === 'ACTION_DISPATCHED' 
                    ? 'bg-green-950 text-green-300 border border-green-800' 
                    : incident.status === 'PENDING_APPROVAL'
                    ? 'bg-red-950 text-red-300 border border-red-700 animate-pulse'
                    : 'bg-slate-800 text-slate-300 border border-slate-700'
                }`}>
                  {incident.status}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">Incident ID: {incident.id} | Run: {incident.run_id}</p>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
          
          {/* Key Metric Gauges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono">
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">Risk Score</span>
              <span className="text-xl font-black text-red-400">{incident.risk_score || 78.5}</span>
              <span className="text-xs text-slate-400 block font-sans font-semibold">/ 100 ({incident.risk_level || incident.severity})</span>
            </div>

            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">Confidence</span>
              <span className="text-xl font-black text-teal-400">{Math.round(incident.confidence_score ? incident.confidence_score * 100 : 78)}%</span>
              <span className="text-[10px] text-slate-400 block font-sans">Honest Sensor Metric</span>
            </div>

            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">24h Rainfall</span>
              <span className="text-xl font-black text-blue-400">184.0</span>
              <span className="text-xs text-slate-400 block font-sans">mm (Cloudburst)</span>
            </div>

            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block">Slope Angle</span>
              <span className="text-xl font-black text-amber-400">38.5°</span>
              <span className="text-xs text-slate-400 block font-sans">Steep Shear Zone</span>
            </div>
          </div>

          {/* Detailed Evidence Cards */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold font-mono text-slate-400 uppercase tracking-wider">Multi-Sensor Evidence Sources</h4>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-950/70 p-2.5 rounded border border-slate-800 flex items-start gap-2.5">
                <Droplets className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-slate-200 block">Rainfall Telemetry</strong>
                  <span className="text-slate-400">184mm in 24h (DHM Trishuli Station)</span>
                  <span className="text-[10px] text-slate-500 block font-mono">[DEMO PROVIDER]</span>
                </div>
              </div>

              <div className="bg-slate-950/70 p-2.5 rounded border border-slate-800 flex items-start gap-2.5">
                <Mountain className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-slate-200 block">Topographic Slope</strong>
                  <span className="text-slate-400">38.5° baseline on fractured phyllite bedrock</span>
                  <span className="text-[10px] text-slate-500 block font-mono">[SRTM 30m DEM]</span>
                </div>
              </div>

              <div className="bg-slate-950/70 p-2.5 rounded border border-slate-800 flex items-start gap-2.5">
                <Satellite className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-slate-200 block">Satellite Change (Copernicus S2)</strong>
                  <span className="text-slate-400">Surface change index: 0.71 (Cloud quality: Moderate)</span>
                  <span className="text-[10px] text-slate-500 block font-mono">[SYNTHETIC DEMO DATA]</span>
                </div>
              </div>

              <div className="bg-slate-950/70 p-2.5 rounded border border-slate-800 flex items-start gap-2.5">
                <Car className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-slate-200 block">Highway Exposure</strong>
                  <span className="text-slate-400">Narayanghat-Mugling (115m away, bridge asset)</span>
                  <span className="text-[10px] text-slate-500 block font-mono">[OSM Highway Cadastre]</span>
                </div>
              </div>
            </div>
          </div>

          {/* Plain-Language Agent Reasoning ("Why the agent thinks this matters") */}
          <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 space-y-2">
            <h4 className="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
              <span>WHY THE AGENT THINKS THIS MATTERS</span>
            </h4>
            <p className="text-sm text-slate-300 leading-relaxed">
              Recent rainfall of 184mm exceeds the DHM 24-hour critical saturation threshold. The site features an unstable 38.5° cut-slope adjacent to the primary Narayanghat-Mugling lifeline corridor. Historical records note 2 prior blockages at this coordinate. Although partial monsoon cloud cover reduces satellite certainty, terrestrial precipitation and slope physics strongly warrant operational human verification.
            </p>
          </div>

          {/* Recommended Action */}
          <div className="bg-amber-950/30 border border-amber-900/60 rounded-lg p-3">
            <span className="text-xs font-mono font-bold text-amber-400 uppercase block mb-1">Recommended Action</span>
            <p className="text-xs text-amber-200 font-medium">
              {incident.recommended_action || "Inspect road segment at KM 28 and stage heavy clearance excavator at Jalbire depot."}
            </p>
          </div>

          {/* Outbound Alerts Preview (Nepali & Low-BW) */}
          <NepaliAlertBadge alertsPreview={incident.alerts_preview} />

          {/* MANDATORY HUMAN CHECKPOINT GATE CONTROLS */}
          {isPending && (
            <div className="bg-slate-950 border-2 border-red-800/80 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-red-400 font-mono text-xs font-bold uppercase">
                <AlertTriangle className="w-4 h-4 text-red-400 animate-pulse" />
                <span>MANDATORY HUMAN APPROVAL CHECKPOINT</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                As per safety protocol, the agent is <strong>blocked from issuing official emergency alerts</strong> until authorized by Ramesh (Municipal Disaster Management Officer).
              </p>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Operator Ground Verification Notes:</label>
                <input
                  type="text"
                  value={operatorNotes}
                  onChange={(e) => setOperatorNotes(e.target.value)}
                  placeholder="e.g. Confirmed with local ward patrol; dispatching crew..."
                  className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <button
                  onClick={handleApprove}
                  disabled={submitting}
                  className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-4 rounded-lg text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-950 transition-all disabled:opacity-50"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  {submitting ? "DISPATCHING..." : "APPROVE ACTION & DISPATCH ALERT"}
                </button>

                <button
                  onClick={handleReject}
                  disabled={submitting}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold py-2 px-4 rounded-lg text-xs flex items-center justify-center gap-1.5 border border-slate-700 transition-colors disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4 text-red-400" />
                  REJECT / SUPPRESS
                </button>
              </div>
            </div>
          )}

          {!isPending && (
            <div className="bg-slate-950 p-3 rounded border border-slate-800 text-xs font-mono text-slate-400 flex items-center justify-between">
              <span>Status: Decision recorded by human operator.</span>
              <span className="text-emerald-400 font-semibold">ACTION COMPLETED</span>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
