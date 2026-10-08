# 🏙️ AI Urban Intelligence Platform (SIH26124)

> **Software-only edge simulation for public bus-mounted camera intelligence:** Real-time road hazard detection, multi-object vehicle tracking, traffic density estimation, explainable safety candidate event detection, Indian ANPR/OCR, and live geospatial dashboard telemetry.

---

## 🎯 Problem Statement Alignment (SIH26124)

In smart city transportation initiatives, static CCTV infrastructure suffers from severe blind spots and high deployment costs. This platform simulates **public buses (BUS-001, BUS-002, BUS-003)** acting as continuous mobile sensing nodes across urban transit corridors.

Each bus camera stream processes real-time front-facing road video on local hardware, detects infrastructure hazards (potholes/cracks), counts distinct vehicles without duplication, categorizes traffic density, audits candidate safety incidents, extracts license plates, attaches **simulated GPS coordinates**, and streams live alerts to a centralized municipal dashboard.

---

## 🌟 Key Features & Architectural Modules

1. **Road Defect Detection**:
   - Neural detection (YOLOv8) with fallback optical depression contour analysis.
   - Pothole and road surface degradation localization.
   - Automatic crop extraction saved into `evidence/` repository.

2. **Isolated Multi-Object Tracking & Flow Analytics**:
   - Camera-isolated multi-object tracking (`StreamTracker`) preventing state leakage across buses.
   - Zero double-counting guarantee (`counted_track_ids`).
   - Categorized vehicle counters (`car`, `bus`, `truck`, `motorcycle`, `bicycle`, `person`).
   - Dynamic 4-tier traffic congestion classification (`LOW`, `MEDIUM`, `HIGH`, `CONGESTED`).

3. **Explainable Safety Analytics Rules Engine**:
   - **Proximity Conflict Rule**: Evaluates spatial distance between vehicles and pedestrians/cyclists.
   - **Erratic Swerving / Rash Driving Rule**: Evaluates lateral displacement rate ($\Delta x / \Delta t$) across multi-frame trajectory history.
   - **Audit Transparency**: All events are explicitly flagged as `CANDIDATE_FOR_REVIEW` with human audit disclaimers, never claiming automated conviction or fault.

4. **Automatic Number Plate Recognition (ANPR)**:
   - Indian standard vehicle registration geometry localization.
   - OCR engine (EasyOCR) with regex validation (`^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$`).
   - Confidence thresholding: items below threshold are explicitly marked `NEEDS_REVIEW`.

5. **Simulated GPS Telemetry**:
   - Synthetic route interpolation for Delhi transit corridors (Route 101, 204, 305).
   - High-contrast OpenStreetMap HUD overlays and polyline routes.
   - Distinctly labeled `SIMULATED GPS` across all UI and API contracts.

6. **Real-time Glassmorphic Dashboard**:
   - React 19 + TypeScript + Vite with custom dark-mode glassmorphic theme.
   - Live Leaflet map with animated bus markers and incident markers.
   - Native HTML5 video player with HUD annotations.
   - Real-time WebSocket incident alert feed and inspector modal.

---

## 🏗️ System Architecture

```
                                  [ Public Bus Camera Stream ]
                                                │
                                                ▼
                                    [ OpenCV Video Service ]
                                                │
                      ┌─────────────────────────┼─────────────────────────┐
                      ▼                         ▼                         ▼
            [ YOLOv8 Neural Engine ]    [ StreamTracker (IoU) ]   [ Simulated GPS Engine ]
            • Vehicles & Pedestrians    • Isolated per camera     • Delhi Transit Routes
            • Potholes & Hazards        • Unique counting         • Interpolated Lat/Lon
                      │                         │                         │
                      └─────────────────────────┼─────────────────────────┘
                                                │
                      ┌─────────────────────────┴─────────────────────────┐
                      ▼                                                   ▼
            [ Safety Analytics Engine ]                          [ ANPR / OCR Engine ]
            • Temporal proximity rules                           • Plate geometry crop
            • Lateral swerving metrics                           • Regex validation
            • CANDIDATE_FOR_REVIEW tags                          • NEEDS_REVIEW flags
                                                │
                                                ▼
                                 [ FastAPI Backend Core ]
                                 • SQLite Async (aiosqlite)
                                 • WebSocket Alert Broadcaster
                                                │
                                                ▼
                                 [ React 19 Web Dashboard ]
                                 • Live OSM Map & Polylines
                                 • Annotated HUD Player
                                 • Live Incident Feed
```

---

## 💻 Tech Stack & Environment

- **Backend**: Python 3.11, FastAPI, Uvicorn, SQLAlchemy 2.0 (Async), aiosqlite, Pydantic v2
- **Deep Learning / Vision**: PyTorch 2.5.1 + CUDA 12.1 (NVIDIA RTX 4050 6GB GPU accelerated), Ultralytics YOLOv8, OpenCV 4.9+, EasyOCR
- **Frontend**: React 19, TypeScript, Vite, Leaflet, Lucide Icons, Vanilla CSS Design System
- **Testing**: pytest, pytest-asyncio, httpx

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) NVIDIA GPU with CUDA for accelerated neural inference

### 1. Backend Setup
```powershell
# Navigate to project root
cd "g:\major project"

# Install backend dependencies
pip install -r backend/requirements.txt

# Start FastAPI server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
API Documentation will be accessible at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
```powershell
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Dashboard will be accessible at: `http://127.0.0.1:5173`

### 3. Generate Sample Video & Run End-to-End Demo
```powershell
# Generate synthetic road driving video with vehicles and defects
python scripts/generate_sample_road_video.py

# Video will be saved to sample_videos/demo_road_run.mp4
# In the Web Dashboard, select BUS-001 and click "Start Stream"
```

---

## 🧪 Automated Test Suite

Run all 18 backend unit and integration tests:
```powershell
pytest backend/tests -v
```
All tests cover health probes, vertical video processing slice, isolated multi-bus tracking, vehicle counting, simulated GPS interpolation, safety rule assertions, ANPR regex validation, and WebSocket broadcasts.

---

## 📊 Dataset Audit & Fine-Tuning Pipeline

When real pothole or road damage datasets (e.g. RDD2022 / Roboflow YOLO format) are downloaded:

```powershell
# 1. Audit class balance and label formatting
python scripts/audit_dataset.py --data-dir datasets/road_damage

# 2. Fine-tune YOLO on local NVIDIA RTX 4050 GPU
python scripts/train_road_defects.py --data-yaml datasets/road_damage/data.yaml --epochs 30 --batch 16
```

---

## ⚖️ Ethical & Transparency Guardrails

1. **Simulated GPS**: All geographic coordinates are explicitly tagged as `is_simulated_gps: true` and labeled `SIMULATED GPS` on the map and video HUDs.
2. **Explainable Safety Alerts**: Safety incident candidates (`PROXIMITY_CONFLICT`, `RASH_DRIVING_CANDIDATE`) are surfaced as review candidates for municipal operators with explainable metrics (measured pixel distance, lateral displacement rate) and do not claim automated conviction.
3. **Review Flagging for OCR**: License plate readings with low confidence or irregular formatting are explicitly flagged as `NEEDS_REVIEW`.

---

## 📄 License
MIT License. Built for Smart India Hackathon (SIH26124).
