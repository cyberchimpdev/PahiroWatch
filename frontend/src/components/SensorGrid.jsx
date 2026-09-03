import React from 'react';

export default function SensorGrid({ sensors, activeSensor, onSelectSensor, sensorCount }) {
  if (!sensors || sensors.length === 0) {
    return (
      <div className="glass rounded-xl flex flex-col h-full overflow-hidden">
        <div className="p-4 border-b border-dark-700/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
            <h2 className="text-[11px] font-bold text-slate-300 uppercase tracking-widest font-mono">Sensor Grid</h2>
          </div>
          <span className="text-[9px] bg-emerald-950 text-emerald-400 border border-emerald-800/50 px-2 py-0.5 rounded font-mono">
            LOADING
          </span>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-2">
            <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-xs text-slate-500 font-mono">Connecting to grid...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass rounded-xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-dark-700/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
          <h2 className="text-[11px] font-bold text-slate-300 uppercase tracking-widest font-mono">Sensor Grid</h2>
        </div>
        <span className="text-[9px] bg-emerald-950 text-emerald-400 border border-emerald-800/50 px-2 py-0.5 rounded font-mono">
          {sensorCount} ONLINE
        </span>
      </div>
      <div className="p-2 space-y-2 flex-1 overflow-y-auto">
        {sensors.map(function(s) {
          var isSelected = s.id === activeSensor;
          var isHighRisk = s.status === 'active';
          return (
            <div
              key={s.id}
              onClick={function() { onSelectSensor(s.id); }}
              className={
                'p-3 rounded-lg border cursor-pointer transition-all duration-200 ' +
                (isSelected
                  ? 'bg-dark-800/80 border-emerald-500/30 glow-green'
                  : 'bg-dark-900/40 border-dark-700/30 hover:bg-dark-800/50 hover:border-dark-600/50')
              }
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-xs text-white font-mono">{s.location}</span>
                <span className={
                  'w-2 h-2 rounded-full ' +
                  (isHighRisk ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500')
                }></span>
              </div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-slate-500 font-mono">{s.id}</span>
                <span className="text-[10px] text-slate-500 font-mono">
                  {s.slope !== undefined ? s.slope + '\u00B0' : '--'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-slate-500 font-mono">
                  NDVI {s.ndvi !== undefined ? s.ndvi.toFixed(2) : '--'}
                </span>
                <span className={
                  'text-[9px] px-1.5 py-0.5 rounded font-mono font-bold uppercase ' +
                  (isHighRisk
                    ? 'bg-rose-950 text-rose-400 border border-rose-800/50'
                    : 'bg-dark-800 text-slate-400 border border-dark-700/50')
                }>
                  {isHighRisk ? 'ACTIVE' : 'MONITORING'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
      <div className="p-3 border-t border-dark-700/50">
        <div className="flex items-center gap-2 text-[9px] text-slate-500 font-mono">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
          <span>Grid connected via Narayanghat-Mugling corridor</span>
        </div>
      </div>
    </div>
  );
}