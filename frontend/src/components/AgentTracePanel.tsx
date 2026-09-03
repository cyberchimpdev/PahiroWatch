import React, { useRef, useEffect, useState } from 'react';
import type { TraceEvent } from '../types';
import { 
  Terminal, Cpu, Clock, DollarSign, Wrench, 
  ShieldAlert, CheckCircle, RefreshCw, Maximize2, Minimize2, Filter 
} from 'lucide-react';

interface AgentTracePanelProps {
  traces: TraceEvent[];
  runInfo?: any;
  loading: boolean;
  onRefresh: () => void;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

export const AgentTracePanel: React.FC<AgentTracePanelProps> = ({
  traces,
  runInfo,
  loading,
  onRefresh,
  isExpanded = false,
  onToggleExpand
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [filter, setFilter] = useState<'ALL' | 'TOOLS' | 'DECISIONS' | 'GATES'>('ALL');

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [traces]);

  const filteredTraces = traces.filter(t => {
    if (filter === 'TOOLS') return t.event_type === 'TOOL_CALL' || t.event_type === 'TOOL_RESULT';
    if (filter === 'DECISIONS') return t.event_type === 'DECISION' || t.event_type === 'CONFIDENCE';
    if (filter === 'GATES') return t.event_type === 'GATE' || t.event_type === 'HUMAN' || t.event_type === 'ACTION';
    return true;
  });

  const getEventBadge = (type: string) => {
    switch (type) {
      case 'TRIGGER':
        return <span className="bg-purple-950 text-purple-300 border border-purple-800 px-1.5 py-0.2 rounded text-[9px] font-bold">TRIGGER</span>;
      case 'GOAL':
        return <span className="bg-blue-950 text-blue-300 border border-blue-800 px-1.5 py-0.2 rounded text-[9px] font-bold">GOAL</span>;
      case 'PLAN':
        return <span className="bg-cyan-950 text-cyan-300 border border-cyan-800 px-1.5 py-0.2 rounded text-[9px] font-bold">PLAN</span>;
      case 'TOOL_CALL':
        return <span className="bg-amber-950 text-amber-300 border border-amber-800 px-1.5 py-0.2 rounded text-[9px] font-bold flex items-center gap-0.5"><Wrench className="w-2.5 h-2.5" /> TOOL</span>;
      case 'TOOL_RESULT':
        return <span className="bg-slate-800 text-slate-300 border border-slate-700 px-1.5 py-0.2 rounded text-[9px] font-bold">RESULT</span>;
      case 'MEMORY':
        return <span className="bg-indigo-950 text-indigo-300 border border-indigo-800 px-1.5 py-0.2 rounded text-[9px] font-bold">MEMORY</span>;
      case 'DECISION':
        return <span className="bg-rose-950 text-rose-300 border border-rose-800 px-1.5 py-0.2 rounded text-[9px] font-bold">DECISION</span>;
      case 'CONFIDENCE':
        return <span className="bg-teal-950 text-teal-300 border border-teal-800 px-1.5 py-0.2 rounded text-[9px] font-bold">CONFIDENCE</span>;
      case 'GATE':
        return <span className="bg-red-950 text-red-300 border border-red-700 px-1.5 py-0.2 rounded text-[9px] font-bold flex items-center gap-0.5 animate-pulse"><ShieldAlert className="w-2.5 h-2.5" /> GATE</span>;
      case 'HUMAN':
        return <span className="bg-emerald-950 text-emerald-300 border border-emerald-700 px-1.5 py-0.2 rounded text-[9px] font-bold flex items-center gap-0.5"><CheckCircle className="w-2.5 h-2.5" /> HUMAN</span>;
      case 'ACTION':
        return <span className="bg-green-950 text-green-300 border border-green-700 px-1.5 py-0.2 rounded text-[9px] font-bold">ACTION</span>;
      default:
        return <span className="bg-slate-800 text-slate-400 px-1.5 py-0.2 rounded text-[9px]">{type}</span>;
    }
  };

  const toolCallsCount = traces.filter(t => t.event_type === 'TOOL_CALL').length;

  return (
    <div className="flex flex-col h-full bg-[#070a12] border border-slate-800/90 rounded-xl overflow-hidden font-mono shadow-2xl">
      
      {/* Trace Top Bar */}
      <div className="bg-[#0e1626] px-3 py-2 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs">
        
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span className="text-white font-bold tracking-wider text-xs">LIVE AGENT TRACE</span>
          {runInfo?.id && (
            <span className="text-slate-400 text-[10px] bg-slate-900 px-1.5 py-0.5 rounded border border-slate-700">
              {runInfo.id}
            </span>
          )}
          {runInfo?.is_resilience_mode && (
            <span className="text-[10px] bg-amber-950 text-amber-300 border border-amber-700 px-1.5 py-0.2 rounded font-bold">
              RESILIENCE
            </span>
          )}
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-1 text-[10px]">
          <Filter className="w-3 h-3 text-slate-400 mr-0.5" />
          {(['ALL', 'TOOLS', 'DECISIONS', 'GATES'] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setFilter(mode)}
              className={`px-1.5 py-0.5 rounded transition-colors ${
                filter === mode
                  ? 'bg-blue-600 text-white font-bold'
                  : 'bg-slate-900 text-slate-400 hover:text-white'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>

        {/* Telemetry Metrics & Actions */}
        <div className="flex items-center gap-3 text-[11px] text-slate-400">
          <div className="hidden sm:flex items-center gap-1">
            <Cpu className="w-3 h-3 text-blue-400" />
            <span>Tools: <strong className="text-white">{toolCallsCount}</strong></span>
          </div>
          <div className="hidden sm:flex items-center gap-1">
            <Clock className="w-3 h-3 text-amber-400" />
            <span>{runInfo?.total_latency_ms || 24}ms</span>
          </div>
          <div className="flex items-center gap-1">
            <DollarSign className="w-3 h-3 text-emerald-400" />
            <span className="text-emerald-400 font-bold">NPR {runInfo?.estimated_cost_npr ? runInfo.estimated_cost_npr.toFixed(4) : "0.0000"}</span>
          </div>

          <div className="flex items-center gap-1 border-l border-slate-700 pl-2">
            <button 
              onClick={onRefresh} 
              className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors"
              title="Refresh Trace Stream"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>

            {onToggleExpand && (
              <button
                onClick={onToggleExpand}
                className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors"
                title={isExpanded ? "Collapse Panel" : "Expand Panel"}
              >
                {isExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>
        </div>

      </div>

      {/* Trace Log Body */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1.5 text-xs bg-[#070a12] leading-relaxed">
        {filteredTraces.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-400 italic text-center p-4">
            <div>
              <Terminal className="w-6 h-6 mx-auto mb-1 text-slate-500" />
              <p className="text-xs">No active trace session.</p>
              <p className="text-[10px] text-slate-400 mt-0.5">Click "1. MONSOON CLOUDBURST" to observe live agent tool execution.</p>
            </div>
          </div>
        ) : (
          filteredTraces.map((trace) => {
            const timeStr = trace.timestamp 
              ? trace.timestamp.split('T')[1]?.slice(0, 8) || trace.timestamp.slice(11, 19) 
              : '--:--:--';

            const isGate = trace.event_type === 'GATE';
            const isDecision = trace.event_type === 'DECISION';
            const isTool = trace.event_type === 'TOOL_CALL' || trace.event_type === 'TOOL_RESULT';

            return (
              <div 
                key={trace.id} 
                className={`flex items-start gap-2.5 p-1.5 rounded transition-colors text-[11px] ${
                  isGate 
                    ? 'bg-red-950/40 border border-red-800/80 shadow-sm' 
                    : isDecision
                    ? 'bg-rose-950/20 border border-rose-900/40'
                    : isTool
                    ? 'hover:bg-slate-900/60'
                    : 'hover:bg-slate-900/30'
                }`}
              >
                <span className="text-slate-400 select-none text-[10px] shrink-0 font-mono">
                  [{timeStr}]
                </span>
                
                <div className="shrink-0 mt-0.5">
                  {getEventBadge(trace.event_type)}
                </div>

                <div className="flex-1 min-w-0">
                  <p className={`text-slate-200 break-words ${
                    isDecision ? 'font-bold text-rose-200' : isGate ? 'font-bold text-red-200' : ''
                  }`}>
                    {trace.content}
                  </p>

                  {/* Metadata Disclaimers */}
                  {trace.metadata && trace.metadata.disclaimer && (
                    <div className="mt-1 text-[9px] text-amber-300 font-sans italic bg-amber-950/40 px-1.5 py-0.5 rounded border border-amber-900/50 inline-block">
                      ⚠ {trace.metadata.disclaimer}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>

    </div>
  );
};
