# 📚 SIH26124 Dataset Audit & Ingestion Guide

> **Sponsor**: Bharat Electronics Limited (BEL)  
> **Problem Statement**: AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet (SIH26124)  
> **Hardware Target**: Windows 11 development laptop with NVIDIA RTX 4050 (6 GB VRAM) & 16 GB RAM.

---

## 🧭 Executive Summary: Dataset Evaluation & Strategy

To satisfy all requirements of SIH26124 on a single onboard simulated bus camera, your onboard pipeline requires 5 distinct vision capabilities:
1. **Road Defect Detection** (Potholes, surface cracks, depressions)
2. **Vehicle Detection, Multi-Object Tracking & Counting** (Cars, buses, trucks, 2-wheelers, auto-rickshaws)
3. **Zebra Crossings, Traffic Signs & Signals**
4. **Pedestrian / Kid-Crossing Proximity Safety**
5. **Indian ANPR / License Plate Recognition**

Rather than running 5 separate disconnected demonstrations, the winning strategy is **stitching clips into a continuous onboard bus feed** (`sample_videos/sih_onboard_continuous_feed.mp4`).

---

## 🔍 In-Depth Dataset Audit by Category

### 1. Road Defects (Potholes, Waterlogging, Hazards)

| Dataset | Format | Recommendation | Notes & Link |
| :--- | :--- | :--- | :--- |
| **Roboflow Pothole Dataset** | YOLOv8 / YOLOv5 (Ready-to-use) | ⭐⭐⭐⭐⭐ **Top Pick** | Pre-split (train/valid/test), balanced annotations, downloadable in 1 click as YOLO txt format. Download: [public.roboflow.com/object-detection/pothole](https://public.roboflow.com/object-detection/pothole) |
| **Kaggle AndrewMVD Pothole** | Pascal VOC XML / YOLO | ⭐⭐⭐⭐ Recommended | 665 annotated road images. Clean labels for potholes. Requires converting XML to YOLO via our audit script. Download: [kaggle.com/datasets/andrewmvd/pothole-detection](https://kaggle.com/datasets/andrewmvd/pothole-detection) |
| **India Driving Dataset (IDD)** | JSON / Polygonal Segmentation | ⭐⭐⭐ Comprehensive | Highly realistic for Indian unstructured roads. Requires user registration on portal and approval. Link: [idd.insaan.iiit.ac.in](https://idd.insaan.iiit.ac.in) |

**RTX 4050 Training Guidance**:
```powershell
# Place dataset in datasets/road_potholes/
python scripts/audit_dataset.py --data-dir datasets/road_potholes
python scripts/train_road_defects.py --data-yaml datasets/road_potholes/data.yaml --epochs 25 --batch 16
```

---

### 2. Vehicle Detection, Classification & Counting

| Dataset | Classes | Recommendation | Notes & Link |
| :--- | :--- | :--- | :--- |
| **Pretrained YOLOv8n (COCO)** | Car, Bus, Truck, Motorcycle, Bicycle | ⭐⭐⭐⭐⭐ **Immediate Use** | Already loaded in your project! Runs at 30+ FPS on CUDA RTX 4050 out of the box with zero training needed. |
| **India Driving Dataset (IDD)** | Autos, Two-wheelers, Buses, Pedestrians | ⭐⭐⭐⭐ Best Indian Mix | Unmatched representation of 3-wheelers (auto-rickshaws) and dense traffic conditions. Link: [idd.insaan.iiit.ac.in](https://idd.insaan.iiit.ac.in) |
| **UA-DETRAC** | Car, Bus, Van, Others | ⭐⭐⭐ Good Benchmark | 140,000 traffic surveillance frames. Great for highway flow benchmarking. Link: [paperswithcode.com/dataset/ua-detrac](https://paperswithcode.com/dataset/ua-detrac) |

---

### 3. Zebra Crossings, Traffic Signs & Signals

| Dataset | Classes | Recommendation | Notes & Link |
| :--- | :--- | :--- | :--- |
| **Roboflow Traffic-Kaggle-Detection** | Stop signs, traffic lights, crosswalks | ⭐⭐⭐⭐⭐ **Top Pick** | 100% YOLOv8 ready with crosswalk annotations. Can directly train a secondary head or merge classes. Link: [universe.roboflow.com/iasugda/traffic-kaggle-detection](https://universe.roboflow.com/iasugda/traffic-kaggle-detection) |

---

### 4. Pedestrian / Kid-Crossing Proximity Safety

| Dataset | Classes | Recommendation | Notes & Link |
| :--- | :--- | :--- | :--- |
| **Caltech Pedestrian Dataset** | Pedestrians, children, occluded people | ⭐⭐⭐⭐ High Quality | Benchmarks vehicle-pedestrian encounters and spatial distance. Link: [data.caltech.edu/records/f6rph-90m20](https://data.caltech.edu/records/f6rph-90m20) |
| **IDD Pedestrians** | Pedestrians on Indian roads | ⭐⭐⭐⭐⭐ Highly Contextual | Pedestrians walking near road edges without dedicated footpaths, typical in Indian urban transit. Link: [idd.insaan.iiit.ac.in](https://idd.insaan.iiit.ac.in) |

**Pipeline Integration**:
Our `SafetyAnalyticsEngine` uses ground-contact Euclidean pixel proximity ($d < 65\text{px}$) and lateral rate of change to tag **`PROXIMITY_CONFLICT`** and **`RASH_DRIVING_CANDIDATE`**.

---

### 5. ANPR / Indian License Plate Detection

| Dataset | Annotations | Recommendation | Notes & Link |
| :--- | :--- | :--- | :--- |
| **Kaggle Thamizhsterio Indian Plates** | YOLOv5 txt (Plates) | ⭐⭐⭐⭐⭐ **Top Pick** | Directly usable with YOLO object detector to isolate license plate bounding box, then passed to EasyOCR. Download: [kaggle.com/datasets/thamizhsterio/indian-license-plates](https://kaggle.com/datasets/thamizhsterio/indian-license-plates) |
| **Kaggle Kedarsai Indian Plates with Labels** | CSV / VOC XML | ⭐⭐⭐⭐ Good Reference | Clear high-resolution plates with ground truth text. Great for verifying OCR character accuracy. Download: [kaggle.com/datasets/kedarsai/indian-license-plates-with-labels](https://kaggle.com/datasets/kedarsai/indian-license-plates-with-labels) |

---

## 🎬 Live Hackathon Demo Strategy: The Continuous Onboard Stream

Instead of switching between disjointed video clips during your defense/presentation, stitch 2–3 sequences into a single continuous **1080p 30 FPS video** named `sample_videos/demo_road_run.mp4`:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CONTINUOUS BUS-001 ONBOARD CAMERA STREAM                        │
├─────────────────────┬─────────────────────┬─────────────────────┬──────────────────────┤
│    Segment 1 (0-8s) │   Segment 2 (8-16s) │  Segment 3 (16-24s) │   Segment 4 (24-32s) │
│   Road Defect Zone  │ Dense Mixed Traffic │  Pedestrian Crossing│   Vehicle Tailgate   │
│   • Potholes        │ • Cars, Buses       │ • Ground contact    │ • Rear plate crop    │
│   • Surface Cracks  │ • Tracking IDs      │ • Proximity Conflict│ • EasyOCR extraction │
│   • Evidence Crop   │ • Density: HIGH     │ • Safety Candidate  │ • VERIFIED Indian HSRP│
└─────────────────────┴─────────────────────┴─────────────────────┴──────────────────────┘
```

---

## 🛠️ Folder Layout for Downloaded Datasets

When you download your chosen zip files, extract them as follows:

```
g:\major project\datasets/
├── road_potholes/              # From Roboflow Pothole or Kaggle
│   ├── data.yaml
│   ├── train/images & labels
│   ├── valid/images & labels
├── indian_license_plates/      # From Kaggle Thamizhsterio
│   ├── data.yaml
│   ├── images/
│   └── labels/
└── raw_clips/                  # Video clips to stitch into onboard stream
    ├── clip_potholes.mp4
    ├── clip_traffic_dense.mp4
    └── clip_pedestrians.mp4
```

---

## 🚀 Quick Commands to Audit & Train

```powershell
# 1. Audit class distribution & box health
python scripts/audit_dataset.py --data-dir datasets/road_potholes

# 2. Fine-tune on RTX 4050 6GB with mixed-precision (FP16)
python scripts/train_road_defects.py --data-yaml datasets/road_potholes/data.yaml --epochs 30 --batch 16 --imgsz 640

# 3. Stitch demo clips into continuous onboard stream
python scripts/stitch_demo_stream.py --input-dir datasets/raw_clips --output sample_videos/sih_onboard_feed.mp4
```
