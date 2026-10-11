import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, CheckCircle2, Film, Video, AlertCircle, RefreshCw, Layers, Cpu, ShieldAlert, Car } from 'lucide-react';
import { api } from '../services/api';
import type { VideoFile } from '../types';

interface AnnotatedVideoPlayerProps {
  onProcessingComplete: () => void;
}

export const AnnotatedVideoPlayer: React.FC<AnnotatedVideoPlayerProps> = ({ onProcessingComplete }) => {
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [selectedBus, setSelectedBus] = useState<string>('BUS-001');
  const [selectedVideo, setSelectedVideo] = useState<string>('demo_road_run.mp4');
  const [availableVideos, setAvailableVideos] = useState<VideoFile[]>([]);
  const [streamMode, setStreamMode] = useState<'annotated' | 'raw'>('annotated');
  const [videoError, setVideoError] = useState<boolean>(false);
  const [videoLoaded, setVideoLoaded] = useState<boolean>(false);
  const [cacheBust, setCacheBust] = useState<number>(Date.now());
  
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const [resultStats, setResultStats] = useState<{
    fps: number;
    frames: number;
    incidents: number;
    time: number;
    vehicles?: number;
    density?: string;
  } | null>(null);

  // Fetch available videos on mount
  useEffect(() => {
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

  // Compute stream URL
  const videoBaseName = selectedVideo.replace(/\.[^/.]+$/, '');
  const annotatedUrl = `http://127.0.0.1:8000/evidence/annotated_${videoBaseName}_${selectedBus}.mp4?t=${cacheBust}`;
  const rawUrl = `http://127.0.0.1:8000/sample_videos/${selectedVideo}?t=${cacheBust}`;
  const currentVideoUrl = streamMode === 'annotated' ? annotatedUrl : rawUrl;

  // Reset video error on change
  useEffect(() => {
    setVideoError(false);
    setVideoLoaded(false);
  }, [streamMode, selectedBus, selectedVideo, cacheBust]);

  const handleRunInference = async () => {
    setIsProcessing(true);
    setResultStats(null);
    setVideoError(false);
    try {
      const res = await api.processVideo(selectedVideo, selectedBus, 240);
      setCacheBust(Date.now());
      setStreamMode('annotated');
      setResultStats({
        fps: res.processing_fps,
        frames: res.frames_processed,
        incidents: res.incidents_created,
        time: res.elapsed_seconds,
        vehicles: res.unique_vehicles_counted,
        density: res.traffic_density
      });
      onProcessingComplete();
    } catch (err: any) {
      alert(`Inference pipeline error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '22px', marginBottom: '24px', position: 'relative' }}>
      {/* Top Header Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.4))',
            padding: '10px',
            borderRadius: '10px',
            border: '1px solid rgba(59, 130, 246, 0.3)'
          }}>
            <Film size={22} color="#60a5fa" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                Annotated Computer Vision Stream Player
              </h2>
              <span className="badge badge-info" style={{ fontSize: '0.68rem', letterSpacing: '0.05em' }}>
                H.264 HARDWARE STREAM
              </span>
            </div>
            <p style={{ fontSize: '0.785rem', color: '#94a3b8', margin: '3px 0 0 0' }}>
              Real-time neural bounding boxes, Indian road defect identification, DeepSORT vehicle tracking & telemetry HUD
            </p>
          </div>
        </div>

        {/* Action & Stream Selectors */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          {/* Stream Mode Switcher */}
          <div style={{
            display: 'inline-flex',
            background: '#0f172a',
            borderRadius: '8px',
            padding: '3px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <button
              onClick={() => setStreamMode('annotated')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '5px 11px',
                borderRadius: '6px',
                border: 'none',
                background: streamMode === 'annotated' ? 'linear-gradient(135deg, #2563eb, #1d4ed8)' : 'transparent',
                color: streamMode === 'annotated' ? '#ffffff' : '#94a3b8',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              <Cpu size={13} />
              <span>AI Neural Stream</span>
            </button>
            <button
              onClick={() => setStreamMode('raw')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '5px 11px',
                borderRadius: '6px',
                border: 'none',
                background: streamMode === 'raw' ? 'linear-gradient(135deg, #0ea5e9, #0284c7)' : 'transparent',
                color: streamMode === 'raw' ? '#ffffff' : '#94a3b8',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              <Video size={13} />
              <span>Raw Bus Camera Feed</span>
            </button>
          </div>

          {/* Video Selector */}
          <select
            value={selectedVideo}
            onChange={(e) => setSelectedVideo(e.target.value)}
            disabled={isProcessing}
            style={{
              padding: '7px 12px',
              borderRadius: '8px',
              background: '#1e293b',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              color: '#38bdf8',
              fontWeight: 600,
              fontSize: '0.8rem',
              outline: 'none',
              cursor: 'pointer'
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

          {/* Bus Stream Selector */}
          <select
            value={selectedBus}
            onChange={(e) => setSelectedBus(e.target.value)}
            disabled={isProcessing}
            style={{
              padding: '7px 12px',
              borderRadius: '8px',
              background: '#1e293b',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              color: '#f8fafc',
              fontSize: '0.8rem',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            <option value="BUS-001">Camera: BUS-001 (Route 101)</option>
            <option value="BUS-002">Camera: BUS-002 (Route 204)</option>
            <option value="BUS-003">Camera: BUS-003 (Route 305)</option>
          </select>

          {/* Inference Action Trigger */}
          <button
            className="btn btn-primary btn-sm"
            onClick={handleRunInference}
            disabled={isProcessing}
            style={{ minWidth: '180px', fontWeight: 600 }}
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

      {/* Main Video Viewport */}
      <div style={{
        position: 'relative',
        width: '100%',
        borderRadius: '12px',
        overflow: 'hidden',
        background: '#070a12',
        border: '1px solid rgba(255, 255, 255, 0.12)',
        aspectRatio: '16/9',
        maxHeight: '520px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)'
      }}>
        {/* Active HTML5 Video Player */}
        <video
          ref={videoRef}
          key={currentVideoUrl}
          src={currentVideoUrl}
          controls
          autoPlay
          muted
          loop
          playsInline
          onLoadedData={() => {
            setVideoLoaded(true);
            setVideoError(false);
          }}
          onError={() => {
            setVideoError(true);
            setVideoLoaded(false);
          }}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            display: (videoError || isProcessing) ? 'none' : 'block'
          }}
        >
          Your browser does not support HTML5 video playback.
        </video>

        {/* Live Stream Mode HUD Overlay (Top-Left of Screen) */}
        {!videoError && !isProcessing && videoLoaded && (
          <div style={{
            position: 'absolute',
            top: '12px',
            left: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: 'rgba(15, 23, 42, 0.75)',
            backdropFilter: 'blur(8px)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            borderRadius: '6px',
            padding: '4px 10px',
            fontSize: '0.72rem',
            color: '#f8fafc',
            pointerEvents: 'none',
            zIndex: 10
          }}>
            <span className={`pulse-dot ${streamMode === 'annotated' ? 'pulse-dot-green' : 'pulse-dot-blue'}`} />
            <span style={{ fontWeight: 700, letterSpacing: '0.04em' }}>
              {streamMode === 'annotated' ? `AI ANNOTATED STREAM [${selectedBus}]` : `RAW CAMERA SENSOR [${selectedBus}]`}
            </span>
          </div>
        )}

        {/* Cinematic CUDA AI Processing Overlay */}
        {isProcessing && (
          <div style={{
            position: 'absolute',
            inset: 0,
            background: 'radial-gradient(circle at center, rgba(15, 23, 42, 0.95), rgba(3, 7, 18, 0.98))',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
            textAlign: 'center',
            zIndex: 20
          }}>
            <div style={{ position: 'relative', width: '70px', height: '70px', marginBottom: '20px' }}>
              <div style={{
                position: 'absolute',
                inset: 0,
                borderRadius: '50%',
                border: '3px solid rgba(59, 130, 246, 0.2)',
                borderTopColor: '#3b82f6',
                animation: 'spin 1.2s linear infinite'
              }} />
              <div style={{
                position: 'absolute',
                inset: '10px',
                borderRadius: '50%',
                border: '3px solid rgba(16, 185, 129, 0.2)',
                borderBottomColor: '#10b981',
                animation: 'spin 0.8s linear infinite reverse'
              }} />
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
                height: '100%'
              }}>
                <Cpu size={26} color="#60a5fa" />
              </div>
            </div>

            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
              CUDA Neural Pipeline Active on {selectedBus}
            </h3>
            <p style={{ fontSize: '0.825rem', color: '#94a3b8', maxWidth: '480px', margin: '0 auto 16px auto', lineHeight: 1.5 }}>
              Executing YOLOv8 Pothole Detector, ByteTrack Vehicle Flow Count, Rash Driving Audit & H.264 Encoder...
            </p>

            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', justifyContent: 'center' }}>
              <span className="badge badge-info" style={{ fontSize: '0.72rem' }}>
                <Car size={12} style={{ marginRight: '4px' }} /> Tracking Vehicles
              </span>
              <span className="badge badge-danger" style={{ fontSize: '0.72rem' }}>
                <ShieldAlert size={12} style={{ marginRight: '4px' }} /> Pothole Extraction
              </span>
              <span className="badge badge-success" style={{ fontSize: '0.72rem' }}>
                <Layers size={12} style={{ marginRight: '4px' }} /> ANPR Verification
              </span>
            </div>
          </div>
        )}

        {/* Stream Standby / Error Fallback State */}
        {videoError && !isProcessing && (
          <div style={{
            position: 'absolute',
            inset: 0,
            background: 'radial-gradient(circle at center, rgba(15, 23, 42, 0.95), rgba(7, 10, 18, 0.98))',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
            textAlign: 'center',
            zIndex: 15
          }}>
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              borderRadius: '50%',
              padding: '16px',
              marginBottom: '16px'
            }}>
              <AlertCircle size={36} color="#f87171" />
            </div>

            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', marginBottom: '6px' }}>
              {streamMode === 'annotated' ? 'No Annotated Stream Available Yet' : 'Camera Feed Offline'}
            </h3>
            <p style={{ fontSize: '0.825rem', color: '#94a3b8', maxWidth: '460px', marginBottom: '20px', lineHeight: 1.5 }}>
              {streamMode === 'annotated'
                ? `Inference has not been run for ${selectedVideo} on ${selectedBus}. Click below to run the end-to-end computer vision pipeline, or preview the raw bus camera feed.`
                : `Could not load ${selectedVideo}. Please check that the backend server is reachable.`
              }
            </p>

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
              <button
                className="btn btn-primary btn-sm"
                onClick={handleRunInference}
                style={{ padding: '8px 18px', fontWeight: 600 }}
              >
                <Sparkles size={14} />
                <span>Run Video AI Pipeline Now</span>
              </button>

              {streamMode === 'annotated' && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => setStreamMode('raw')}
                  style={{ padding: '8px 18px' }}
                >
                  <Video size={14} />
                  <span>Preview Raw Camera Feed</span>
                </button>
              )}

              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setCacheBust(Date.now())}
                style={{ padding: '8px 14px' }}
                title="Retry loading stream"
              >
                <RefreshCw size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Result Metrics Bar */}
      {resultStats && (
        <div style={{
          marginTop: '16px',
          background: 'linear-gradient(90deg, rgba(16, 185, 129, 0.12), rgba(59, 130, 246, 0.08))',
          border: '1px solid rgba(16, 185, 129, 0.35)',
          borderRadius: '10px',
          padding: '14px 18px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '14px',
          fontSize: '0.825rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#34d399', fontWeight: 600 }}>
            <CheckCircle2 size={18} />
            <span>AI Pipeline Completed & Stream Encoded:</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '22px', fontFamily: 'var(--font-mono)', color: '#cbd5e1', flexWrap: 'wrap' }}>
            <span>Frames: <b style={{ color: '#f8fafc' }}>{resultStats.frames}</b></span>
            <span>Speed: <b style={{ color: '#60a5fa' }}>{resultStats.fps} FPS</b></span>
            <span>Latency: <b style={{ color: '#f8fafc' }}>{resultStats.time}s</b></span>
            <span>Incidents: <b style={{ color: '#fb7185' }}>{resultStats.incidents}</b></span>
            {resultStats.vehicles !== undefined && (
              <span>Vehicles: <b style={{ color: '#fbbf24' }}>{resultStats.vehicles}</b></span>
            )}
            {resultStats.density && (
              <span>Density: <b style={{ color: '#a78bfa' }}>{resultStats.density}</b></span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
