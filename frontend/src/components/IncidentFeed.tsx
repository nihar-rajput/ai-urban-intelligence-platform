import React from 'react';
import { AlertCircle, Check, X, Shield, Eye, Clock, MapPin } from 'lucide-react';
import type { IncidentEvent } from '../types';

interface IncidentFeedProps {
  incidents: IncidentEvent[];
  onReview: (eventId: number, status: 'VERIFIED' | 'FALSE_POSITIVE' | 'RESOLVED') => void;
  onSelectIncident: (incident: IncidentEvent) => void;
  isLoading: boolean;
}

export const IncidentFeed: React.FC<IncidentFeedProps> = ({
  incidents,
  onReview,
  onSelectIncident,
  isLoading
}) => {
  const getSeverityBadgeClass = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
      case 'HIGH':
        return 'badge-critical';
      case 'MEDIUM':
        return 'badge-warning';
      default:
        return 'badge-neutral';
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'VERIFIED':
      case 'RESOLVED':
        return 'badge-online';
      case 'FALSE_POSITIVE':
        return 'badge-critical';
      default:
        return 'badge-warning';
    }
  };

  const [filterSeverity, setFilterSeverity] = React.useState<string>('ALL');
  const [filterStatus, setFilterStatus] = React.useState<string>('ALL');
  const [filterBus, setFilterBus] = React.useState<string>('ALL');

  const filteredIncidents = incidents.filter((inc) => {
    if (filterSeverity !== 'ALL' && inc.severity.toUpperCase() !== filterSeverity) return false;
    if (filterStatus !== 'ALL' && inc.review_status.toUpperCase() !== filterStatus) return false;
    if (filterBus !== 'ALL' && inc.camera_id !== filterBus) return false;
    return true;
  });

  return (
    <div className="glass-panel" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AlertCircle size={20} color="#f43f5e" />
          <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
            Incident Alert Feed & Human Review Queue
          </h2>
        </div>

        {/* Filter Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <select
            value={filterBus}
            onChange={(e) => setFilterBus(e.target.value)}
            style={{
              padding: '4px 8px',
              borderRadius: '6px',
              background: '#1e293b',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#cbd5e1',
              fontSize: '0.75rem'
            }}
          >
            <option value="ALL">All Cameras</option>
            <option value="BUS-001">BUS-001</option>
            <option value="BUS-002">BUS-002</option>
            <option value="BUS-003">BUS-003</option>
          </select>

          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            style={{
              padding: '4px 8px',
              borderRadius: '6px',
              background: '#1e293b',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#cbd5e1',
              fontSize: '0.75rem'
            }}
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            style={{
              padding: '4px 8px',
              borderRadius: '6px',
              background: '#1e293b',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#cbd5e1',
              fontSize: '0.75rem'
            }}
          >
            <option value="ALL">All Statuses</option>
            <option value="PENDING">Pending Review</option>
            <option value="VERIFIED">Verified</option>
            <option value="FALSE_POSITIVE">False Positive</option>
            <option value="RESOLVED">Resolved</option>
          </select>

          <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
            {filteredIncidents.length} / {incidents.length}
          </span>
        </div>
      </div>

      {incidents.length === 0 ? (
        <div style={{
          padding: '48px 24px',
          textAlign: 'center',
          background: 'rgba(15, 23, 42, 0.4)',
          borderRadius: '12px',
          border: '1px dashed rgba(255, 255, 255, 0.1)'
        }}>
          <Shield size={36} color="#475569" style={{ marginBottom: '12px' }} />
          <p style={{ color: '#94a3b8', fontSize: '0.9rem', fontWeight: 600 }}>
            No Incidents Detected Yet
          </p>
          <p style={{ color: '#64748b', fontSize: '0.775rem', marginTop: '4px', maxWidth: '400px', margin: '4px auto 0' }}>
            Start a simulated bus stream or upload road footage to trigger the computer vision detection pipeline.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {filteredIncidents.map((inc) => (
            <div
              key={inc.id}
              style={{
                background: 'rgba(15, 23, 42, 0.65)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '12px',
                padding: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '14px',
                transition: 'border-color 0.2s ease'
              }}
            >
              {/* Left Column: Details */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flex: 1, minWidth: '280px' }}>
                <div style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '10px',
                  background: inc.severity === 'CRITICAL' || inc.severity === 'HIGH'
                    ? 'rgba(244, 63, 94, 0.15)'
                    : 'rgba(245, 158, 11, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <AlertCircle size={22} color={inc.severity === 'CRITICAL' || inc.severity === 'HIGH' ? '#fb7185' : '#fbbf24'} />
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.9rem', color: '#f8fafc' }}>
                      {inc.event_type.replace(/_/g, ' ')}
                    </span>
                    <span className={`badge ${getSeverityBadgeClass(inc.severity)}`} style={{ fontSize: '0.675rem' }}>
                      {inc.severity}
                    </span>
                    <span className={`badge ${getStatusBadgeClass(inc.review_status)}`} style={{ fontSize: '0.675rem' }}>
                      {inc.review_status}
                    </span>
                  </div>

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '14px',
                    fontSize: '0.75rem',
                    color: '#94a3b8',
                    marginTop: '6px',
                    flexWrap: 'wrap'
                  }}>
                    <span style={{ fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>
                      Bus: {inc.camera_id}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Clock size={12} /> {inc.timestamp.toFixed(1)}s
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#c084fc' }}>
                      <MapPin size={12} /> {inc.latitude.toFixed(4)}, {inc.longitude.toFixed(4)} (SIM)
                    </span>
                    <span style={{ fontWeight: 600 }}>
                      Conf: {(inc.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Right Column: Actions */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => onSelectIncident(inc)}
                  title="View evidence & details"
                >
                  <Eye size={13} /> View
                </button>

                {inc.review_status === 'PENDING' && (
                  <>
                    <button
                      className="btn btn-success btn-sm"
                      disabled={isLoading}
                      onClick={() => onReview(inc.id, 'VERIFIED')}
                      title="Verify incident as real defect"
                    >
                      <Check size={13} /> Verify
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      disabled={isLoading}
                      onClick={() => onReview(inc.id, 'FALSE_POSITIVE')}
                      title="Mark as false positive"
                    >
                      <X size={13} /> False Alarm
                    </button>
                  </>
                )}

                {inc.review_status === 'VERIFIED' && (
                  <button
                    className="btn btn-primary btn-sm"
                    disabled={isLoading}
                    onClick={() => onReview(inc.id, 'RESOLVED')}
                    title="Mark repaired or resolved"
                  >
                    Resolve
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
