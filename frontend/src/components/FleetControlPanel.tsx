import React from 'react';
import { Bus, Play, Pause, Square, RotateCcw, Navigation } from 'lucide-react';
import type { CameraSource } from '../types';

interface FleetControlPanelProps {
  sources: CameraSource[];
  densityMap?: Record<string, string>;
  onControl: (busId: string, action: 'START' | 'PAUSE' | 'RESUME' | 'STOP' | 'REPLAY') => void;
  isLoading: boolean;
}

export const FleetControlPanel: React.FC<FleetControlPanelProps> = ({
  sources,
  densityMap,
  onControl,
  isLoading
}) => {
  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Bus size={20} color="#3b82f6" />
          <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
            Simulated Bus Camera Fleet Sources
          </h2>
        </div>
        <span className="badge badge-simulated" style={{ fontSize: '0.7rem' }}>
          3 Simulated Mounted Streams
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))',
        gap: '16px'
      }}>
        {sources.map((bus) => {
          const isRunning = bus.status === 'RUNNING';
          const isPaused = bus.status === 'PAUSED';

          return (
            <div
              key={bus.bus_id}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                borderRadius: '12px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}
            >
              {/* Bus Header */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{
                      fontWeight: 800,
                      fontSize: '0.95rem',
                      fontFamily: 'var(--font-mono)',
                      color: '#60a5fa'
                    }}>
                      {bus.bus_id}
                    </span>
                    <span className={`badge ${
                      isRunning ? 'badge-online' : isPaused ? 'badge-warning' : 'badge-neutral'
                    }`}>
                      <span className={`pulse-dot ${
                        isRunning ? 'pulse-dot-green' : isPaused ? 'pulse-dot-amber' : ''
                      }`} />
                      {bus.status}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>
                    {bus.name}
                  </p>
                </div>
                <div style={{
                  fontSize: '0.8rem',
                  fontFamily: 'var(--font-mono)',
                  color: isRunning ? '#34d399' : '#64748b',
                  fontWeight: 600
                }}>
                  {isRunning ? `${bus.fps || 24} FPS` : '0 FPS'}
                </div>
              </div>

              {/* Telemetry info */}
              <div style={{
                background: 'rgba(0, 0, 0, 0.25)',
                padding: '8px 12px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.75rem',
                fontFamily: 'var(--font-mono)',
                color: '#94a3b8'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Navigation size={13} color="#a855f7" />
                  <span>
                    {bus.current_lat?.toFixed(4)}, {bus.current_lon?.toFixed(4)}
                  </span>
                </div>
                <span className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>
                  {densityMap?.[bus.bus_id] ? `DENSITY: ${densityMap[bus.bus_id]}` : 'SIMULATED GPS'}
                </span>
              </div>

              {/* Stream Stats Counters */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.725rem',
                color: '#64748b',
                fontFamily: 'var(--font-mono)'
              }}>
                <span>Frames: <b style={{ color: '#cbd5e1' }}>{bus.total_frames_processed}</b></span>
                <span>Incidents: <b style={{ color: '#fb7185' }}>{bus.total_incidents_detected}</b></span>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
                {!isRunning && !isPaused && (
                  <button
                    className="btn btn-primary btn-sm"
                    style={{ flex: 1 }}
                    disabled={isLoading}
                    onClick={() => onControl(bus.bus_id, 'START')}
                  >
                    <Play size={14} /> Start Stream
                  </button>
                )}

                {isRunning && (
                  <>
                    <button
                      className="btn btn-secondary btn-sm"
                      style={{ flex: 1 }}
                      disabled={isLoading}
                      onClick={() => onControl(bus.bus_id, 'PAUSE')}
                    >
                      <Pause size={14} /> Pause
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      disabled={isLoading}
                      onClick={() => onControl(bus.bus_id, 'STOP')}
                    >
                      <Square size={14} />
                    </button>
                  </>
                )}

                {isPaused && (
                  <>
                    <button
                      className="btn btn-success btn-sm"
                      style={{ flex: 1 }}
                      disabled={isLoading}
                      onClick={() => onControl(bus.bus_id, 'RESUME')}
                    >
                      <Play size={14} /> Resume
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      disabled={isLoading}
                      onClick={() => onControl(bus.bus_id, 'STOP')}
                    >
                      <Square size={14} />
                    </button>
                  </>
                )}

                <button
                  className="btn btn-secondary btn-sm"
                  title="Replay from start"
                  disabled={isLoading}
                  onClick={() => onControl(bus.bus_id, 'REPLAY')}
                >
                  <RotateCcw size={14} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
