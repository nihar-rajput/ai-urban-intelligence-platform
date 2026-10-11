import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { ModelStatusBanner } from './components/ModelStatusBanner';
import { SummaryCards } from './components/SummaryCards';
import { FleetControlPanel } from './components/FleetControlPanel';
import { LiveMap } from './components/LiveMap';
import { AnnotatedVideoPlayer } from './components/AnnotatedVideoPlayer';
import { IncidentFeed } from './components/IncidentFeed';
import { IncidentModal } from './components/IncidentModal';
import { ANPRLogPanel } from './components/ANPRLogPanel';
import { TrafficAnalyticsPanel } from './components/TrafficAnalyticsPanel';
import { api } from './services/api';
import type {
  HealthResponse,
  FleetStatusSummary,
  IncidentEvent,
  AnalyticsOverview
} from './types';
import { Upload, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [fleet, setFleet] = useState<FleetStatusSummary | null>(null);
  const [incidents, setIncidents] = useState<IncidentEvent[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [selectedIncident, setSelectedIncident] = useState<IncidentEvent | null>(null);

  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [h, f, inc, an] = await Promise.all([
        api.getHealth(),
        api.getFleetStatus(),
        api.getEvents({ limit: 50 }),
        api.getAnalytics()
      ]);
      setHealth(h);
      setFleet(f);
      setIncidents(inc);
      setAnalytics(an);
      setIsConnected(true);
    } catch (err) {
      console.error('Failed to sync with API:', err);
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 4000);
    return () => clearInterval(interval);
  }, [loadData]);

  // Real-time WebSocket connection for instant alerts
  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://127.0.0.1:8000/api/v1/ws/alerts';
    let ws: WebSocket | null = null;
    let retryTimer: any = null;

    const connectWs = () => {
      try {
        ws = new WebSocket(wsUrl);
        ws.onopen = () => {
          console.log('Connected to real-time incident WebSocket feed.');
        };
        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'INCIDENT_ALERT' && msg.data) {
              setIncidents((prev) => [msg.data, ...prev]);
              setAnalytics((prev) => {
                if (!prev) return prev;
                return {
                  ...prev,
                  total_incidents: prev.total_incidents + 1,
                  pending_reviews: prev.pending_reviews + 1
                };
              });
            }
          } catch (e) {
            console.error('Error parsing WebSocket alert:', e);
          }
        };
        ws.onclose = () => {
          retryTimer = setTimeout(connectWs, 3000);
        };
        ws.onerror = () => {
          if (ws) ws.close();
        };
      } catch (e) {
        retryTimer = setTimeout(connectWs, 3000);
      }
    };

    connectWs();
    return () => {
      if (ws) ws.close();
      if (retryTimer) clearTimeout(retryTimer);
    };
  }, []);

  const handleControlStream = async (
    busId: string,
    action: 'START' | 'PAUSE' | 'RESUME' | 'STOP' | 'REPLAY'
  ) => {
    setIsLoading(true);
    try {
      await api.controlStream(busId, action);
      await loadData();
    } catch (err: any) {
      alert(`Error controlling stream: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReview = async (
    eventId: number,
    status: 'VERIFIED' | 'FALSE_POSITIVE' | 'RESOLVED',
    notes?: string
  ) => {
    setIsLoading(true);
    try {
      await api.updateEventReview(eventId, status, notes);
      await loadData();
    } catch (err: any) {
      alert(`Error updating review: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setUploadStatus(`Uploading ${file.name}...`);
    try {
      const res = await api.uploadVideo(file);
      setUploadStatus(`Uploaded ${res.filename} (${res.size_mb} MB) successfully!`);
      setTimeout(() => setUploadStatus(null), 5000);
    } catch (err: any) {
      setUploadStatus(`Upload failed: ${err.message}`);
      setTimeout(() => setUploadStatus(null), 5000);
    }
  };

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px 20px 48px' }}>
      {/* Platform Header */}
      <Header health={health} isConnected={isConnected} />

      {/* Inference & Model Status Banner */}
      <ModelStatusBanner health={health} />

      {/* Metric Summary Cards */}
      <SummaryCards analytics={analytics} fleet={fleet} />

      {/* Video Ingestion & Stream Management Toolbar */}
      <div className="glass-panel" style={{
        padding: '16px 20px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '14px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <label className="btn btn-secondary btn-sm" style={{ cursor: 'pointer' }}>
            <Upload size={14} />
            <span>Upload Road Video (.mp4, .avi)</span>
            <input
              type="file"
              accept=".mp4,.avi,.mov,.mkv,.webm"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </label>
          {uploadStatus && (
            <span style={{ fontSize: '0.8rem', color: '#60a5fa', fontWeight: 600 }}>
              {uploadStatus}
            </span>
          )}
        </div>

        <button
          className="btn btn-secondary btn-sm"
          onClick={() => loadData()}
          title="Refresh telemetry"
        >
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* Fleet Stream Control Deck */}
      <FleetControlPanel
        sources={fleet?.sources || []}
        densityMap={analytics?.traffic_density_by_bus}
        onControl={handleControlStream}
        isLoading={isLoading}
      />

      {/* Annotated Computer Vision Video Player */}
      <AnnotatedVideoPlayer onProcessingComplete={loadData} />

      {/* Traffic Flow & Vehicle Classification Analytics */}
      <TrafficAnalyticsPanel densityMap={analytics?.traffic_density_by_bus} />

      {/* Automatic Number Plate Recognition (ANPR) Logs & Inspector */}
      <ANPRLogPanel />

      {/* Interactive Leaflet Map with OpenStreetMap */}
      <LiveMap
        sources={fleet?.sources || []}
        incidents={incidents}
        onSelectIncident={(inc) => setSelectedIncident(inc)}
      />

      {/* Real-time Incident Feed & Review Queue */}
      <IncidentFeed
        incidents={incidents}
        onReview={(id, status) => handleReview(id, status)}
        onSelectIncident={(inc) => setSelectedIncident(inc)}
        isLoading={isLoading}
      />

      {/* Modal for Detailed Incident View & Review */}
      <IncidentModal
        incident={selectedIncident}
        onClose={() => setSelectedIncident(null)}
        onReview={handleReview}
        isLoading={isLoading}
      />
    </div>
  );
};

export default App;
