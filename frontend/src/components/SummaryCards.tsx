import React from 'react';
import { Video, AlertOctagon, Car, ShieldCheck } from 'lucide-react';
import type { AnalyticsOverview, FleetStatusSummary } from '../types';

interface SummaryCardsProps {
  analytics: AnalyticsOverview | null;
  fleet: FleetStatusSummary | null;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ analytics, fleet }) => {
  const activeBuses = fleet?.active_buses || 0;
  const totalBuses = fleet?.total_buses || 3;
  const totalIncidents = analytics?.total_incidents || 0;
  const pendingReviews = analytics?.pending_reviews || 0;
  const resolvedIncidents = analytics?.resolved_incidents || 0;
  const vehiclesTracked = analytics?.total_vehicles_tracked || 0;

  const cards = [
    {
      label: 'Active Camera Streams',
      value: `${activeBuses} / ${totalBuses}`,
      subtext: activeBuses > 0 ? 'Live telemetry transmitting' : 'Streams idle / paused',
      icon: <Video size={22} color="#3b82f6" />,
      accentGlow: 'rgba(59, 130, 246, 0.25)',
      borderColor: 'rgba(59, 130, 246, 0.3)'
    },
    {
      label: 'Road Defect Incidents',
      value: totalIncidents,
      subtext: `${pendingReviews} pending human review`,
      icon: <AlertOctagon size={22} color="#f43f5e" />,
      accentGlow: 'rgba(244, 63, 94, 0.25)',
      borderColor: 'rgba(244, 63, 94, 0.3)'
    },
    {
      label: 'Human Review Actions',
      value: resolvedIncidents,
      subtext: 'Verified & resolved items',
      icon: <ShieldCheck size={22} color="#10b981" />,
      accentGlow: 'rgba(16, 185, 129, 0.25)',
      borderColor: 'rgba(16, 185, 129, 0.3)'
    },
    {
      label: 'Vehicles Tracked',
      value: vehiclesTracked,
      subtext: 'Unique vehicle IDs recorded',
      icon: <Car size={22} color="#8b5cf6" />,
      accentGlow: 'rgba(139, 92, 246, 0.25)',
      borderColor: 'rgba(139, 92, 246, 0.3)'
    }
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
      gap: '18px',
      marginBottom: '24px'
    }}>
      {cards.map((card, idx) => (
        <div
          key={idx}
          className="glass-panel glass-card-interactive"
          style={{
            padding: '20px',
            position: 'relative',
            overflow: 'hidden',
            borderLeft: `4px solid ${card.borderColor}`
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.825rem', color: '#94a3b8', fontWeight: 600 }}>
              {card.label}
            </span>
            <div style={{
              padding: '8px',
              borderRadius: '10px',
              background: card.accentGlow,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {card.icon}
            </div>
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', marginBottom: '4px', letterSpacing: '-0.02em' }}>
            {card.value}
          </div>
          <div style={{ fontSize: '0.775rem', color: '#64748b' }}>
            {card.subtext}
          </div>
        </div>
      ))}
    </div>
  );
};
