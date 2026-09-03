import React from 'react';
import { CloudRain, Compass, AlertOctagon, Play, Loader2 } from 'lucide-react';

interface ScenarioBarProps {
  onRunMonsoon: () => void;
  onRunLowConfidence: () => void;
  onRunBadDay: () => void;
  onRunScheduled: () => void;
  loading: boolean;
  activeScenario: string | null;
}

export const ScenarioBar: React.FC<ScenarioBarProps> = ({
  onRunMonsoon,
  onRunLowConfidence,
  onRunBadDay,
  onRunScheduled,
  loading,
  activeScenario,
}) => {
  return (
    <div className="bg-slate-900 border-b border-slate-800 px-6 py-2.5 flex flex-wrap items-center justify-between gap-3 text-xs font-mono select-none">
      
      <div className="flex items-center gap-2">
        <span className="text-slate-400 font-bold uppercase flex items-center gap-1.5">
          <Play className="w-3.5 h-3.5 text-blue-400" />
          DEMO SCENARIO CONTROL:
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2.5">
        
        {/* P0 Primary Demo Scenario: Monsoon Cloudburst */}
        <button
          onClick={onRunMonsoon}
          disabled={loading}
          className={`px-3 py-1.5 rounded font-bold text-xs flex items-center gap-1.5 transition-all shadow-md ${
            activeScenario === 'MONSOON'
              ? 'bg-red-600 text-white shadow-red-950/80 ring-2 ring-red-400'
              : 'bg-red-950/80 hover:bg-red-900 text-red-200 border border-red-800/80 hover:border-red-600'
          } disabled:opacity-50`}
        >
          {loading && activeScenario === 'MONSOON' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <CloudRain className="w-3.5 h-3.5 text-red-400" />
          )}
          <span>1. RUN MONSOON SCENARIO</span>
        </button>

        {/* Demo Scenario 2: Low Confidence / Suppression */}
        <button
          onClick={onRunLowConfidence}
          disabled={loading}
          className={`px-3 py-1.5 rounded font-semibold text-xs flex items-center gap-1.5 transition-all ${
            activeScenario === 'LOW_CONFIDENCE'
              ? 'bg-blue-600 text-white ring-2 ring-blue-400'
              : 'bg-slate-800/90 hover:bg-slate-700 text-slate-300 border border-slate-700'
          } disabled:opacity-50`}
        >
          {loading && activeScenario === 'LOW_CONFIDENCE' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Compass className="w-3.5 h-3.5 text-blue-400" />
          )}
          <span>2. LOW CONFIDENCE (SUPPRESS FALSE ALARM)</span>
        </button>

        {/* Demo Scenario 3: Bad Day / Resilience */}
        <button
          onClick={onRunBadDay}
          disabled={loading}
          className={`px-3 py-1.5 rounded font-semibold text-xs flex items-center gap-1.5 transition-all ${
            activeScenario === 'BAD_DAY'
              ? 'bg-amber-600 text-white ring-2 ring-amber-400'
              : 'bg-amber-950/70 hover:bg-amber-900/80 text-amber-200 border border-amber-800/80'
          } disabled:opacity-50`}
        >
          {loading && activeScenario === 'BAD_DAY' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <AlertOctagon className="w-3.5 h-3.5 text-amber-400" />
          )}
          <span>3. BAD DAY (RESILIENCE MODE)</span>
        </button>

        {/* Routine Trigger Button */}
        <button
          onClick={onRunScheduled}
          disabled={loading}
          className="px-3 py-1.5 rounded font-mono text-[11px] text-slate-400 hover:text-slate-200 bg-slate-950 hover:bg-slate-800 border border-slate-800 transition-colors disabled:opacity-50"
        >
          {loading && activeScenario === 'SCHEDULED' ? 'EXECUTING...' : 'RUN MONITORING CYCLE NOW'}
        </button>

      </div>

    </div>
  );
};
