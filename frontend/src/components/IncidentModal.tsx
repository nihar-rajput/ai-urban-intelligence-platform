import React, { useState } from 'react';
import { X, Check, Camera } from 'lucide-react';
import type { IncidentEvent } from '../types';

interface IncidentModalProps {
  incident: IncidentEvent | null;
  onClose: () => void;
  onReview: (eventId: number, status: 'VERIFIED' | 'FALSE_POSITIVE' | 'RESOLVED', notes?: string) => void;
  isLoading: boolean;
}

export const IncidentModal: React.FC<IncidentModalProps> = ({
  incident,
  onClose,
  onReview,
  isLoading
}) => {
  const [notes, setNotes] = useState<string>('');

  if (!incident) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px'
    }}>
      <div className="glass-panel" style={{
        maxWidth: '650px',
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '24px',
        background: '#0f172a',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        position: 'relative'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.15rem', fontWeight: 800, color: '#f8fafc' }}>
                {incident.event_type.replace(/_/g, ' ')}
              </span>
              <span className="badge badge-critical" style={{ fontSize: '0.7rem' }}>
                {incident.severity}
              </span>
            </div>
            <p style={{ fontSize: '0.775rem', color: '#94a3b8', marginTop: '2px' }}>
              UUID: {incident.event_uuid}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              padding: '6px'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Evidence Snapshot Preview */}
        <div style={{
          width: '100%',
          height: '240px',
          background: 'rgba(0, 0, 0, 0.5)',
          borderRadius: '10px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '18px',
          overflow: 'hidden',
          position: 'relative'
        }}>
          {incident.evidence_image_path ? (
            <img
              src={`http://127.0.0.1:8000/${incident.evidence_image_path}`}
              alt="Incident evidence snapshot"
              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            />
          ) : (
            <div style={{ textAlign: 'center', color: '#64748b' }}>
              <Camera size={38} style={{ marginBottom: '8px', opacity: 0.5 }} />
              <p style={{ fontSize: '0.825rem' }}>No evidence crop captured</p>
            </div>
          )}
          <div style={{
            position: 'absolute',
            bottom: '8px',
            right: '8px',
            background: 'rgba(0, 0, 0, 0.7)',
            padding: '4px 8px',
            borderRadius: '6px',
            fontSize: '0.7rem',
            color: '#c084fc',
            fontFamily: 'var(--font-mono)'
          }}>
            SIMULATED GPS: {incident.latitude.toFixed(4)}, {incident.longitude.toFixed(4)}
          </div>
        </div>

        {/* Metadata Details Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '12px',
          marginBottom: '18px',
          fontSize: '0.8rem'
        }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '10px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8' }}>Camera Source:</span>
            <div style={{ fontWeight: 700, color: '#60a5fa', marginTop: '2px' }}>
              {incident.camera_id}
            </div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '10px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8' }}>Detection Confidence:</span>
            <div style={{ fontWeight: 700, color: '#34d399', marginTop: '2px' }}>
              {(incident.confidence * 100).toFixed(1)}%
            </div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '10px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8' }}>Stream Timestamp:</span>
            <div style={{ fontWeight: 700, color: '#f8fafc', marginTop: '2px' }}>
              {incident.timestamp.toFixed(2)}s
            </div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '10px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8' }}>Current Review Status:</span>
            <div style={{ fontWeight: 700, color: '#fbbf24', marginTop: '2px' }}>
              {incident.review_status}
            </div>
          </div>
        </div>

        {/* Human Review Notes Input */}
        <div style={{ marginBottom: '18px' }}>
          <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>
            Auditor / Engineer Review Notes:
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add verification notes, road department dispatch ref, or false-positive reason..."
            style={{
              width: '100%',
              minHeight: '70px',
              padding: '10px',
              borderRadius: '8px',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#f8fafc',
              fontSize: '0.8rem',
              resize: 'vertical'
            }}
          />
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
          <button
            className="btn btn-secondary"
            onClick={onClose}
          >
            Close
          </button>
          <button
            className="btn btn-danger"
            disabled={isLoading}
            onClick={() => {
              onReview(incident.id, 'FALSE_POSITIVE', notes);
              onClose();
            }}
          >
            Mark False Positive
          </button>
          <button
            className="btn btn-success"
            disabled={isLoading}
            onClick={() => {
              onReview(incident.id, 'VERIFIED', notes);
              onClose();
            }}
          >
            <Check size={14} /> Verify Defect
          </button>
          <button
            className="btn btn-primary"
            disabled={isLoading}
            onClick={() => {
              onReview(incident.id, 'RESOLVED', notes);
              onClose();
            }}
          >
            Mark Resolved
          </button>
        </div>
      </div>
    </div>
  );
};
