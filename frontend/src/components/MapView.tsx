import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Layers, Crosshair, Mountain, MapPin } from 'lucide-react';
import type { Location, Incident } from '../types';

// Fix Leaflet default marker icon paths
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom High-Contrast SVG Radar Markers
const createCustomIcon = (color: string, isRadar: boolean = false) => {
  return L.divIcon({
    className: 'custom-radar-marker',
    html: `
      <div style="
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
      ">
        <div style="
          position: absolute;
          width: 28px;
          height: 28px;
          border-radius: 50%;
          background: ${color}33;
          ${isRadar ? 'animation: pulse-radar 1.5s infinite;' : ''}
        "></div>
        <div style="
          position: relative;
          background: ${color};
          width: 14px;
          height: 14px;
          border-radius: 50%;
          border: 2px solid #ffffff;
          box-shadow: 0 0 10px ${color};
        "></div>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -16]
  });
};

const redIcon = createCustomIcon('#ef4444', true);
const amberIcon = createCustomIcon('#f59e0b', true);
const greenIcon = createCustomIcon('#10b981', false);

// Essential Map Resize Fix Component
const MapResizer: React.FC = () => {
  const map = useMap();
  useEffect(() => {
    map.invalidateSize();
    const t1 = setTimeout(() => map.invalidateSize(), 200);
    const t2 = setTimeout(() => map.invalidateSize(), 600);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [map]);
  return null;
};

// Recenter Map Helper
const RecenterMap: React.FC<{ coords: [number, number]; zoom?: number }> = ({ coords, zoom = 12 }) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo(coords, zoom, { duration: 1.0 });
  }, [coords, zoom, map]);
  return null;
};

interface MapViewProps {
  locations: Location[];
  incidents: Incident[];
  selectedLocation: Location | null;
  onSelectLocation: (loc: Location) => void;
  onSelectIncident: (inc: Incident) => void;
}

export const MapView: React.FC<MapViewProps> = ({
  locations,
  incidents,
  selectedLocation,
  onSelectLocation
}) => {
  const defaultCenter: [number, number] = [27.8300, 84.5450]; // Narayanghat-Mugling center
  const [mapLayer, setMapLayer] = useState<'DARK' | 'SATELLITE'>('DARK');

  // Highway polyline corridor path
  const highwayPath: [number, number][] = locations
    .slice()
    .sort((a, b) => a.latitude - b.latitude)
    .map(loc => [loc.latitude, loc.longitude]);

  return (
    <div className="relative w-full h-full min-h-[440px] bg-[#070a12] overflow-hidden rounded-xl border border-slate-800 shadow-2xl flex flex-col">
      
      {/* Top Map Bar: Status & Layer Switcher */}
      <div className="absolute top-3 left-3 z-[400] bg-slate-900/95 backdrop-blur-md border border-slate-700/80 rounded-lg px-3 py-1.5 shadow-2xl text-xs font-mono flex items-center gap-2 pointer-events-auto">
        <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping shrink-0"></span>
        <span className="text-white font-bold tracking-wider">NH-05 CORRIDOR MAP</span>
        <span className="text-slate-400 text-[11px]">(KM 24 to KM 38)</span>
      </div>

      <div className="absolute top-3 right-3 z-[400] flex items-center gap-2 pointer-events-auto">
        <button
          onClick={() => setMapLayer(mapLayer === 'DARK' ? 'SATELLITE' : 'DARK')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/95 hover:bg-slate-800 text-slate-200 text-xs font-mono font-semibold border border-slate-700 shadow-xl transition-all cursor-pointer"
        >
          <Layers size={14} className="text-blue-400 shrink-0 inline-block" />
          <span>{mapLayer === 'DARK' ? 'SATELLITE IMAGERY' : 'DARK MAP'}</span>
        </button>

        <button
          onClick={() => {
            if (selectedLocation) {
              onSelectLocation(selectedLocation);
            }
          }}
          className="p-1.5 rounded-lg bg-slate-900/95 hover:bg-slate-800 text-slate-200 border border-slate-700 shadow-xl transition-all cursor-pointer"
          title="Recenter Highway Corridor"
        >
          <Crosshair size={16} className="text-emerald-400 shrink-0 inline-block" />
        </button>
      </div>

      {/* Map Container */}
      <div className="flex-1 w-full h-full min-h-[400px]">
        <MapContainer
          center={defaultCenter}
          zoom={12}
          scrollWheelZoom={true}
          style={{ width: '100%', height: '100%', minHeight: '400px' }}
        >
          <MapResizer />
          {selectedLocation && (
            <RecenterMap coords={[selectedLocation.latitude, selectedLocation.longitude]} zoom={13} />
          )}

          {/* Dynamic Basemap Layer */}
          {mapLayer === 'DARK' ? (
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              maxZoom={19}
            />
          ) : (
            <TileLayer
              attribution='&copy; Esri, Maxar'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              maxZoom={19}
            />
          )}

          {/* Highway Route Polyline */}
          {highwayPath.length > 1 && (
            <>
              <Polyline
                positions={highwayPath}
                pathOptions={{
                  color: '#3b82f6',
                  weight: 7,
                  opacity: 0.35,
                }}
              />
              <Polyline
                positions={highwayPath}
                pathOptions={{
                  color: '#60a5fa',
                  weight: 3,
                  opacity: 0.95,
                  dashArray: '8, 6'
                }}
              />
            </>
          )}

          {/* Monitored Highway Sectors */}
          {locations.map((loc) => {
            const isHighRisk = loc.baseline_slope_deg >= 32.0;
            const isSelected = selectedLocation?.id === loc.id;
            const markerIcon = isHighRisk ? redIcon : loc.baseline_slope_deg >= 22 ? amberIcon : greenIcon;
            const circleColor = isHighRisk ? '#ef4444' : loc.baseline_slope_deg >= 22 ? '#f59e0b' : '#10b981';

            return (
              <React.Fragment key={loc.id}>
                <Circle
                  center={[loc.latitude, loc.longitude]}
                  radius={isHighRisk ? 550 : 350}
                  pathOptions={{
                    color: circleColor,
                    fillColor: circleColor,
                    fillOpacity: isSelected ? 0.35 : 0.15,
                    weight: isSelected ? 2.5 : 1
                  }}
                />

                <Marker
                  position={[loc.latitude, loc.longitude]}
                  icon={markerIcon}
                  eventHandlers={{
                    click: () => onSelectLocation(loc),
                  }}
                >
                  <Tooltip direction="top" offset={[0, -14]} opacity={0.95} permanent={isSelected}>
                    <div className="bg-slate-900 border border-slate-700 text-white font-mono text-[11px] font-bold px-2 py-0.5 rounded shadow">
                      {loc.name} ({loc.baseline_slope_deg}°)
                    </div>
                  </Tooltip>

                  <Popup offset={[0, -10]}>
                    <div className="p-1 text-white font-sans w-64 space-y-2">
                      <div className="flex items-center justify-between border-b border-slate-700 pb-1.5">
                        <h3 className="font-bold text-sm text-white truncate">{loc.name}</h3>
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold ${
                          isHighRisk ? 'bg-red-950 text-red-300 border border-red-700' : 'bg-slate-800 text-slate-200'
                        }`}>
                          {loc.baseline_slope_deg}° SLOPE
                        </span>
                      </div>

                      <div className="space-y-1 text-xs font-mono">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-300 flex items-center gap-1.5">
                            <Mountain size={14} className="text-blue-400 shrink-0 inline-block" />
                            Elevation:
                          </span>
                          <span className="text-white font-bold">{loc.elevation_m}m</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-slate-300">Highway:</span>
                          <span className="text-white truncate max-w-[120px] font-semibold">{loc.road_name}</span>
                        </div>
                      </div>

                      <button
                        onClick={() => onSelectLocation(loc)}
                        className="mt-2 w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-1.5 rounded text-xs font-mono transition-colors shadow cursor-pointer block text-center"
                      >
                        SELECT SECTOR
                      </button>
                    </div>
                  </Popup>
                </Marker>
              </React.Fragment>
            );
          })}

          {/* Active Incidents */}
          {incidents.map((inc) => {
            if (!inc.latitude || !inc.longitude) return null;
            return (
              <Circle
                key={`inc-${inc.id}`}
                center={[inc.latitude, inc.longitude]}
                radius={700}
                pathOptions={{
                  color: '#ef4444',
                  fillColor: '#dc2626',
                  fillOpacity: 0.35,
                  weight: 3,
                  dashArray: '6, 6'
                }}
              />
            );
          })}

        </MapContainer>
      </div>

      {/* Bottom Map Legend */}
      <div className="bg-[#0e1626] border-t border-slate-800/90 px-3 py-1.5 text-[11px] font-mono text-slate-300 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_6px_#ef4444]"></span>
            <span className="text-red-300 font-semibold">&gt;35° Critical Slope</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <span className="text-amber-300">22–35° Moderate</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            <span className="text-emerald-300">&lt;22° Stable</span>
          </div>
        </div>

        <div className="text-[10px] text-slate-300 flex items-center gap-1">
          <MapPin size={13} className="text-blue-400 shrink-0 inline-block" />
          <span>Click any marker or pill to focus sector</span>
        </div>
      </div>

    </div>
  );
};
