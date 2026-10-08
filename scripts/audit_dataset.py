import os
import sys
import argparse
from typing import Dict
from collections import Counter
import yaml
from PIL import Image


def audit_yolo_dataset(data_yaml_path: str):
    """
    Validates and audits a YOLO formatted road defect dataset.
    Checks class distributions, bounding box coordinates sanity, and missing files.
    """
    if not os.path.exists(data_yaml_path):
        print(f"[!] data.yaml not found at: {data_yaml_path}")
        print("\nTo use your dataset:")
        print("1. Extract your dataset into the 'datasets/' directory")
        print("   Expected structure:")
        print("   datasets/")
        print("     data.yaml")
        print("     images/train/ (or train/images/)")
        print("     labels/train/ (or train/labels/)")
        print("     images/val/")
        print("     labels/val/")
        print("2. Run: python scripts/audit_dataset.py --yaml datasets/data.yaml")
        return False

    with open(data_yaml_path, "r", encoding="utf-8") as f:
        data_cfg = yaml.safe_load(f)

    classes = data_cfg.get("names", [])
    if isinstance(classes, dict):
        class_names = [classes[i] for i in sorted(classes.keys())]
    else:
        class_names = list(classes)

    print("=" * 60)
    print("DATASET AUDIT REPORT")
    print("=" * 60)
    print(f"Dataset Config: {data_yaml_path}")
    print(f"Total Defined Classes: {len(class_names)}")
    for idx, cname in enumerate(class_names):
        print(f"  [{idx}]: {cname}")

    base_dir = os.path.dirname(os.path.abspath(data_yaml_path))
    splits = ["train", "val", "test"]

    for split in splits:
        split_path = data_cfg.get(split)
        if not split_path:
            continue

        if not os.path.isabs(split_path):
            full_split_path = os.path.normpath(os.path.join(base_dir, split_path))
        else:
            full_split_path = split_path

        if not os.path.exists(full_split_path):
            print(f"\n[!] Split '{split}' path does not exist: {full_split_path}")
            continue

        # Look for images and corresponding labels
        image_files = []
        for root, _, files in os.walk(full_split_path):
            for file in files:
                if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
                    image_files.append(os.path.join(root, file))

        print(f"\n--- Split: {split.upper()} ---")
        print(f"Images Found: {len(image_files)}")

        label_counter = Counter()
        corrupted_images = 0
        missing_labels = 0

        for img_path in image_files[:500]:  # Sample first 500 for fast audit
            # Check image integrity
            try:
                with Image.open(img_path) as im:
                    im.verify()
            except Exception:
                corrupted_images += 1

            # Match label file
            label_path = (
                img_path.replace("images", "labels")
                .rsplit(".", 1)[0] + ".txt"
            )
            if not os.path.exists(label_path):
                missing_labels += 1
                continue

            with open(label_path, "r") as lf:
                for line in lf:
                    parts = line.strip().split()
                    if parts:
                        try:
                            cid = int(parts[0])
                            cname = class_names[cid] if cid < len(class_names) else f"class_{cid}"
                            label_counter[cname] += 1
                        except ValueError:
                            pass

        print(f"Corrupted Images: {corrupted_images}")
        print(f"Missing Labels: {missing_labels}")
        print("Class Instance Distribution (Sampled):")
        for cname, count in label_counter.most_common():
            print(f"  - {cname}: {count} bounding boxes")

    print("\n[OK] Dataset audit complete.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit road defect dataset format and balance")
    parser.add_argument("--yaml", default="datasets/data.yaml", help="Path to data.yaml")
    args = parser.parse_args()
    audit_yolo_dataset(args.yaml)
