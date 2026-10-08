import React, { useState, useEffect } from 'react';
import { Bus, Cpu, Activity, Clock } from 'lucide-react';
import type { HealthResponse } from '../types';

interface HeaderProps {
  health: HealthResponse | null;
  isConnected: boolean;
}

export const Header: React.FC<HeaderProps> = ({ health, isConnected }) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString() + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="glass-panel" style={{ padding: '16px 24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Brand & Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '46px',
            height: '46px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 18px rgba(59, 130, 246, 0.45)'
          }}>
            <Bus size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontSize: '1.35rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc' }}>
                AI Urban Intelligence Platform
              </h1>
              <span className="badge badge-simulated" style={{ fontSize: '0.65rem' }}>
                SIH26124
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
              Simulated Bus-Mounted Camera Edge AI & Road Defect Monitor
            </p>
          </div>
        </div>

        {/* Telemetry & System Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          {/* Backend Connection */}
          <div className={`badge ${isConnected ? 'badge-online' : 'badge-critical'}`}>
            <span className={`pulse-dot ${isConnected ? 'pulse-dot-green' : 'pulse-dot-red'}`} />
            {isConnected ? 'API CONNECTED' : 'OFFLINE'}
          </div>

          {/* GPU Hardware Status */}
          <div className="badge badge-neutral" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Cpu size={14} color="#60a5fa" />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
              {health?.gpu.is_available
                ? `${health.gpu.device_name?.replace('NVIDIA ', '') || 'CUDA GPU'} (CUDA ON)`
                : 'CPU FALLBACK'}
            </span>
          </div>

          {/* Simulated GPS Indicator */}
          <div className="badge badge-simulated" title="Coordinates are simulated route interpolations">
            <Activity size={13} />
            <span>SIMULATED GPS</span>
          </div>

          {/* Clock */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            color: '#64748b',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.75rem',
            padding: '4px 8px'
          }}>
            <Clock size={13} />
            <span>{timeStr}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
