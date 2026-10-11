import type {
  HealthResponse,
  FleetStatusSummary,
  CameraSource,
  IncidentEvent,
  AnalyticsOverview,
  VideoFile
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorText = await res.text();
    let errorDetail = errorText;
    try {
      const parsed = JSON.parse(errorText);
      errorDetail = parsed.detail || errorText;
    } catch {
      // Keep plain text
    }
    throw new Error(errorDetail || `HTTP error ${res.status}`);
  }
  return res.json();
}

export const api = {
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE_URL}/health`);
    return handleResponse<HealthResponse>(res);
  },

  async getFleetStatus(): Promise<FleetStatusSummary> {
    const res = await fetch(`${API_BASE_URL}/fleet`);
    return handleResponse<FleetStatusSummary>(res);
  },

  async getBusStatus(busId: string): Promise<CameraSource> {
    const res = await fetch(`${API_BASE_URL}/fleet/${busId}`);
    return handleResponse<CameraSource>(res);
  },

  async controlStream(
    busId: string,
    action: 'START' | 'PAUSE' | 'RESUME' | 'STOP' | 'REPLAY',
    playbackSpeed: number = 1.0,
    videoPath?: string
  ): Promise<CameraSource> {
    const res = await fetch(`${API_BASE_URL}/fleet/${busId}/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action,
        playback_speed: playbackSpeed,
        video_path: videoPath
      })
    });
    return handleResponse<CameraSource>(res);
  },

  async getEvents(params?: {
    camera_id?: string;
    event_type?: string;
    severity?: string;
    review_status?: string;
    limit?: number;
    offset?: number;
  }): Promise<IncidentEvent[]> {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== '') {
          query.append(key, String(val));
        }
      });
    }
    const res = await fetch(`${API_BASE_URL}/events?${query.toString()}`);
    return handleResponse<IncidentEvent[]>(res);
  },

  async updateEventReview(
    eventId: number,
    reviewStatus: 'VERIFIED' | 'FALSE_POSITIVE' | 'RESOLVED' | 'PENDING',
    reviewNotes?: string
  ): Promise<IncidentEvent> {
    const res = await fetch(`${API_BASE_URL}/events/${eventId}/review`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        review_status: reviewStatus,
        review_notes: reviewNotes
      })
    });
    return handleResponse<IncidentEvent>(res);
  },

  async getAnalytics(): Promise<AnalyticsOverview> {
    const res = await fetch(`${API_BASE_URL}/analytics/overview`);
    return handleResponse<AnalyticsOverview>(res);
  },

  async getVideos(): Promise<VideoFile[]> {
    const res = await fetch(`${API_BASE_URL}/sources/videos`);
    return handleResponse<VideoFile[]>(res);
  },

  async uploadVideo(file: File): Promise<{ filename: string; path: string; size_mb: number }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE_URL}/sources/upload`, {
      method: 'POST',
      body: formData
    });
    return handleResponse(res);
  },

  async processVideo(filename: string, cameraId: string = 'BUS-001', maxFrames?: number): Promise<{
    status: string;
    camera_id: string;
    frames_processed: number;
    total_video_frames: number;
    processing_fps: number;
    elapsed_seconds: number;
    incidents_created: number;
    annotated_video_path: string;
  }> {
    const res = await fetch(`${API_BASE_URL}/sources/process-video`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename,
        camera_id: cameraId,
        max_frames: maxFrames
      })
    });
    return handleResponse(res);
  },

  async getANPRReadings(params?: {
    camera_id?: string;
    verification_status?: string;
    limit?: number;
  }): Promise<import('../types').ANPRReadingItem[]> {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== '') {
          query.append(key, String(val));
        }
      });
    }
    const res = await fetch(`${API_BASE_URL}/analytics/anpr?${query.toString()}`);
    return handleResponse<import('../types').ANPRReadingItem[]>(res);
  },

  async getVehicleAnalytics(cameraId: string): Promise<import('../types').CameraVehicleStats> {
    const res = await fetch(`${API_BASE_URL}/analytics/vehicles/${cameraId}`);
    return handleResponse<import('../types').CameraVehicleStats>(res);
  }
};


