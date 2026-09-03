import React from 'react';

var SENSOR_NAMES = {
  'SNS-MUG-01': 'Jalbire (KM 24)',
  'SNS-MUG-04': 'Char Kilo (KM 36)',
  'SNS-MUG-09': 'Mugling Bazar (KM 42)',
};

export default function TelemetryChart({ telemetry, mlResult, onSimulate, loading, activeSensor }) {
  var isCritical = mlResult && mlResult.severity === 'CRITICAL';
  var isWarning = mlResult && mlResult.severity === 'WARNING';

  function getSeverityColor() {
    if (isCritical) return 'from-rose-500/10 to-rose-950/20 border-rose-500/30';
    if (isWarning) return 'from-amber-500/10 to-amber-950/20 border-amber-500/30';
    return 'from-emerald-500/10 to-emerald-950/20 border-emerald-500/30';
  }

  function getSeverityText() {
    if (isCritical) return 'text-rose-400';
    if (isWarning) return 'text-amber-400';
    return 'text-emerald-400';
  }

  function getBarWidth(value, max) {
    return Math.min((value / max) * 100, 100);
  }

  function getBarColor(value, threshold) {
    if (value >= threshold) return 'bg-rose-500';
    if (value >= threshold * 0.7) return 'bg-amber-500';
    return 'bg-emerald-500';
  }

  return (
    <div className="flex flex-col gap-3 h-full">
      <div className="flex items-center gap-2 mb-1">
        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
        <h2 className="text-[11px] font-bold text-emerald-400 uppercase tracking-widest font-mono">
          Telemetry - {SENSOR_NAMES[activeSensor] || activeSensor}
        </h2>
      </div>

      <div className="grid grid-cols-5 gap-2">
        <div className="glass rounded-lg p-3">
          <div className="text-[9px] text-slate-400 uppercase font-mono tracking-wider mb-1">Slope</div>
          <div className="text-2xl font-bold text-white font-mono">{telemetry.slope_deg}</div>
          <div className="mt-1.5 h-1 bg-dark-700 rounded-full overflow-hidden">
            <div
              className={'h-full rounded-full transition-all duration-500 ' + getBarColor(telemetry.slope_deg, 40)}
              style={{ width: getBarWidth(telemetry.slope_deg, 60) + '%' }}
            ></div>
          </div>
          <div className="text-[9px] text-slate-500 mt-1 font-mono">Limit: 40 deg</div>
        </div>
        <div className="glass rounded-lg p-3">
          <div className="text-[9px] text-slate-400 uppercase font-mono tracking-wider mb-1">72h Rain</div>
          <div className="text-2xl font-bold text-sky-400 font-mono">{telemetry.rain_72h}<span className="text-xs text-slate-400"> mm</span></div>
          <div className="mt-1.5 h-1 bg-dark-700 rounded-full overflow-hidden">
            <div
              className={'h-full rounded-full transition-all duration-500 ' + getBarColor(telemetry.rain_72h, 140)}
              style={{ width: getBarWidth(telemetry.rain_72h, 260) + '%' }}
            ></div>
          </div>
          <div className="text-[9px] text-slate-500 mt-1 font-mono">Limit: 140mm</div>
        </div>
        <div className="glass rounded-lg p-3">
          <div className="text-[9px] text-slate-400 uppercase font-mono tracking-wider mb-1">Moisture</div>
          <div className="text-2xl font-bold text-blue-400 font-mono">{telemetry.moisture}<span className="text-xs text-slate-400">%</span></div>
          <div className="mt-1.5 h-1 bg-dark-700 rounded-full overflow-hidden">
            <div
              className={'h-full rounded-full transition-all duration-500 ' + getBarColor(telemetry.moisture, 85)}
              style={{ width: getBarWidth(telemetry.moisture, 100) + '%' }}
            ></div>
          </div>
          <div className="text-[9px] text-slate-500 mt-1 font-mono">Limit: 85%</div>
        </div>
        <div className="glass rounded-lg p-3">
          <div className="text-[9px] text-slate-400 uppercase font-mono tracking-wider mb-1">NDVI</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">{telemetry.ndvi}</div>
          <div className="mt-1.5 h-1 bg-dark-700 rounded-full overflow-hidden">
            <div
              className={'h-full rounded-full transition-all duration-500 ' + (telemetry.ndvi <= 0.25 ? 'bg-rose-500' : 'bg-emerald-500')}
              style={{ width: getBarWidth(telemetry.ndvi, 1) + '%' }}
            ></div>
          </div>
          <div className="text-[9px] text-slate-500 mt-1 font-mono">Barren: 0.25-</div>
        </div>
        <div className="glass rounded-lg p-3">
          <div className="text-[9px] text-slate-400 uppercase font-mono tracking-wider mb-1">Vibration</div>
          <div className="text-2xl font-bold text-purple-400 font-mono">{telemetry.acoustic_vib}<span className="text-xs text-slate-400"> Hz</span></div>
          <div className="mt-1.5 h-1 bg-dark-700 rounded-full overflow-hidden">
            <div
              className={'h-full rounded-full transition-all duration-500 ' + getBarColor(telemetry.acoustic_vib, 40)}
              style={{ width: getBarWidth(telemetry.acoustic_vib, 80) + '%' }}
            ></div>
          </div>
          <div className="text-[9px] text-slate-500 mt-1 font-mono">Limit: 40 Hz</div>
        </div>
      </div>

      <div className={
        'p-4 rounded-xl border bg-gradient-to-r ' + getSeverityColor() + ' flex flex-col md:flex-row justify-between items-start md:items-center gap-3 transition-all duration-300'
      }>
        <div className="flex-1 min-w-0">
          <div className="text-[9px] text-slate-400 uppercase font-mono tracking-wider mb-1">
            Random Forest Landslide Classifier (mhscience methodology)
          </div>
          <div className="text-xs text-slate-200 font-mono">
            <span className="text-slate-400">Vulnerabilities:</span>{' '}
            {mlResult && mlResult.key_contributors ? mlResult.key_contributors.join(' | ') : 'Awaiting telemetry input'}
          </div>
        </div>
        <div className="text-right shrink-0">
          <div className="text-[9px] text-slate-400 uppercase font-mono tracking-wider">Probability</div>
          <div className={'text-3xl font-bold font-mono ' + getSeverityText()}>
            {mlResult && mlResult.probability ? (mlResult.probability * 100).toFixed(1) + '%' : '--'}
          </div>
          <div className={'text-[10px] font-bold font-mono uppercase ' + getSeverityText()}>
            {mlResult && mlResult.severity ? mlResult.severity : 'STABLE'}
          </div>
        </div>
      </div>

      <div className="glass rounded-xl p-5 flex-1 flex flex-col justify-center items-center text-center">
        <p className="text-xs text-slate-400 max-w-md mb-4 leading-relaxed">
          BhumiSense monitors highway sectors automatically. Simulating a cloudburst trips the local Random Forest model, which autonomously launches the agent planning loop via Azure OpenAI gpt-5.5.
        </p>
        <div className="flex flex-wrap gap-3 justify-center">
          <button
            onClick={function() { if (!loading) onSimulate(false); }}
            disabled={loading}
            className="px-5 py-2.5 bg-dark-800 hover:bg-dark-700 text-xs font-medium rounded-lg text-slate-200 border border-dark-600 transition-all duration-200 font-mono disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Normal Monsoon
          </button>
          <button
            onClick={function() { if (!loading) onSimulate(true); }}
            disabled={loading}
            className="px-5 py-2.5 bg-rose-950 hover:bg-rose-900 text-xs font-bold rounded-lg text-rose-300 border border-rose-700 transition-all duration-200 font-mono shadow-lg shadow-rose-950/50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Simulate Cloudburst (Critical)'}
          </button>
        </div>
      </div>
    </div>
  );
}