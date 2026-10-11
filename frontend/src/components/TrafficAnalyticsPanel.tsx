import React, { useState, useEffect } from 'react';
import { BarChart3, Car, Bus, Truck, Bike, Users, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import type { CameraVehicleStats } from '../types';

interface TrafficAnalyticsPanelProps {
  densityMap?: Record<string, string>;
}

export const TrafficAnalyticsPanel: React.FC<TrafficAnalyticsPanelProps> = ({ densityMap }) => {
  const [selectedBus, setSelectedBus] = useState<string>('BUS-001');
  const [stats, setStats] = useState<CameraVehicleStats | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchStats = async () => {
    setIsLoading(true);
    try {
      const data = await api.getVehicleAnalytics(selectedBus);
      setStats(data);
    } catch (err) {
      console.error(`Failed to fetch stats for ${selectedBus}:`, err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, [selectedBus]);

  const density = densityMap?.[selectedBus] || stats?.density_level || 'LOW';

  const getDensityColor = (d: string) => {
    switch (d.toUpperCase()) {
      case 'CONGESTED': return '#f43f5e';
      case 'HIGH': return '#fb923c';
      case 'MEDIUM': return '#fbbf24';
      default: return '#34d399';
    }
  };

  const counts = stats?.counts_by_class || {};
  const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;

  const categories = [
    { key: 'car', label: 'Cars', icon: Car, count: counts['car'] || 0, color: '#38bdf8' },
    { key: 'bus', label: 'Buses', icon: Bus, count: counts['bus'] || 0, color: '#818cf8' },
    { key: 'truck', label: 'Heavy Trucks', icon: Truck, count: counts['truck'] || 0, color: '#f59e0b' },
    { key: 'motorcycle', label: 'Motorcycles', icon: Bike, count: counts['motorcycle'] || 0, color: '#34d399' },
    { key: 'bicycle', label: 'Bicycles', icon: Bike, count: counts['bicycle'] || 0, color: '#a78bfa' },
    { key: 'person', label: 'Pedestrians', icon: Users, count: counts['person'] || 0, color: '#ec4899' },
  ];

  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            background: 'rgba(129, 140, 248, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <BarChart3 size={20} color="#818cf8" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
              Traffic Density & Multimodal Flow Breakdown
            </h2>
            <p style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '2px' }}>
              Isolated stream classification & vehicle volume distribution
            </p>
          </div>
        </div>

        {/* Bus Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {(['BUS-001', 'BUS-002', 'BUS-003'] as const).map((bus) => (
            <button
              key={bus}
              onClick={() => setSelectedBus(bus)}
              className="btn btn-sm"
              style={{
                background: selectedBus === bus ? 'rgba(56, 189, 248, 0.2)' : 'rgba(15, 23, 42, 0.6)',
                borderColor: selectedBus === bus ? '#38bdf8' : 'rgba(255, 255, 255, 0.1)',
                color: selectedBus === bus ? '#38bdf8' : '#94a3b8',
                fontWeight: 600,
                fontSize: '0.75rem'
              }}
            >
              {bus}
            </button>
          ))}
          <button
            className="btn btn-secondary btn-sm"
            onClick={fetchStats}
            title="Refresh Traffic Stats"
            disabled={isLoading}
          >
            <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Top Metric Strip */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '14px',
        marginBottom: '20px'
      }}>
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '10px',
          padding: '14px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>DENSITY LEVEL</span>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: getDensityColor(density), marginTop: '4px' }}>
              {density}
            </div>
          </div>
          <div style={{
            width: '14px',
            height: '14px',
            borderRadius: '50%',
            background: getDensityColor(density),
            boxShadow: `0 0 10px ${getDensityColor(density)}`
          }} />
        </div>

        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '10px',
          padding: '14px'
        }}>
          <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>UNIQUE VEHICLES COUNTED</span>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', marginTop: '4px' }}>
            {stats?.total_unique_vehicles || 0}
          </div>
        </div>

        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '10px',
          padding: '14px'
        }}>
          <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>ACTIVE TRACKS IN FRAME</span>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#38bdf8', marginTop: '4px' }}>
            {stats?.active_tracks || 0}
          </div>
        </div>
      </div>

      {/* Category Breakdown Progress Bars */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {categories.map((cat) => {
          const Icon = cat.icon;
          const pct = Math.round((cat.count / total) * 100);
          return (
            <div
              key={cat.key}
              style={{
                background: 'rgba(15, 23, 42, 0.4)',
                borderRadius: '8px',
                padding: '10px 14px',
                border: '1px solid rgba(255, 255, 255, 0.05)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: '#cbd5e1' }}>
                  <Icon size={14} color={cat.color} />
                  <span>{cat.label}</span>
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#f8fafc' }}>
                  {cat.count} <span style={{ color: '#64748b', fontWeight: 400, fontSize: '0.75rem' }}>({pct}%)</span>
                </div>
              </div>

              {/* Progress bar */}
              <div style={{
                height: '6px',
                width: '100%',
                background: 'rgba(255, 255, 255, 0.08)',
                borderRadius: '3px',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${pct}%`,
                  background: cat.color,
                  borderRadius: '3px',
                  transition: 'width 0.4s ease'
                }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
