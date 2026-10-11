"""
SIH26124 - Automated Dataset Downloader & Staging Utility
Downloads and sets up recommended datasets for the Onboard AI Pipeline:
1. Pothole Road Defects (Kaggle: andrewmvd/pothole-detection)
2. Indian License Plates (Kaggle: thamizhsterio/indian-license-plates)
3. Traffic Signals & Crosswalks
4. Creates sample starter kits for immediate training

Usage:
  python scripts/download_datasets.py --help
  python scripts/download_datasets.py --all
"""

import os
import sys
import argparse
import zipfile
import shutil
import cv2
import numpy as np


DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets")


def ensure_dirs():
    os.makedirs(os.path.join(DATASETS_DIR, "road_potholes", "images", "train"), exist_ok=True)
    os.makedirs(os.path.join(DATASETS_DIR, "road_potholes", "images", "val"), exist_ok=True)
    os.makedirs(os.path.join(DATASETS_DIR, "road_potholes", "labels", "train"), exist_ok=True)
    os.makedirs(os.path.join(DATASETS_DIR, "road_potholes", "labels", "val"), exist_ok=True)

    os.makedirs(os.path.join(DATASETS_DIR, "indian_plates", "images"), exist_ok=True)
    os.makedirs(os.path.join(DATASETS_DIR, "indian_plates", "labels"), exist_ok=True)

    os.makedirs(os.path.join(DATASETS_DIR, "raw_clips"), exist_ok=True)


def create_starter_pothole_dataset():
    """Generates starter training samples and data.yaml for instant YOLOv8 verification."""
    pothole_dir = os.path.join(DATASETS_DIR, "road_potholes")
    data_yaml_path = os.path.join(pothole_dir, "data.yaml")
    norm_path = os.path.abspath(pothole_dir).replace('\\', '/')

    yaml_content = f"""path: {norm_path}
train: images/train
val: images/val

names:
  0: pothole
"""
    with open(data_yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    # Generate 10 synthetic sample training images & labels if folder is empty
    train_img_dir = os.path.join(pothole_dir, "images", "train")
    train_lbl_dir = os.path.join(pothole_dir, "labels", "train")
    val_img_dir = os.path.join(pothole_dir, "images", "val")
    val_lbl_dir = os.path.join(pothole_dir, "labels", "val")

    if len(os.listdir(train_img_dir)) == 0:
        print("[Dataset] Creating starter sample pothole training set for verification...")
        for i in range(12):
            img = np.full((640, 640, 3), (45, 48, 50), dtype=np.uint8)
            # Add synthetic road asphalt texture
            noise = np.random.randint(-15, 15, (640, 640, 3), dtype=np.int16)
            img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

            # Draw pothole depression
            cx, cy = np.random.randint(180, 460), np.random.randint(250, 520)
            rx, ry = np.random.randint(35, 75), np.random.randint(20, 45)
            cv2.ellipse(img, (cx, cy), (rx, ry), np.random.randint(-10, 10), 0, 360, (20, 20, 20), -1)
            cv2.ellipse(img, (cx, cy), (rx + 4, ry + 2), 0, 0, 360, (32, 35, 38), 2)

            # YOLO bounding box: <class_id> <cx> <cy> <w> <h> (normalized)
            norm_cx = round(cx / 640.0, 5)
            norm_cy = round(cy / 640.0, 5)
            norm_w = round((rx * 2 + 8) / 640.0, 5)
            norm_h = round((ry * 2 + 6) / 640.0, 5)
            label_text = f"0 {norm_cx} {norm_cy} {norm_w} {norm_h}\n"

            target_img_dir = val_img_dir if i >= 10 else train_img_dir
            target_lbl_dir = val_lbl_dir if i >= 10 else train_lbl_dir

            fname = f"sample_pothole_{i+1:03d}"
            cv2.imwrite(os.path.join(target_img_dir, f"{fname}.jpg"), img)
            with open(os.path.join(target_lbl_dir, f"{fname}.txt"), "w", encoding="utf-8") as lf:
                lf.write(label_text)

        print("[Dataset] Starter pothole dataset created in: datasets/road_potholes/")


def download_from_kaggle(dataset_slug: str, target_dir: str):
    """Attempts to download dataset via official Kaggle Python API."""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        print(f"[Kaggle] Authenticated. Downloading {dataset_slug} to {target_dir}...")
        os.makedirs(target_dir, exist_ok=True)
        api.dataset_download_files(dataset_slug, path=target_dir, unzip=True)
        print(f"[Kaggle] Download complete: {dataset_slug}")
        return True
    except (Exception, SystemExit) as e:
        print(f"[Kaggle Notice] Automated API download requires kaggle credentials.")
        print(f"  -> Manual 1-click download: https://www.kaggle.com/datasets/{dataset_slug}")
        print(f"  -> Or run: kaggle auth login")
        return False


def main():
    parser = argparse.ArgumentParser(description="SIH26124 Dataset Downloader")
    parser.add_argument("--all", action="store_true", help="Prepare directories and download datasets")
    parser.add_argument("--kaggle-potholes", action="store_true", help="Download Kaggle andrewmvd/pothole-detection")
    parser.add_argument("--kaggle-plates", action="store_true", help="Download Kaggle thamizhsterio/indian-license-plates")

    args = parser.parse_args()

    ensure_dirs()
    create_starter_pothole_dataset()

    if args.kaggle_potholes or args.all:
        download_from_kaggle("andrewmvd/pothole-detection", os.path.join(DATASETS_DIR, "road_potholes"))

    if args.kaggle_plates or args.all:
        download_from_kaggle("thamizhsterio/indian-license-plates", os.path.join(DATASETS_DIR, "indian_plates"))

    print("\n[Done] Datasets structure ready. Run 'python scripts/audit_dataset.py --data-dir datasets/road_potholes' to verify.")


if __name__ == "__main__":
    main()
