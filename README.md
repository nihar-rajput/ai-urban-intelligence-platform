# 🏙️ AI Urban Intelligence Platform (SIH26124)

> **Sponsor**: Bharat Electronics Limited (BEL)  
> **Problem Statement**: AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet (SIH26124)  
> **Hardware Target**: Windows 11 development laptop with NVIDIA RTX 4050 (6 GB VRAM) & 16 GB RAM.  
> **Repository**: [https://github.com/nihar-rajput/ai-urban-intelligence-platform](https://github.com/nihar-rajput/ai-urban-intelligence-platform)

---

## 🎯 Problem Statement Alignment (BEL / SIH26124)

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
   - Dedicated **Indian High-Security License Plate (HSRP)** UI panel with blue `IND` strip.

5. **Simulated GPS Telemetry**:
   - Synthetic route interpolation for Delhi transit corridors (Route 101, 204, 305).
   - High-contrast OpenStreetMap HUD overlays and polyline routes.
   - Distinctly labeled `SIMULATED GPS` across all UI and API contracts.

6. **Real-time Glassmorphic Dashboard**:
   - React 19 + TypeScript + Vite with custom dark-mode glassmorphic theme.
   - Live Leaflet map with animated bus markers and incident markers.
   - Native HTML5 video player with HUD annotations.
   - Real-time WebSocket incident alert feed and inspector modal.
   - One-click **Municipal CSV Audit Log Exporter**.

---

## 📚 Datasets for Onboard AI Pipeline

Aligned with the official SIH26124 pipeline requirements:

### 1. Road Defects (Potholes, Waterlogging, Missing Signs)
- **Roboflow Pothole Dataset (Top Pick - Train-Ready)**: [public.roboflow.com/object-detection/pothole](https://public.roboflow.com/object-detection/pothole)
- **Kaggle Annotated Potholes Image Dataset**: [kaggle.com/datasets/andrewmvd/pothole-detection](https://kaggle.com/datasets/andrewmvd/pothole-detection)
- **India Driving Dataset (IDD)**: [idd.insaan.iiit.ac.in](https://idd.insaan.iiit.ac.in)

### 2. Vehicle Detection, Classification & Counting
- **Pretrained YOLOv8n (COCO - Active in Codebase)**: Runs at 32 FPS on CUDA RTX 4050.
- **India Driving Dataset (IDD)**: Indian vehicle mix (cars, buses, autos, 2-wheelers).
- **UA-DETRAC Traffic Surveillance**: [paperswithcode.com/dataset/ua-detrac](https://paperswithcode.com/dataset/ua-detrac)

### 3. Zebra Crossings, Traffic Signs & Signals
- **Roboflow Traffic-Kaggle-Detection**: [universe.roboflow.com/iasugda/traffic-kaggle-detection](https://universe.roboflow.com/iasugda/traffic-kaggle-detection)

### 4. Pedestrian / Kids-Crossing Safety
- **Caltech Pedestrian Dataset**: [data.caltech.edu/records/f6rph-90m20](https://data.caltech.edu/records/f6rph-90m20)
- **IDD Pedestrians**: Indian street conditions & roadside pedestrians.

### 5. Indian ANPR / License Plates
- **Kaggle Indian License Plates (YOLOv5/v8)**: [kaggle.com/datasets/thamizhsterio/indian-license-plates](https://kaggle.com/datasets/thamizhsterio/indian-license-plates)
- **Kaggle Indian License Plates with Labels**: [kaggle.com/datasets/kedarsai/indian-license-plates-with-labels](https://kaggle.com/datasets/kedarsai/indian-license-plates-with-labels)

> Detailed setup guide available in **[docs/DATASET_GUIDE_SIH26124.md](docs/DATASET_GUIDE_SIH26124.md)**.

---

## 🎬 Continuous Onboard Stream Stitcher

To demonstrate all 5 detection types running seamlessly off a single onboard camera feed:

```powershell
# 1. Synthesize a 5-in-1 multi-scenario road run (Potholes, Traffic, Swerving, Pedestrians, ANPR):
python scripts/stitch_demo_stream.py --synthetic --duration 15 --output sample_videos/demo_road_run.mp4

# 2. Or stitch external downloaded video clips:
python scripts/stitch_demo_stream.py --clips clip1_potholes.mp4 clip2_traffic.mp4 clip3_pedestrians.mp4 --output sample_videos/demo_road_run.mp4
```

---

## 🚀 How to Run & Test Live

Both the backend and frontend development servers are configured for zero-friction local development:

### Step 1: Start Backend
```powershell
cd "g:\major project"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- API Docs: `http://127.0.0.1:8000/docs`
- Health Probe: `http://127.0.0.1:8000/api/v1/health`

### Step 2: Start Frontend
```powershell
cd "g:\major project\frontend"
npm run dev -- --host 127.0.0.1 --port 5173
```
- Open browser: **`http://127.0.0.1:5173`**

### Step 3: Interactive Live Demonstration Walkthrough
1. **Model & GPU Status Banner**: Check the top banner confirming `NVIDIA GeForce RTX 4050 Laptop GPU` active with CUDA acceleration.
2. **Fleet Control Panel**: Click **Start Stream** on **BUS-001** to trigger continuous simulated telemetry along Delhi Route 101.
3. **Annotated Video Processing**: In the Annotated Video Player, select `demo_road_run.mp4` and click **Process Video**. Watch the neural pipeline process frames at ~32 FPS.
4. **Traffic Analytics Panel**: Observe dynamic traffic density (`LOW`, `MEDIUM`, `HIGH`) and category volume breakdown bars (Cars, Buses, Trucks, Motorcycles, Pedestrians).
5. **ANPR License Plate Inspector**: Scroll to the ANPR log to inspect high-security Indian plates (e.g. `DL01AB1234`) with confidence scores and `VERIFIED` status badges.
6. **Live Geospatial Map**: View animated bus markers along Delhi transit polylines and clicked incident markers with evidence thumbnails.
7. **Incident Feed & Review Queue**:
   - Hear audio alerts and view real-time WebSocket incident cards.
   - Filter by Bus, Severity, Review Status, or Event Type.
   - Click an incident to open the **Review Modal** and mark it `VERIFIED`, `RESOLVED`, or `FALSE_POSITIVE`.
   - Click **Export CSV** to download a complete municipal audit report for road maintenance authorities.

---

## 🧪 Automated Test Suite

Run the complete suite of 18 automated pytest unit and integration tests:
```powershell
pytest backend/tests -v
```
All 18 tests cover health endpoints, vertical video processing slice, isolated multi-bus tracking, vehicle counting, simulated GPS interpolation, safety rule assertions, ANPR regex validation, and WebSocket alerts.

---

## ⚖️ Ethical & Transparency Guardrails

1. **Simulated GPS**: All geographic coordinates are explicitly tagged as `is_simulated_gps: true` and labeled `SIMULATED GPS` on the map and video HUDs.
2. **Explainable Safety Alerts**: Safety incident candidates (`PROXIMITY_CONFLICT`, `RASH_DRIVING_CANDIDATE`) are surfaced as review candidates for municipal operators with explainable metrics (measured pixel distance, lateral displacement rate) and do not claim automated conviction.
3. **Review Flagging for OCR**: License plate readings with low confidence or irregular formatting are explicitly flagged as `NEEDS_REVIEW`.

---

## 📄 License
MIT License. Built for Smart India Hackathon (SIH26124).
