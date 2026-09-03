import React, { useState, useEffect } from 'react';
import SensorGrid from './components/SensorGrid';
import TelemetryChart from './components/TelemetryChart';
import AgentTracePanel from './components/AgentTracePanel';

var API_BASE = 'http://127.0.0.1:8000/api';

var SENSOR_DEFAULTS = {
  'SNS-MUG-01': { slope_deg: 28.0, rain_72h: 35.0, moisture: 65.0, ndvi: 0.42, acoustic_vib: 14.0 },
  'SNS-MUG-04': { slope_deg: 48.0, rain_72h: 185.0, moisture: 93.0, ndvi: 0.18, acoustic_vib: 62.0 },
  'SNS-MUG-09': { slope_deg: 22.0, rain_72h: 28.0, moisture: 58.0, ndvi: 0.55, acoustic_vib: 10.0 },
};

export default function App() {
  var _s = useState([]);
  var sensors = _s[0], setSensors = _s[1];
  var _a = useState('SNS-MUG-04');
  var activeSensor = _a[0], setActiveSensor = _a[1];
  var _t = useState({ slope_deg: 48.0, rain_72h: 185.0, moisture: 93.0, ndvi: 0.18, acoustic_vib: 62.0 });
  var telemetry = _t[0], setTelemetry = _t[1];
  var _m = useState(null);
  var mlResult = _m[0], setMlResult = _m[1];
  var _r = useState(null);
  var activeRunId = _r[0], setActiveRunId = _r[1];
  var _d = useState(null);
  var runData = _d[0], setRunData = _d[1];
  var _l = useState(false);
  var loading = _l[0], setLoading = _l[1];
  var _c = useState(0);
  var sensorCount = _c[0], setSensorCount = _c[1];
  var _h = useState(false);
  var history = _h[0], setHistory = _h[1];

  useEffect(function() {
    fetch(API_BASE + '/sensors/')
      .then(function(res) { return res.json(); })
      .then(function(data) {
        setSensors(data);
        setSensorCount(data.length);
      })
      .catch(function() {
        setSensors([
          { id: 'SNS-MUG-01', location: 'Jalbire (KM 24)', slope: 28.0, ndvi: 0.42, status: 'normal' },
          { id: 'SNS-MUG-04', location: 'Char Kilo (KM 36)', slope: 48.0, ndvi: 0.18, status: 'active' },
          { id: 'SNS-MUG-09', location: 'Mugling Bazar (KM 42)', slope: 22.0, ndvi: 0.55, status: 'normal' },
        ]);
        setSensorCount(3);
      });
  }, []);

  useEffect(function() {
    if (SENSOR_DEFAULTS[activeSensor]) {
      setTelemetry(SENSOR_DEFAULTS[activeSensor]);
    }
  }, [activeSensor]);

  useEffect(function() {
    if (!activeRunId) return;
    var pollCount = 0;
    var pollInterval = setInterval(function() {
      pollCount++;
      if (pollCount > 60) {
        clearInterval(pollInterval);
        setLoading(false);
        return;
      }
      fetch(API_BASE + '/runs/' + activeRunId + '/trace/')
        .then(function(res) { return res.json(); })
        .then(function(data) {
          setRunData(data);
          if (data.status === 'EXECUTED' || data.status === 'REJECTED' || data.status === 'FAILED') {
            clearInterval(pollInterval);
            setLoading(false);
          }
        })
        .catch(function() {});
    }, 1500);
    return function() { clearInterval(pollInterval); };
  }, [activeRunId]);

  function handleSimulate(isExtreme) {
    var base = SENSOR_DEFAULTS[activeSensor] || SENSOR_DEFAULTS['SNS-MUG-04'];
    var payload;
    if (isExtreme) {
      payload = {
        sensor_id: activeSensor,
        slope_deg: Math.max(base.slope_deg, 42.0),
        rain_72h: 185.0,
        moisture: 93.0,
        ndvi: Math.min(base.ndvi, 0.20),
        acoustic_vib: 62.0
      };
    } else {
      payload = {
        sensor_id: activeSensor,
        slope_deg: base.slope_deg,
        rain_72h: 35.0,
        moisture: 65.0,
        ndvi: base.ndvi,
        acoustic_vib: 14.0
      };
    }

    setTelemetry(payload);
    setLoading(true);
    setRunData(null);

    fetch(API_BASE + '/telemetry/ingest/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        setMlResult(data.ml_evaluation);
        if (data.agent_triggered && data.run_id) {
          setActiveRunId(data.run_id);
        } else {
          setLoading(false);
        }
      })
      .catch(function() { setLoading(false); });
  }

  function handleResolveGate(approved) {
    if (!activeRunId) return;
    setLoading(true);
    fetch(API_BASE + '/runs/' + activeRunId + '/gate/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved: approved })
    })
      .then(function() {
        return fetch(API_BASE + '/runs/' + activeRunId + '/trace/');
      })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        setRunData(data);
        setLoading(false);
      })
      .catch(function() { setLoading(false); });
  }

  function handleReset() {
    setMlResult(null);
    setRunData(null);
    setActiveRunId(null);
    setLoading(false);
    setTelemetry(SENSOR_DEFAULTS[activeSensor] || SENSOR_DEFAULTS['SNS-MUG-04']);
  }

  return (
    <div className="h-screen flex flex-col bg-dark-950 text-slate-100 overflow-hidden">
      <header className="flex items-center justify-between px-6 py-3 glass border-b border-dark-700/50 shrink-0 z-10">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
            <div className="absolute inset-0 w-3 h-3 rounded-full bg-emerald-500 animate-ping opacity-50"></div>
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">
              BhumiSense <span className="text-emerald-400 font-extrabold">AI</span>
            </h1>
            <p className="text-[10px] text-slate-400 font-mono uppercase tracking-widest">
              Corridor Disaster Sentinel
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right hidden md:block">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">Narayanghat-Mugling Highway</p>
            <p className="text-[10px] text-slate-400 font-mono">Pulchowk Hackathon 2026</p>
          </div>
          <div className="h-8 w-px bg-dark-700"></div>
          <button
            onClick={handleReset}
            className="text-[10px] text-slate-400 hover:text-white transition-colors font-mono uppercase tracking-wider"
          >
            Reset
          </button>
        </div>
      </header>

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-3 p-3 min-h-0 overflow-hidden">
        <div className="lg:col-span-3 h-full min-h-0">
          <SensorGrid
            sensors={sensors}
            activeSensor={activeSensor}
            onSelectSensor={setActiveSensor}
            sensorCount={sensorCount}
          />
        </div>
        <div className="lg:col-span-5 h-full min-h-0 overflow-y-auto">
          <TelemetryChart
            mlResult={mlResult}
            onSimulate={handleSimulate}
            telemetry={telemetry}
            loading={loading}
            activeSensor={activeSensor}
          />
        </div>
        <div className="lg:col-span-4 h-full min-h-0">
          <AgentTracePanel
            onResolveGate={handleResolveGate}
            runData={runData}
            loading={loading}
          />
        </div>
      </main>
    </div>
  );
}