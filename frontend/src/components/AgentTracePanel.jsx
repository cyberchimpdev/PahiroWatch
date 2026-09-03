import React, { useEffect, useRef } from 'react';

export default function AgentTracePanel({ runData, onResolveGate, loading }) {
  var traces = (runData && runData.traces) ? runData.traces : [];
  var traceEndRef = useRef(null);

  useEffect(function() {
    if (traceEndRef.current) {
      traceEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [traces.length]);

  function formatTime(ts) {
    if (!ts) return '--:--';
    return new Date(ts).toLocaleTimeString();
  }

  function getTraceStyle(stepType) {
    if (stepType === 'PLAN') return 'text-sky-400 bg-sky-950/30 border-sky-800/30';
    if (stepType === 'TOOL_CALL') return 'text-amber-400 bg-amber-950/30 border-amber-800/30';
    if (stepType === 'TOOL_RESULT') return 'text-emerald-400 bg-emerald-950/30 border-emerald-800/30';
    if (stepType === 'GATE') return 'text-rose-400 bg-rose-950/30 border-rose-800/30';
    if (stepType === 'ACTION') return 'text-purple-400 bg-purple-950/30 border-purple-800/30';
    if (stepType === 'ERROR') return 'text-red-400 bg-red-950/30 border-red-800/30';
    return 'text-slate-400 bg-slate-950/30 border-slate-800/30';
  }

  function getTraceIcon(stepType) {
    if (stepType === 'PLAN') return 'PLAN';
    if (stepType === 'TOOL_CALL') return 'CALL';
    if (stepType === 'TOOL_RESULT') return 'RES';
    if (stepType === 'GATE') return 'GATE';
    if (stepType === 'ACTION') return 'EXEC';
    if (stepType === 'ERROR') return 'FAIL';
    return 'LOG';
  }

  function getStatusStyle() {
    if (!runData || !runData.status) return 'bg-dark-800 text-slate-400 border-dark-700';
    if (runData.status === 'RUNNING') return 'bg-amber-950 text-amber-400 border-amber-800';
    if (runData.status === 'AWAITING_APPROVAL') return 'bg-rose-950 text-rose-400 border-rose-800';
    if (runData.status === 'EXECUTED') return 'bg-emerald-950 text-emerald-400 border-emerald-800';
    if (runData.status === 'REJECTED') return 'bg-dark-800 text-slate-400 border-dark-700';
    if (runData.status === 'FAILED') return 'bg-red-950 text-red-400 border-red-800';
    return 'bg-dark-800 text-slate-400 border-dark-700';
  }

  function getStatusLabel() {
    if (!runData || !runData.status) return 'IDLE';
    if (runData.status === 'RUNNING') return 'RUNNING';
    if (runData.status === 'AWAITING_APPROVAL') return 'AWAITING APPROVAL';
    if (runData.status === 'EXECUTED') return 'EXECUTED';
    if (runData.status === 'REJECTED') return 'REJECTED';
    if (runData.status === 'FAILED') return 'FAILED';
    return runData.status;
  }

  return (
    <div className="glass rounded-xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-dark-700/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={'w-1.5 h-1.5 rounded-full ' + (loading ? 'bg-amber-500 animate-pulse' : 'bg-indigo-500')}></div>
          <h2 className="text-[11px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Agent Trace</h2>
        </div>
        <span className={'text-[9px] px-2 py-0.5 rounded border font-mono font-bold ' + getStatusStyle()}>
          {getStatusLabel()}
        </span>
      </div>

      {runData && runData.status === 'AWAITING_APPROVAL' && runData.proposed_action && (
        <div className="p-4 bg-gradient-to-r from-rose-950/40 to-rose-900/20 border-b-2 border-rose-500/50 flex flex-col gap-3 animate-slide-in animate-pulse-glow">
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider font-mono">
              Human Checkpoint Required
            </span>
            <span className="text-[8px] bg-rose-900 text-rose-200 px-2 py-0.5 rounded font-mono font-bold border border-rose-700">
              GATED
            </span>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            The agent requests immediate broadcast to <strong className="text-white">{runData.proposed_action.target_ward}</strong> and closure of police barriers.
          </p>
          <div className="bg-dark-950/80 p-3 rounded-lg border border-rose-900/30">
            <p className="text-[10px] text-amber-200 font-mono leading-relaxed">
              {runData.proposed_action.sms_payload_nepali}
            </p>
          </div>
          <div className="text-[10px] text-slate-400 font-mono">
            Detour: <strong className="text-white">{runData.proposed_action.recommended_detour}</strong>
          </div>
          <div className="flex gap-2 mt-1">
            <button
              onClick={function() { if (!loading) onResolveGate(true); }}
              disabled={loading}
              className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2.5 text-[11px] rounded-lg transition-all duration-200 font-mono disabled:opacity-50"
            >
              APPROVE &amp; BROADCAST
            </button>
            <button
              onClick={function() { if (!loading) onResolveGate(false); }}
              disabled={loading}
              className="flex-1 bg-dark-800 hover:bg-dark-700 text-slate-300 py-2.5 text-[11px] rounded-lg transition-all duration-200 font-mono border border-dark-600 disabled:opacity-50"
            >
              REJECT
            </button>
          </div>
        </div>
      )}

      <div className="flex-1 p-2 overflow-y-auto space-y-1.5 font-mono text-[11px]">
        {traces.length === 0 ? (
          <div className="text-slate-600 italic text-center py-12 flex flex-col items-center gap-2">
            <div className="w-8 h-8 rounded-full border-2 border-dark-700 flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-dark-600"></div>
            </div>
            <span className="text-[10px]">Awaiting trigger</span>
          </div>
        ) : (
          traces.map(function(t, idx) {
            return (
              <div key={idx} className="trace-entry leading-relaxed py-1.5 px-2 rounded border border-transparent hover:border-dark-700/50 transition-colors">
                <div className="flex items-start gap-2">
                  <span className="text-[9px] text-slate-600 shrink-0 mt-0.5 w-16">{formatTime(t.timestamp)}</span>
                  <span className={
                    'text-[8px] px-1.5 py-0.5 rounded border shrink-0 mt-0.5 font-bold ' + getTraceStyle(t.step_type)
                  }>
                    {getTraceIcon(t.step_type)}
                  </span>
                  <span className="text-slate-300 break-words flex-1">
                    {t.thought || t.tool_result || (t.tool_name ? t.tool_name + ': ' + JSON.stringify(t.tool_args) : '')}
                  </span>
                </div>
              </div>
            );
          })
        )}
        <div ref={traceEndRef}></div>
      </div>

      <div className="p-3 border-t border-dark-700/50 flex justify-between text-[10px] text-slate-500 font-mono bg-dark-900/50">
        <span>Tokens: <span className="text-slate-300">{runData && runData.total_tokens ? runData.total_tokens : 0}</span></span>
        <span>Conf: <span className="text-slate-300">{runData && runData.confidence ? (runData.confidence * 100).toFixed(0) + '%' : '--'}</span></span>
        <span>Cost: <span className="text-slate-300">NPR {runData && runData.cost_npr ? runData.cost_npr : '0.00'}</span></span>
      </div>
    </div>
  );
}