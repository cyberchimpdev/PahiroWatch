import React from 'react';
import { 
  MapPin, AlertOctagon, 
  Layers, ShieldAlert, ChevronRight, Activity, Mountain 
} from 'lucide-react';
import type { Location, Incident } from '../types';

interface LeftSidebarProps {
  locations: Location[];
  selectedLocation: Location | null;
  onSelectLocation: (loc: Location) => void;
  incidents: Incident[];
  activeTab: 'OVERVIEW' | 'INCIDENTS' | 'TRACE';
  onSelectTab: (tab: 'OVERVIEW' | 'INCIDENTS' | 'TRACE') => void;
  onSelectIncident: (inc: Incident) => void;
}

export const LeftSidebar: React.FC<LeftSidebarProps> = ({
  locations,
  selectedLocation,
  onSelectLocation,
  incidents,
  activeTab,
  onSelectTab,
  onSelectIncident
}) => {
  return (
    <aside className="w-full lg:w-72 bg-[#0b0f19] border-r border-slate-800/90 flex flex-col justify-between font-sans text-xs shrink-0 select-none shadow-xl">
      
      {/* Top Section */}
      <div className="p-3 space-y-3.5 overflow-y-auto">
        
        {/* Navigation Tabs */}
        <div className="grid grid-cols-2 gap-1.5 font-mono text-[11px]">
          <button
            onClick={() => onSelectTab('OVERVIEW')}
            className={`flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg font-bold transition-all ${
              activeTab === 'OVERVIEW'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-white border border-slate-800'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>CORRIDOR</span>
          </button>

          <button
            onClick={() => onSelectTab('INCIDENTS')}
            className={`flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg font-bold transition-all ${
              activeTab === 'INCIDENTS'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-900/80 text-slate-400 hover:bg-slate-800 hover:text-white border border-slate-800'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>INCIDENTS</span>
            {incidents.length > 0 && (
              <span className="text-[10px] bg-red-600 text-white px-1.5 py-0.2 rounded-full font-bold animate-pulse">
                {incidents.length}
              </span>
            )}
          </button>
        </div>

        {/* Highway Sectors List */}
        <div className="space-y-1.5 pt-1">
          <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 font-bold uppercase tracking-wider px-1">
            <span>PILOT HIGHWAY SECTORS</span>
            <span className="text-slate-400">SLOPE</span>
          </div>

          <div className="space-y-1">
            {locations.map((loc) => {
              const isSelected = selectedLocation?.id === loc.id;
              const isSteep = loc.baseline_slope_deg >= 32.0;
              const isModerate = loc.baseline_slope_deg >= 22.0 && loc.baseline_slope_deg < 32.0;

              return (
                <button
                  key={loc.id}
                  onClick={() => onSelectLocation(loc)}
                  className={`w-full text-left p-2 rounded-lg border transition-all flex items-center justify-between group ${
                    isSelected
                      ? 'bg-slate-800/90 border-blue-500 text-white shadow-md'
                      : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:bg-slate-800/40 hover:border-slate-700'
                  }`}
                >
                  <div className="min-w-0 pr-2">
                    <div className="flex items-center gap-1.5 font-semibold text-xs truncate">
                      <MapPin className={`w-3.5 h-3.5 shrink-0 ${
                        isSteep ? 'text-red-400' : isModerate ? 'text-amber-400' : 'text-emerald-400'
                      }`} />
                      <span className="truncate group-hover:text-white">{loc.name}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono mt-0.5">
                      <span>Ward {loc.ward}</span>
                      <span>•</span>
                      <span className="flex items-center gap-0.5">
                        <Mountain className="w-2.5 h-2.5 text-slate-400" />
                        {loc.elevation_m}m EL
                      </span>
                    </div>
                  </div>

                  <span className={`font-mono text-[11px] font-bold shrink-0 px-1.5 py-0.5 rounded ${
                    isSteep 
                      ? 'bg-red-950 text-red-400 border border-red-800' 
                      : isModerate
                      ? 'bg-amber-950 text-amber-400 border border-amber-800'
                      : 'bg-slate-900 text-slate-400 border border-slate-800'
                  }`}>
                    {loc.baseline_slope_deg}°
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Priority Active Escalations List */}
        {incidents.length > 0 && (
          <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
            <span className="text-[10px] font-mono text-red-400 font-bold uppercase tracking-wider flex items-center gap-1 px-1">
              <AlertOctagon className="w-3.5 h-3.5" />
              ACTIVE ESCALATIONS ({incidents.length})
            </span>

            <div className="space-y-1">
              {incidents.slice(0, 3).map((inc) => (
                <div
                  key={inc.id}
                  onClick={() => onSelectIncident(inc)}
                  className="bg-red-950/30 border border-red-900/60 hover:border-red-500 p-2 rounded-lg cursor-pointer transition-all hover:bg-red-950/50"
                >
                  <div className="flex items-center justify-between text-[11px] font-bold text-red-200">
                    <span className="truncate">{inc.title.replace('Active Hazard Escalation: ', '')}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-red-400 shrink-0" />
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mt-1">
                    <span className="text-red-400 font-semibold">{inc.severity} RISK</span>
                    <span className="text-slate-300 font-mono text-[9px] bg-slate-900 px-1 rounded">
                      {inc.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>

      {/* Bottom Mission Card */}
      <div className="p-3 bg-slate-950 border-t border-slate-800/80 font-mono text-[10px] text-slate-400 space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-slate-400">JURISDICTION:</span>
          <span className="text-slate-200 font-bold">ICHHYAKAMANA</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-400">SAFETY PROTOCOL:</span>
          <span className="text-emerald-400 font-bold flex items-center gap-1">
            <Activity className="w-2.5 h-2.5" />
            HUMAN-IN-THE-LOOP
          </span>
        </div>
      </div>

    </aside>
  );
};
