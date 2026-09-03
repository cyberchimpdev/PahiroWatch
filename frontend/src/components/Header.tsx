import React from 'react';
import { 
  Shield, Activity, User, Coins, RefreshCw, 
  CloudRain, Compass, AlertOctagon, Play, Loader2 
} from 'lucide-react';
import type { CorridorStatus, AgentMetrics } from '../types';

interface HeaderProps {
  status: CorridorStatus | null;
  metrics: AgentMetrics | null;
  isResilienceMode: boolean;
  onRefresh: () => void;
  onRunMonsoon: () => void;
  onRunLowConfidence: () => void;
  onRunBadDay: () => void;
  onRunScheduled: () => void;
  loading: boolean;
  activeScenario: string | null;
}

export const Header: React.FC<HeaderProps> = ({ 
  status, 
  metrics, 
  isResilienceMode, 
  onRefresh,
  onRunMonsoon,
  onRunLowConfidence,
  onRunBadDay,
  onRunScheduled,
  loading,
  activeScenario
}) => {
  return (
    <header className="bg-[#0b0f19] border-b border-slate-800/90 px-4 py-2 select-none shrink-0 shadow-lg">
      <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-2.5">
        
        {/* Left: Brand, Pilot Corridor & Live Radar Pulse */}
        <div className="flex items-center space-x-3 shrink-0">
          <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-red-950/90 border border-red-700/80 text-red-400 font-bold shadow-md shadow-red-950/50">
            <Shield className="w-5 h-5 text-red-400" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </span>
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <span className="text-base font-black tracking-wider text-white uppercase flex items-center gap-1.5 font-mono">
                PAHIROWATCH
                <span className="text-[10px] tracking-normal font-sans bg-blue-950 text-blue-300 px-1.5 py-0.5 rounded border border-blue-800 font-bold">
                  पहिरोवाच • NH05
                </span>
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium italic truncate max-w-xs">
              Detect the slope. Protect the road. Alert before the disaster.
            </p>
          </div>
        </div>

        {/* Center: Mission Scenario Control Hub */}
        <div className="flex flex-wrap items-center gap-1.5 bg-slate-950/80 p-1 rounded-lg border border-slate-800/80 font-mono text-xs">
          <span className="text-[10px] font-bold text-slate-400 px-2 flex items-center gap-1">
            <Play className="w-3 h-3 text-cyan-400" />
            DEMO SCENARIOS:
          </span>

          {/* Scenario 1: Monsoon */}
          <button
            onClick={onRunMonsoon}
            disabled={loading}
            className={`px-2.5 py-1 rounded text-[11px] font-bold flex items-center gap-1.5 transition-all ${
              activeScenario === 'MONSOON'
                ? 'bg-red-600 text-white shadow-md shadow-red-950 ring-1 ring-red-300'
                : 'bg-red-950/70 hover:bg-red-900 text-red-200 border border-red-800/70'
            } disabled:opacity-50`}
            title="Monsoon cloudburst, steep slope, satellite retry, human checkpoint gate"
          >
            {loading && activeScenario === 'MONSOON' ? (
              <Loader2 className="w-3 h-3 animate-spin" />
            ) : (
              <CloudRain className="w-3 h-3 text-red-400" />
            )}
            <span>1. MONSOON CLOUDBURST</span>
          </button>

          {/* Scenario 2: Low Confidence / Suppression */}
          <button
            onClick={onRunLowConfidence}
            disabled={loading}
            className={`px-2.5 py-1 rounded text-[11px] font-semibold flex items-center gap-1.5 transition-all ${
              activeScenario === 'LOW_CONFIDENCE'
                ? 'bg-blue-600 text-white shadow-md ring-1 ring-blue-300'
                : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700'
            } disabled:opacity-50`}
            title="Gentle slope, low exposure: suppresses false alarms"
          >
            {loading && activeScenario === 'LOW_CONFIDENCE' ? (
              <Loader2 className="w-3 h-3 animate-spin" />
            ) : (
              <Compass className="w-3 h-3 text-blue-400" />
            )}
            <span>2. FALSE-ALARM FILTER</span>
          </button>

          {/* Scenario 3: Bad Day */}
          <button
            onClick={onRunBadDay}
            disabled={loading}
            className={`px-2.5 py-1 rounded text-[11px] font-semibold flex items-center gap-1.5 transition-all ${
              activeScenario === 'BAD_DAY'
                ? 'bg-amber-600 text-white shadow-md ring-1 ring-amber-300'
                : 'bg-amber-950/70 hover:bg-amber-900 text-amber-200 border border-amber-800/70'
            } disabled:opacity-50`}
            title="Stale weather, satellite blackout: resilience mode fallback"
          >
            {loading && activeScenario === 'BAD_DAY' ? (
              <Loader2 className="w-3 h-3 animate-spin" />
            ) : (
              <AlertOctagon className="w-3 h-3 text-amber-400" />
            )}
            <span>3. SENSOR BLACKOUT</span>
          </button>

          {/* Scheduled Cycle */}
          <button
            onClick={onRunScheduled}
            disabled={loading}
            className="px-2 py-1 rounded text-[10px] text-slate-400 hover:text-white bg-slate-900/60 hover:bg-slate-800 border border-slate-800 transition-colors disabled:opacity-50"
            title="Run standard periodic monitoring cycle"
          >
            {loading && activeScenario === 'SCHEDULED' ? 'RUNNING...' : 'RUN CYCLE'}
          </button>
        </div>

        {/* Right: Operator Context, Resilience Badge & Cost Telemetry */}
        <div className="flex items-center space-x-3 text-xs font-mono shrink-0">
          
          {isResilienceMode && (
            <div className="bg-amber-950/90 border border-amber-500/80 rounded px-2 py-1 flex items-center gap-1.5 text-amber-300 text-[11px] font-bold animate-pulse">
              <AlertOctagon className="w-3 h-3 text-amber-400" />
              <span>RESILIENCE ACTIVE</span>
            </div>
          )}

          <div className="hidden lg:flex items-center gap-1.5 bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-[11px]">
            <User className="w-3 h-3 text-blue-400" />
            <span className="text-slate-400">OPERATOR:</span>
            <span className="text-slate-200 font-semibold">{status?.operator?.split(',')[0] || "Ramesh"}</span>
          </div>

          <div className="bg-slate-950 border border-slate-800 rounded px-2.5 py-1 flex items-center gap-2 text-[11px]">
            <Coins className="w-3 h-3 text-emerald-400" />
            <span className="text-slate-400">COST:</span>
            <span className="text-emerald-400 font-bold">
              NPR {metrics?.total_cost_npr !== undefined ? metrics.total_cost_npr.toFixed(3) : "0.024"}
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className={`px-2 py-1 rounded text-[10px] font-bold border flex items-center gap-1 ${
              status?.agent_status === 'PAUSED_HUMAN_GATE' 
                ? 'bg-red-950 text-red-400 border-red-800 animate-pulse'
                : 'bg-emerald-950 text-emerald-400 border-emerald-800'
            }`}>
              <Activity className="w-2.5 h-2.5" />
              {status?.agent_status || "WATCHING"}
            </span>

            <button
              onClick={onRefresh}
              className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors border border-slate-800"
              title="Refresh Corridor Telemetry"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

        </div>

      </div>
    </header>
  );
};
