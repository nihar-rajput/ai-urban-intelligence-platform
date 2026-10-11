export interface GPUInfo {
  is_available: boolean;
  device_name: string | null;
  device_count: number;
  allocated_memory_mb: number | null;
  reserved_memory_mb: number | null;
}

export interface ModelStatus {
  name: string;
  loaded: boolean;
  path: string;
  device: string;
  supported_classes: string[];
}

export interface HealthResponse {
  status: string;
  project: string;
  version: string;
  timestamp: string;
  gpu: GPUInfo;
  active_streams: number;
  models: Record<string, ModelStatus>;
}

export interface CameraSource {
  id: number;
  bus_id: string;
  name: string;
  stream_url_or_path: string | null;
  status: 'STOPPED' | 'RUNNING' | 'PAUSED' | 'ERROR';
  is_active: boolean;
  fps: number;
  current_lat: number | null;
  current_lon: number | null;
  total_frames_processed: number;
  total_incidents_detected: number;
  created_at: string;
  updated_at: string;
}

export interface FleetStatusSummary {
  total_buses: number;
  active_buses: number;
  stopped_buses: number;
  sources: CameraSource[];
}

export interface IncidentEvent {
  id: number;
  event_uuid: string;
  event_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  camera_id: string;
  track_id: number | null;
  timestamp: number;
  latitude: number;
  longitude: number;
  is_simulated_gps: boolean;
  evidence_image_path: string | null;
  review_status: 'PENDING' | 'VERIFIED' | 'FALSE_POSITIVE' | 'RESOLVED';
  review_notes: string | null;
  metadata_json: string | null;
  created_at: string;
}

export interface AnalyticsOverview {
  total_incidents: number;
  pending_reviews: number;
  resolved_incidents: number;
  incidents_by_type: Record<string, number>;
  incidents_by_severity: Record<string, number>;
  traffic_density_by_bus: Record<string, string>;
  total_vehicles_tracked: number;
}

export interface VideoFile {
  filename: string;
  path: string;
  size_mb: number;
  extension: string;
}

export interface ANPRReadingItem {
  id: number;
  camera_id: string;
  track_id: number | null;
  plate_text: string;
  confidence: number;
  evidence_crop_path: string | null;
  verification_status: 'VERIFIED' | 'NEEDS_REVIEW' | 'REJECTED';
  timestamp: number;
  created_at: string | null;
}

export interface CameraVehicleStats {
  camera_id: string;
  active_tracks: number;
  total_unique_vehicles: number;
  counts_by_class: Record<string, number>;
  density_level: string;
}
