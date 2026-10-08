import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import type { CameraSource, IncidentEvent } from '../types';

interface LiveMapProps {
  sources: CameraSource[];
  incidents: IncidentEvent[];
  onSelectIncident?: (incident: IncidentEvent) => void;
}

export const LiveMap: React.FC<LiveMapProps> = ({ sources, incidents, onSelectIncident }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<{ [key: string]: L.Marker | L.CircleMarker }>({});

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Default to New Delhi coordinates
      const map = L.map(mapContainerRef.current, {
        center: [28.6139, 77.2090],
        zoom: 12,
        zoomControl: true,
        attributionControl: true
      });

      // Standard OpenStreetMap with explicit attribution
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(map);

      // Pre-configured simulated bus routes
      const ROUTE_PATHS: Record<string, { coords: [number, number][]; color: string; name: string }> = {
        'BUS-001': {
          name: 'Route 101 (Connaught Place -> AIIMS)',
          color: '#3b82f6',
          coords: [
            [28.6315, 77.2167],
            [28.6250, 77.2185],
            [28.6129, 77.2295],
            [28.5910, 77.2240],
            [28.5672, 77.2100]
          ]
        },
        'BUS-002': {
          name: 'Route 204 (Nehru Place -> South Extension)',
          color: '#10b981',
          coords: [
            [28.5494, 77.2534],
            [28.5412, 77.2580],
            [28.5700, 77.2370],
            [28.5750, 77.2150]
          ]
        },
        'BUS-003': {
          name: 'Route 305 (Red Fort -> Civil Lines)',
          color: '#f59e0b',
          coords: [
            [28.6562, 77.2410],
            [28.6510, 77.2300],
            [28.6675, 77.2280],
            [28.6810, 77.2200]
          ]
        }
      };

      Object.values(ROUTE_PATHS).forEach((route) => {
        L.polyline(route.coords, {
          color: route.color,
          weight: 4,
          opacity: 0.65,
          dashArray: '8, 8'
        }).addTo(map).bindTooltip(route.name, { sticky: true });
      });

      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;

    // Clear old markers
    Object.values(markersRef.current).forEach((marker) => marker.remove());
    markersRef.current = {};

    // Custom Bus Icon generator
    const createBusIcon = (busId: string, isRunning: boolean) => {
      return L.divIcon({
        className: 'custom-bus-marker',
        html: `
          <div style="
            background: ${isRunning ? '#2563eb' : '#475569'};
            color: #ffffff;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 8px;
            border: 2px solid ${isRunning ? '#60a5fa' : '#94a3b8'};
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
          ">
            <span>🚌</span>
            <span>${busId}</span>
          </div>
        `,
        iconSize: [80, 28],
        iconAnchor: [40, 14]
      });
    };

    // Add Bus Markers
    sources.forEach((bus) => {
      if (bus.current_lat && bus.current_lon) {
        const isRunning = bus.status === 'RUNNING';
        const marker = L.marker([bus.current_lat, bus.current_lon], {
          icon: createBusIcon(bus.bus_id, isRunning)
        }).addTo(map);

        marker.bindPopup(`
          <div style="padding: 4px;">
            <div style="font-weight: bold; font-size: 13px; color: #60a5fa; margin-bottom: 4px;">
              ${bus.bus_id} - ${bus.name}
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">
              Status: <b style="color: ${isRunning ? '#34d399' : '#cbd5e1'}">${bus.status}</b>
            </div>
            <div style="font-size: 10px; color: #c084fc;">
              SIMULATED GPS: ${bus.current_lat.toFixed(4)}, ${bus.current_lon.toFixed(4)}
            </div>
          </div>
        `);

        markersRef.current[`bus-${bus.bus_id}`] = marker;
      }
    });

    // Add Incident Markers
    incidents.slice(0, 30).forEach((inc) => {
      const isCritical = inc.severity === 'CRITICAL' || inc.severity === 'HIGH';
      const color = isCritical ? '#f43f5e' : '#f59e0b';

      const circle = L.circleMarker([inc.latitude, inc.longitude], {
        radius: isCritical ? 9 : 7,
        fillColor: color,
        color: '#ffffff',
        weight: 1.5,
        opacity: 1,
        fillOpacity: 0.85
      }).addTo(map);

      circle.bindPopup(`
        <div style="padding: 4px; min-width: 150px;">
          <div style="font-weight: bold; font-size: 12px; color: ${color}; margin-bottom: 2px;">
            ${inc.event_type.replace(/_/g, ' ')}
          </div>
          <div style="font-size: 11px; color: #cbd5e1; margin-bottom: 2px;">
            Bus: ${inc.camera_id} | Conf: ${(inc.confidence * 100).toFixed(0)}%
          </div>
          <div style="font-size: 10px; color: #94a3b8; margin-bottom: 4px;">
            Status: ${inc.review_status}
          </div>
          <div style="font-size: 9px; color: #c084fc;">
            SIMULATED GPS
          </div>
        </div>
      `);

      if (onSelectIncident) {
        circle.on('click', () => onSelectIncident(inc));
      }

      markersRef.current[`inc-${inc.id}`] = circle;
    });

    return () => {
      // Keep map instance across renders
    };
  }, [sources, incidents]);

  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
            Live Fleet & Defect Spatial Map
          </h2>
          <p style={{ fontSize: '0.775rem', color: '#94a3b8' }}>
            Real-time simulated telemetry with OpenStreetMap & Leaflet
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-simulated" style={{ fontSize: '0.7rem' }}>
            OpenStreetMap Contributors
          </span>
        </div>
      </div>

      <div
        ref={mapContainerRef}
        style={{
          width: '100%',
          height: '420px',
          borderRadius: '12px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          overflow: 'hidden'
        }}
      />
    </div>
  );
};
