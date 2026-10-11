import React, { useState, useEffect } from 'react';
import { CreditCard, Search, CheckCircle2, AlertTriangle, RefreshCw, Car } from 'lucide-react';
import { api } from '../services/api';
import type { ANPRReadingItem } from '../types';

export const ANPRLogPanel: React.FC = () => {
  const [readings, setReadings] = useState<ANPRReadingItem[]>([]);
  const [search, setSearch] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [cameraFilter, setCameraFilter] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  const fetchReadings = async () => {
    setIsLoading(true);
    try {
      const data = await api.getANPRReadings({ limit: 40 });
      setReadings(data);
    } catch (err) {
      console.error('Failed to fetch ANPR logs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReadings();
    const interval = setInterval(fetchReadings, 6000);
    return () => clearInterval(interval);
  }, []);

  const filtered = readings.filter((r) => {
    if (search && !r.plate_text.toLowerCase().includes(search.toLowerCase())) return false;
    if (statusFilter !== 'ALL' && r.verification_status !== statusFilter) return false;
    if (cameraFilter !== 'ALL' && r.camera_id !== cameraFilter) return false;
    return true;
  });

  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            background: 'rgba(56, 189, 248, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <CreditCard size={20} color="#38bdf8" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
              Automatic Number Plate Recognition (ANPR) Logs
              <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                {readings.length} Detected
              </span>
            </h2>
            <p style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '2px' }}>
              Vehicle license plate extraction, OCR confidence scoring, and Indian format verification
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={fetchReadings}
            title="Refresh ANPR Logs"
            disabled={isLoading}
          >
            <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
          </button>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </button>
        </div>
      </div>

      {isExpanded && (
        <>
          {/* Controls Bar */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            flexWrap: 'wrap',
            marginBottom: '16px',
            background: 'rgba(15, 23, 42, 0.4)',
            padding: '10px 14px',
            borderRadius: '8px',
            border: '1px solid rgba(255, 255, 255, 0.05)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: '200px' }}>
              <Search size={14} color="#64748b" />
              <input
                type="text"
                placeholder="Search registration number (e.g. DL01)..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: '#f8fafc',
                  fontSize: '0.8rem',
                  width: '100%'
                }}
              />
            </div>

            <select
              value={cameraFilter}
              onChange={(e) => setCameraFilter(e.target.value)}
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
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
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
              <option value="VERIFIED">Verified Plates</option>
              <option value="NEEDS_REVIEW">Needs Review</option>
            </select>
          </div>

          {/* Grid of Plates */}
          {filtered.length === 0 ? (
            <div style={{
              padding: '36px 16px',
              textAlign: 'center',
              color: '#64748b',
              fontSize: '0.85rem'
            }}>
              <Car size={32} color="#475569" style={{ margin: '0 auto 8px', display: 'block' }} />
              No license plates detected matching current filters. Run video stream to extract plates.
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
              gap: '12px'
            }}>
              {filtered.map((item, idx) => {
                const isVerified = item.verification_status === 'VERIFIED';
                return (
                  <div
                    key={`${item.id}-${item.plate_text}-${idx}`}
                    style={{
                      background: 'rgba(15, 23, 42, 0.6)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: '10px',
                      padding: '12px 14px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '10px',
                      transition: 'border-color 0.2s ease',
                    }}
                  >
                    {/* Top Row: Camera & Confidence */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                        {item.camera_id} {item.track_id ? `• Track #${item.track_id}` : ''}
                      </span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                        {isVerified ? (
                          <span className="badge badge-online" style={{ fontSize: '0.68rem', display: 'flex', alignItems: 'center', gap: '3px' }}>
                            <CheckCircle2 size={11} /> VERIFIED
                          </span>
                        ) : (
                          <span className="badge badge-warning" style={{ fontSize: '0.68rem', display: 'flex', alignItems: 'center', gap: '3px' }}>
                            <AlertTriangle size={11} /> NEEDS REVIEW
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Realistic High-Security Indian License Plate UI */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'stretch',
                      background: '#ffffff',
                      borderRadius: '6px',
                      border: '2px solid #0f172a',
                      overflow: 'hidden',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
                      height: '42px'
                    }}>
                      {/* Left Blue IND Strip */}
                      <div style={{
                        background: '#1d4ed8',
                        color: '#ffffff',
                        width: '32px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '2px 0',
                        fontSize: '0.6rem',
                        fontWeight: 900,
                        letterSpacing: '0.5px',
                        userSelect: 'none'
                      }}>
                        <span style={{ fontSize: '0.55rem', opacity: 0.9 }}>🇮🇳</span>
                        <span style={{ fontSize: '0.65rem' }}>IND</span>
                      </div>

                      {/* Plate Text Center */}
                      <div style={{
                        flex: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#0f172a',
                        fontFamily: "'Courier New', Courier, monospace",
                        fontWeight: 900,
                        fontSize: '1.1rem',
                        letterSpacing: '2px',
                        textTransform: 'uppercase'
                      }}>
                        {item.plate_text}
                      </div>
                    </div>

                    {/* Bottom Metadata */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.72rem', color: '#64748b' }}>
                      <span>Confidence: <strong style={{ color: isVerified ? '#34d399' : '#fbbf24' }}>{Math.round(item.confidence * 100)}%</strong></span>
                      <span>T: {item.timestamp.toFixed(1)}s</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
};
