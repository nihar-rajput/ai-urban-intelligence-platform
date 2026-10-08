import React from 'react';
import { Layers, AlertTriangle, CheckCircle, Database } from 'lucide-react';
import type { HealthResponse } from '../types';

interface ModelStatusBannerProps {
  health: HealthResponse | null;
}

export const ModelStatusBanner: React.FC<ModelStatusBannerProps> = ({ health }) => {
  const vehicleModel = health?.models?.vehicle_detector;
  const defectModel = health?.models?.road_defect_detector;

  return (
    <div className="glass-panel" style={{ padding: '14px 20px', marginBottom: '24px', background: 'rgba(15, 23, 42, 0.65)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Layers size={18} color="#38bdf8" />
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#e2e8f0' }}>
            Inference Engine Status
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
          {/* Vehicle Detector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem' }}>
            <span style={{ color: '#94a3b8' }}>Vehicle & Pedestrian:</span>
            {vehicleModel?.loaded ? (
              <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
                <CheckCircle size={14} /> Ready ({vehicleModel.device.toUpperCase()})
              </span>
            ) : (
              <span style={{ color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <AlertTriangle size={14} /> Auto-download on start ({vehicleModel?.device || 'CUDA'})
              </span>
            )}
          </div>

          {/* Road Defect Detector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem' }}>
            <span style={{ color: '#94a3b8' }}>Pothole & Road Defect:</span>
            {defectModel?.loaded ? (
              <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
                <CheckCircle size={14} /> Fine-tuned Model Loaded
              </span>
            ) : (
              <span style={{ color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Database size={14} color="#f59e0b" />
                <span style={{ color: '#f59e0b' }}>Awaiting Dataset Ingestion (Phase 5)</span>
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
