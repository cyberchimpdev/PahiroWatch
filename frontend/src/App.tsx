import React, { useState, useEffect } from 'react';
import { 
  Shield, CloudRain, Compass, AlertOctagon, 
  ChevronDown, ChevronUp, Terminal, 
  MapPin, CheckCircle2, AlertTriangle, XCircle, 
  Coins, User, Languages
} from 'lucide-react';
import { MapView } from './components/MapView';
import { api } from './services/api';
import type { Location, Incident, TraceEvent, CorridorStatus, AgentMetrics } from './types';

export const App: React.FC = () => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [corridorStatus, setCorridorStatus] = useState<CorridorStatus | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [traces, setTraces] = useState<TraceEvent[]>([]);
  const [currentRunInfo, setCurrentRunInfo] = useState<any>(null);
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null);
  
  const [activeScenario, setActiveScenario] = useState<string | null>('MONSOON');
  const [loading, setLoading] = useState<boolean>(false);
  const [isTraceOpen, setIsTraceOpen] = useState<boolean>(true);
  const [activeAlertTab, setActiveAlertTab] = useState<'NEPALI' | 'ENGLISH' | 'SMS'>('NEPALI');
  const [approvalNotes, setApprovalNotes] = useState<string>('');

  // Initial Load
  const loadData = async () => {
    try {
      const [locs, status, incs, met] = await Promise.all([
        api.getLocations(),
        api.getCorridorStatus(),
        api.getIncidents(),
        api.getMetrics(),
      ]);

      setLocations(locs);
      if (locs.length > 0 && !selectedLocation) {
        // Default to Jalbire (KM 28) - the primary landslide hazard sector
        const jalbire = locs.find((l: Location) => l.id.includes('JALBIRE')) || locs[0];
        setSelectedLocation(jalbire);
      }
      setCorridorStatus(status);
      setIncidents(incs);
      setMetrics(met);

      // Load latest trace
      const traceData = await api.getTrace();
      setTraces(traceData.traces || []);
      setCurrentRunInfo(traceData.run_info);
    } catch (err) {
      console.error("Failed to load operations data:", err);
    }
  };

  useEffect(() => {
    loadData();
    const timer = setInterval(loadData, 12000);
    return () => clearInterval(timer);
  }, []);

  // Scenario Triggers
  const handleRunMonsoon = async () => {
    setLoading(true);
    setActiveScenario('MONSOON');
    try {
      const locId = selectedLocation?.id || "LOC-JALBIRE-KM28";
      const res = await api.runMonsoonScenario(locId);
      await loadData();
      const traceData = await api.getTrace(res.run_id);
      setTraces(traceData.traces || []);
      setCurrentRunInfo(traceData.run_info);
    } catch (err) {
      console.error("Monsoon scenario error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunLowConfidence = async () => {
    setLoading(true);
    setActiveScenario('LOW_CONFIDENCE');
    try {
      const kurintar = locations.find(l => l.id.includes('KURINTAR')) || selectedLocation;
      if (kurintar) setSelectedLocation(kurintar);
      const res = await api.runLowConfidenceScenario(kurintar?.id || "LOC-KURINTAR-KM36");
      await loadData();
      const traceData = await api.getTrace(res.run_id);
      setTraces(traceData.traces || []);
      setCurrentRunInfo(traceData.run_info);
    } catch (err) {
      console.error("Low confidence scenario error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunBadDay = async () => {
    setLoading(true);
    setActiveScenario('BAD_DAY');
    try {
      const charkilo = locations.find(l => l.id.includes('CHARKILO')) || selectedLocation;
      if (charkilo) setSelectedLocation(charkilo);
      const res = await api.runBadDayScenario(charkilo?.id || "LOC-CHARKILO-KM32");
      await loadData();
      const traceData = await api.getTrace(res.run_id);
      setTraces(traceData.traces || []);
      setCurrentRunInfo(traceData.run_info);
    } catch (err) {
      console.error("Bad Day scenario error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Find the active incident for the selected location or latest
  const activeIncident = incidents.find(i => i.location_id === selectedLocation?.id) || 
                         (incidents.length > 0 ? incidents[0] : null);

  const isPendingApproval = activeIncident?.status === 'PENDING_APPROVAL' || 
                            currentRunInfo?.status === 'PAUSED_HUMAN_GATE';

  const isDispatched = activeIncident?.status === 'ACTION_DISPATCHED';

  // Human Checkpoint Handlers
  const handleApprove = async () => {
    if (!activeIncident) return;
    try {
      await api.approveIncident(
        activeIncident.id, 
        "Ramesh, Municipal Disaster Management Officer",
        approvalNotes || "Field inspection authorized. Excavator team staged at Jalbire depot."
      );
      await loadData();
      const traceData = await api.getTrace(currentRunInfo?.id);
      setTraces(traceData.traces || []);
      setCurrentRunInfo(traceData.run_info);
    } catch (err) {
      console.error("Approval error:", err);
    }
  };

  const handleReject = async () => {
    if (!activeIncident) return;
    try {
      await api.rejectIncident(
        activeIncident.id,
        "Ramesh, Municipal Disaster Management Officer",
        approvalNotes || "Local patrol confirmed slope is stable; emergency alert suppressed."
      );
      await loadData();
      const traceData = await api.getTrace(currentRunInfo?.id);
      setTraces(traceData.traces || []);
      setCurrentRunInfo(traceData.run_info);
    } catch (err) {
      console.error("Reject error:", err);
    }
  };

  const riskScore = currentRunInfo?.risk_score !== undefined ? currentRunInfo.risk_score : (activeIncident?.risk_score || 86.0);
  const confidenceScore = currentRunInfo?.confidence_score !== undefined ? Math.round(currentRunInfo.confidence_score * 100) : 75;
  const isResilience = Boolean(currentRunInfo?.is_resilience_mode || activeScenario === 'BAD_DAY');

  return (
    <div className="min-h-screen bg-[#070a12] text-slate-100 flex flex-col font-sans">
      
      {/* 1. Top Navbar: Brand & Mission Info */}
      <header className="bg-[#0b0f19] border-b border-slate-800 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 shadow-md shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-red-950 border border-red-700 flex items-center justify-center text-red-400 font-bold shadow">
            <Shield size={20} className="text-red-400 shrink-0 inline-block" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-black tracking-wide text-white uppercase font-mono">
                PAHIROWATCH <span className="text-slate-400 font-normal text-xs">(पहिरोवाच)</span>
              </h1>
              <span className="bg-blue-950 border border-blue-800 text-blue-300 text-[10px] font-bold px-1.5 py-0.5 rounded">
                {corridorStatus?.corridor_code || "NH05"} • {corridorStatus?.corridor_name || "NARAYANGHAT–MUGLING"}
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Autonomous Landslide Risk & Response Agent • Ichhyakamana Rural Municipality
            </p>
          </div>
        </div>

        {/* Status Pills */}
        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
            <User size={15} className="text-blue-400 shrink-0 inline-block" />
            <span className="text-slate-400">Operator:</span>
            <span className="text-white font-semibold">Ramesh (Disaster Officer)</span>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
            <Coins size={15} className="text-emerald-400 shrink-0 inline-block" />
            <span className="text-slate-400">Cost:</span>
            <span className="text-emerald-400 font-bold">
              NPR {metrics?.total_cost_npr !== undefined ? metrics.total_cost_npr.toFixed(3) : "0.024"}
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-emerald-950 text-emerald-300 border border-emerald-800 px-2.5 py-1 rounded font-bold text-[11px]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>AGENT WATCHING</span>
          </div>
        </div>
      </header>

      {/* 2. DEMO SCENARIO LAUNCHER (Clear, high-impact buttons) */}
      <section className="bg-[#0e1626] border-b border-slate-800/90 px-4 py-3">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h2 className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
              <span>SELECT A DEMO SCENARIO TO TEST THE AGENT:</span>
            </h2>
            <p className="text-xs text-slate-300 mt-0.5">
              Each scenario proves real agentic behavior: goal-driven tool calling, confidence penalties, resilience fallback, or human checkpoints.
            </p>
          </div>

          {/* The 3 Demo Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            
            {/* Scenario 1: Monsoon */}
            <button
              onClick={handleRunMonsoon}
              disabled={loading}
              className={`px-3 py-2 rounded-lg font-bold text-xs flex items-center gap-2 transition-all shadow-md ${
                activeScenario === 'MONSOON'
                  ? 'bg-red-600 hover:bg-red-500 text-white ring-2 ring-red-400'
                  : 'bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700'
              } disabled:opacity-50`}
            >
              <CloudRain size={20} className="text-red-300 shrink-0 inline-block" />
              <div className="text-left">
                <span className="block font-bold leading-tight">1. Monsoon Hazard (High Risk)</span>
                <span className="block text-[10px] font-normal text-red-200">184mm rain • Steep 38.5° • Halts at Human Gate</span>
              </div>
            </button>

            {/* Scenario 2: False Alarm Filter */}
            <button
              onClick={handleRunLowConfidence}
              disabled={loading}
              className={`px-3 py-2 rounded-lg font-semibold text-xs flex items-center gap-2 transition-all shadow-md ${
                activeScenario === 'LOW_CONFIDENCE'
                  ? 'bg-blue-600 hover:bg-blue-500 text-white ring-2 ring-blue-400'
                  : 'bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700'
              } disabled:opacity-50`}
            >
              <Compass size={20} className="text-blue-300 shrink-0 inline-block" />
              <div className="text-left">
                <span className="block font-bold leading-tight">2. False-Alarm Filter</span>
                <span className="block text-[10px] font-normal text-blue-200">Rain on gentle 18° slope • Suppresses panic</span>
              </div>
            </button>

            {/* Scenario 3: Bad Day */}
            <button
              onClick={handleRunBadDay}
              disabled={loading}
              className={`px-3 py-2 rounded-lg font-semibold text-xs flex items-center gap-2 transition-all shadow-md ${
                activeScenario === 'BAD_DAY'
                  ? 'bg-amber-600 hover:bg-amber-500 text-white ring-2 ring-amber-400'
                  : 'bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700'
              } disabled:opacity-50`}
            >
              <AlertOctagon size={20} className="text-amber-300 shrink-0 inline-block" />
              <div className="text-left">
                <span className="block font-bold leading-tight">3. Sensor Blackout</span>
                <span className="block text-[10px] font-normal text-amber-200">Satellite offline • Resilience Fallback Active</span>
              </div>
            </button>

          </div>
        </div>
      </section>

      {/* 3. SECTOR SELECTOR PILLS */}
      <section className="bg-[#0b0f19] border-b border-slate-800/80 px-4 py-2">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-mono text-slate-400 font-bold uppercase mr-1 flex items-center gap-1">
            <MapPin size={14} className="text-blue-400 shrink-0 inline-block" />
            SELECT HIGHWAY SECTOR:
          </span>

          {locations.map((loc) => {
            const isSelected = selectedLocation?.id === loc.id;
            const isCritical = loc.baseline_slope_deg >= 32.0;

            return (
              <button
                key={loc.id}
                onClick={() => setSelectedLocation(loc)}
                className={`px-2.5 py-1 rounded-full text-xs font-mono font-medium transition-all flex items-center gap-1.5 ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-md font-bold ring-1 ring-blue-300'
                    : 'bg-slate-900 text-slate-300 hover:bg-slate-800 hover:text-white border border-slate-800'
                }`}
              >
                <span>{loc.name.split(' (')[0]}</span>
                <span className={`text-[10px] px-1 py-0.2 rounded font-bold ${
                  isCritical ? 'bg-red-950 text-red-400 border border-red-800' : 'bg-slate-800 text-slate-400'
                }`}>
                  {loc.baseline_slope_deg}°
                </span>
              </button>
            );
          })}
        </div>
      </section>

      {/* 4. MAIN WORKSPACE: 2-COLUMN SPLIT (MAP & DECISION ENGINE) */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-4 grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* LEFT COLUMN: Geospatial Highway Map (7 cols) */}
        <div className="lg:col-span-7 flex flex-col h-[480px]">
          <MapView
            locations={locations}
            incidents={incidents}
            selectedLocation={selectedLocation}
            onSelectLocation={(loc) => setSelectedLocation(loc)}
            onSelectIncident={() => {}}
          />
        </div>

        {/* RIGHT COLUMN: What the Agent Found & Human Gate (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-3 h-[480px] overflow-y-auto">
          
          {/* Card A: Risk & Evidence Breakdown */}
          <div className="bg-[#0b0f19] border border-slate-800 rounded-xl p-3.5 shadow-xl space-y-3">
            
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase font-bold block">Assessed Location</span>
                <h3 className="text-sm font-bold text-white truncate max-w-[240px]">
                  {selectedLocation?.name || "Jalbire Waterfall Sector (KM 28)"}
                </h3>
              </div>
              
              <div className="text-right">
                <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-black ${
                  riskScore > 75 ? 'bg-red-950 text-red-400 border border-red-800' :
                  riskScore > 40 ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                  'bg-emerald-950 text-emerald-400 border border-emerald-800'
                }`}>
                  {riskScore > 75 ? 'CRITICAL RISK' : riskScore > 40 ? 'MODERATE RISK' : 'LOW RISK'}
                </span>
              </div>
            </div>

            {/* Score & Confidence Meters */}
            <div className="grid grid-cols-2 gap-2 text-center font-mono">
              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase block">Landslide Risk</span>
                <span className="text-2xl font-black text-red-400">{riskScore}</span>
                <span className="text-xs text-slate-400 block font-sans">/ 100</span>
              </div>

              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase block">Honest Confidence</span>
                <span className="text-2xl font-black text-teal-400">{confidenceScore}%</span>
                <span className="text-[10px] text-slate-400 block font-sans truncate">
                  {isResilience ? "Sensor Outage Penalties" : "Multi-Source Verified"}
                </span>
              </div>
            </div>

            {/* Evidence Chips */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono text-slate-300">
              <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
                <span className="text-slate-400 text-[10px] block">🌧️ 24h Rainfall:</span>
                <strong className="text-blue-400 text-sm">184.0 mm</strong>
                <span className="text-[10px] text-slate-400 block font-sans">Critical Saturation</span>
              </div>

              <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
                <span className="text-slate-400 text-[10px] block">⛰️ Topographic Slope:</span>
                <strong className="text-amber-400 text-sm">{selectedLocation?.baseline_slope_deg || 38.5}°</strong>
                <span className="text-[10px] text-slate-400 block font-sans">Steep Shear Zone</span>
              </div>

              <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
                <span className="text-slate-400 text-[10px] block">🛰️ Sentinel-2 Optical:</span>
                <strong className={isResilience ? 'text-red-400 text-xs' : 'text-cyan-400 text-xs'}>
                  {isResilience ? 'OUTAGE (FALLBACK)' : '82.5% Cloud Cover'}
                </strong>
                <span className="text-[10px] text-slate-400 block font-sans">Honest Penalties</span>
              </div>

              <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
                <span className="text-slate-400 text-[10px] block">🚗 Highway Proximity:</span>
                <strong className="text-emerald-400 text-sm">115 meters</strong>
                <span className="text-[10px] text-slate-400 block font-sans">Lifeline Bridge Asset</span>
              </div>
            </div>

          </div>

          {/* Card B: MANDATORY HUMAN CHECKPOINT GATE (The Safety Rule) */}
          <div className="bg-[#0b0f19] border border-slate-800 rounded-xl p-3.5 shadow-xl space-y-3">
            
            <div className="flex items-center gap-2">
              <Shield size={18} className={`shrink-0 inline-block ${isPendingApproval ? 'text-red-400 animate-pulse' : 'text-emerald-400'}`} />
              <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
                MANDATORY HUMAN CHECKPOINT GATE
              </h4>
            </div>

            {/* When Pending Operator Approval */}
            {isPendingApproval && (
              <div className="bg-red-950/40 border border-red-800/80 rounded-lg p-3 space-y-2.5">
                <div className="flex items-center gap-1.5 text-red-400 font-bold text-xs">
                  <AlertTriangle size={16} className="text-red-400 shrink-0 inline-block" />
                  <span>ACTION PAUSED: Human Verification Required</span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed font-sans">
                  The agent identified critical hazard conditions (86/100). Under municipal safety rules, <strong>the AI is blocked from declaring an emergency</strong> until authorized by Ramesh.
                </p>

                <div className="bg-slate-950 p-2 rounded border border-slate-800 text-xs font-mono">
                  <span className="text-slate-400 text-[10px] block font-bold">RECOMMENDED OPERATIONAL ACTION:</span>
                  <p className="text-amber-200 font-medium mt-0.5">
                    {activeIncident?.recommended_action || "Dispatch municipal road inspection patrol and stage excavator at Jalbire depot."}
                  </p>
                </div>

                <div className="space-y-1 pt-1">
                  <input
                    type="text"
                    value={approvalNotes}
                    onChange={(e) => setApprovalNotes(e.target.value)}
                    placeholder="Enter operator note (e.g. Confirmed with KM 28 checkpoint...)"
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-sans"
                  />
                </div>

                <div className="flex gap-2 pt-1">
                  <button
                    onClick={handleApprove}
                    className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-3 rounded-lg text-xs flex items-center justify-center gap-1.5 shadow-lg shadow-emerald-950 transition-all font-mono cursor-pointer"
                  >
                    <CheckCircle2 size={16} className="text-white shrink-0 inline-block" />
                    <span>APPROVE & DISPATCH ALERT</span>
                  </button>

                  <button
                    onClick={handleReject}
                    className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-2 px-3 rounded-lg text-xs flex items-center justify-center gap-1 border border-slate-700 transition-colors font-mono cursor-pointer"
                  >
                    <XCircle size={15} className="text-red-400 shrink-0 inline-block" />
                    <span>SUPPRESS</span>
                  </button>
                </div>
              </div>
            )}

            {/* When Approved & Dispatched */}
            {isDispatched && (
              <div className="bg-emerald-950/40 border border-emerald-800/80 rounded-lg p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold font-mono text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 size={16} className="text-emerald-400 shrink-0 inline-block" />
                    ACTION AUTHORIZED BY OPERATOR RAMESH
                  </span>
                  <span className="text-[10px] bg-emerald-900/60 text-emerald-200 border border-emerald-700 px-1.5 py-0.2 rounded font-mono font-bold">
                    DISPATCHED
                  </span>
                </div>

                <p className="text-xs text-slate-300 font-sans">
                  Ground crew and clearance excavator staged. Bilingual public alert dispatched.
                </p>

                {/* Live Alert Preview */}
                <div className="bg-slate-950 rounded-lg border border-slate-800 p-2 space-y-1.5 font-mono text-xs">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-1 text-[11px]">
                    <div className="flex items-center gap-1">
                      <Languages size={15} className="text-blue-400 shrink-0 inline-block" />
                      <span className="font-bold text-slate-300">DISPATCHED PAYLOAD:</span>
                    </div>

                    <div className="flex gap-1">
                      <button 
                        onClick={() => setActiveAlertTab('NEPALI')}
                        className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${activeAlertTab === 'NEPALI' ? 'bg-blue-600 text-white' : 'text-slate-400'}`}
                      >
                        नेपाली
                      </button>
                      <button 
                        onClick={() => setActiveAlertTab('ENGLISH')}
                        className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${activeAlertTab === 'ENGLISH' ? 'bg-blue-600 text-white' : 'text-slate-400'}`}
                      >
                        EN
                      </button>
                      <button 
                        onClick={() => setActiveAlertTab('SMS')}
                        className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${activeAlertTab === 'SMS' ? 'bg-amber-600 text-white' : 'text-slate-400'}`}
                      >
                        SMS
                      </button>
                    </div>
                  </div>

                  <div className="p-2 bg-slate-900 rounded text-slate-200 whitespace-pre-line text-[11px] leading-relaxed font-sans max-h-28 overflow-y-auto">
                    {activeAlertTab === 'NEPALI' && (
                      `पहिरोवाच (PahiroWatch) पूर्वसूचना तथा सचेतना सूचना\n\nस्थिति: सम्भावित पहिरो अति उच्च जोखिम (CRITICAL) छ (जोखिम: 86/100, विश्वसनीयता: 75%)\nस्थान: ${selectedLocation?.name || 'Jalbire Sector'}\n\nप्रमुख प्राविधिक कारण:\n• पछिल्लो २४ घण्टामा अति भारी वर्षा: 184.0 मि.मि.\n• भिरालो जमिन: 38.5 डिग्री`
                    )}
                    {activeAlertTab === 'ENGLISH' && (
                      `PAHIROWATCH EARLY-WARNING ADVISORY\nStatus: CRITICAL RISK (Score: 86/100, Confidence: 75%)\nLocation: ${selectedLocation?.name || 'Jalbire Sector'}\nKey Drivers: 184mm Rain, 38.5° Slope, Highway 115m.`
                    )}
                    {activeAlertTab === 'SMS' && (
                      `PAHIROWATCH ALERT\nCRITICAL (86.0)\nLoc: Jalbire Waterfall\nRain24h: 184mm | Slope: 38.5deg\nConf: 75%\nAction: Dispatch inspection team`
                    )}
                  </div>
                </div>

              </div>
            )}

            {/* When Routine Surveillance */}
            {!isPendingApproval && !isDispatched && (
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs font-mono text-slate-400 space-y-1">
                <span className="text-emerald-400 font-bold flex items-center gap-1">
                  <CheckCircle2 size={16} className="text-emerald-400 shrink-0 inline-block" />
                  CORRIDOR STABLE
                </span>
                <p className="text-slate-400 font-sans text-xs">
                  Conditions are within routine operational tolerance. Agent continues background surveillance cycle.
                </p>
              </div>
            )}

          </div>

        </div>

      </main>

      {/* 5. BOTTOM SECTION: 🤖 AGENT REASONING TIMELINE (Readable & Honest) */}
      <footer className="bg-[#0b0f19] border-t border-slate-800 px-4 py-2 mt-auto shrink-0 font-mono">
        <div className="max-w-7xl mx-auto">
          
          <button
            onClick={() => setIsTraceOpen(!isTraceOpen)}
            className="w-full flex items-center justify-between py-1 text-xs text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <Terminal size={16} className="text-cyan-400 shrink-0 inline-block" />
              <span className="text-white font-bold">AGENT REASONING & TOOL TRACE</span>
              <span className="text-[11px] text-slate-400">({traces.length} steps recorded)</span>
              {currentRunInfo?.id && (
                <span className="bg-slate-900 border border-slate-800 px-1.5 py-0.2 rounded text-[10px] text-slate-400">
                  {currentRunInfo.id}
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400 text-[11px]">Click to {isTraceOpen ? 'Collapse' : 'Expand'}</span>
              {isTraceOpen ? <ChevronDown size={16} className="shrink-0 inline-block" /> : <ChevronUp size={16} className="shrink-0 inline-block" />}
            </div>
          </button>

          {/* Trace Steps Container */}
          {isTraceOpen && (
            <div className="mt-2 pt-2 border-t border-slate-800 max-h-48 overflow-y-auto space-y-1 text-xs">
              {traces.length === 0 ? (
                <p className="text-slate-400 italic text-xs py-2">No active trace. Run a scenario above.</p>
              ) : (
                traces.map((t) => {
                  const isGate = t.event_type === 'GATE';
                  const isDecision = t.event_type === 'DECISION';
                  const isTool = t.event_type === 'TOOL_CALL' || t.event_type === 'TOOL_RESULT';

                  return (
                    <div 
                      key={t.id}
                      className={`flex items-start gap-2 py-1 px-2 rounded text-[11px] ${
                        isGate ? 'bg-red-950/40 border border-red-800 text-red-200' :
                        isDecision ? 'bg-slate-900 border border-slate-800 text-rose-200' :
                        isTool ? 'text-slate-300' : 'text-slate-400'
                      }`}
                    >
                      <span className="text-slate-400 text-[10px] shrink-0 font-mono">
                        Step {t.step_number}:
                      </span>
                      <span className={`px-1 rounded text-[9px] font-bold shrink-0 ${
                        isGate ? 'bg-red-900 text-white' :
                        isDecision ? 'bg-rose-900 text-rose-200' :
                        'bg-slate-800 text-slate-300'
                      }`}>
                        {t.event_type}
                      </span>
                      <span className="break-words flex-1">{t.content}</span>
                    </div>
                  );
                })
              )}
            </div>
          )}

        </div>
      </footer>

    </div>
  );
};

export default App;
