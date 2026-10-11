import React, { useState } from 'react';
import { Sparkles, CheckCircle2, Film } from 'lucide-react';
import { api } from '../services/api';

interface AnnotatedVideoPlayerProps {
  onProcessingComplete: () => void;
}

export const AnnotatedVideoPlayer: React.FC<AnnotatedVideoPlayerProps> = ({ onProcessingComplete }) => {
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [selectedBus, setSelectedBus] = useState<string>('BUS-001');
  const [selectedVideo, setSelectedVideo] = useState<string>('demo_road_run.mp4');
  const [availableVideos, setAvailableVideos] = useState<import('../types').VideoFile[]>([]);
  const [videoSrc, setVideoSrc] = useState<string>('http://127.0.0.1:8000/evidence/annotated_demo_road_run_BUS-001.mp4');
  const [resultStats, setResultStats] = useState<{
    fps: number;
    frames: number;
    incidents: number;
    time: number;
  } | null>(null);

  React.useEffect(() => {
    const fetchVideos = async () => {
      try {
        const vids = await api.getVideos();
        setAvailableVideos(vids);
        if (vids.length > 0 && !vids.find(v => v.filename === selectedVideo)) {
          setSelectedVideo(vids[0].filename);
        }
      } catch (e) {
        console.error('Error fetching videos:', e);
      }
    };
    fetchVideos();
  }, []);

  const handleRunInference = async () => {
    setIsProcessing(true);
    setResultStats(null);
    try {
      const res = await api.processVideo(selectedVideo, selectedBus, 240);
      setVideoSrc(`http://127.0.0.1:8000/${res.annotated_video_path}?t=${Date.now()}`);
      setResultStats({
        fps: res.processing_fps,
        frames: res.frames_processed,
        incidents: res.incidents_created,
        time: res.elapsed_seconds
      });
      onProcessingComplete();
    } catch (err: any) {
      alert(`Inference failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Film size={20} color="#3b82f6" />
          <div>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
              Annotated Computer Vision Stream Player
            </h2>
            <p style={{ fontSize: '0.775rem', color: '#94a3b8' }}>
              Real-time neural detection bounding boxes, HUD telemetry, and road defect identification
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          {/* Video Selector */}
          <select
            value={selectedVideo}
            onChange={(e) => setSelectedVideo(e.target.value)}
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              background: '#1e293b',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#38bdf8',
              fontWeight: 600,
              fontSize: '0.8rem',
              outline: 'none'
            }}
          >
            {availableVideos.length > 0 ? (
              availableVideos.map((v) => (
                <option key={v.filename} value={v.filename}>
                  📹 {v.filename} ({v.size_mb} MB)
                </option>
              ))
            ) : (
              <option value="demo_road_run.mp4">📹 demo_road_run.mp4</option>
            )}
          </select>

          <select
            value={selectedBus}
            onChange={(e) => setSelectedBus(e.target.value)}
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              background: '#1e293b',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#f8fafc',
              fontSize: '0.8rem',
              outline: 'none'
            }}
          >
            <option value="BUS-001">Camera: BUS-001 (Route 101)</option>
            <option value="BUS-002">Camera: BUS-002 (Route 204)</option>
            <option value="BUS-003">Camera: BUS-003 (Route 305)</option>
          </select>

          <button
            className="btn btn-primary btn-sm"
            onClick={handleRunInference}
            disabled={isProcessing}
            style={{ minWidth: '170px' }}
          >
            {isProcessing ? (
              <>
                <span className="pulse-dot pulse-dot-amber" />
                <span>Running CUDA AI...</span>
              </>
            ) : (
              <>
                <Sparkles size={14} />
                <span>Run Video AI Pipeline</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Video Container */}
      <div style={{
        position: 'relative',
        width: '100%',
        borderRadius: '12px',
        overflow: 'hidden',
        background: '#090d16',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        aspectRatio: '16/9',
        maxHeight: '480px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <video
          key={videoSrc}
          src={videoSrc}
          controls
          autoPlay
          muted
          loop
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        >
          Your browser does not support HTML5 video playback.
        </video>
      </div>

      {/* Result Metrics Bar */}
      {resultStats && (
        <div style={{
          marginTop: '14px',
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: '10px',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          fontSize: '0.8rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#34d399', fontWeight: 600 }}>
            <CheckCircle2 size={16} />
            <span>Vertical Slice Processed Successfully:</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', fontFamily: 'var(--font-mono)', color: '#cbd5e1' }}>
            <span>Frames: <b style={{ color: '#f8fafc' }}>{resultStats.frames}</b></span>
            <span>Speed: <b style={{ color: '#60a5fa' }}>{resultStats.fps} FPS</b></span>
            <span>Latency: <b style={{ color: '#f8fafc' }}>{resultStats.time}s</b></span>
            <span>New Incidents: <b style={{ color: '#fb7185' }}>{resultStats.incidents}</b></span>
          </div>
        </div>
      )}
    </div>
  );
};
