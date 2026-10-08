import os
import shutil
import argparse
import torch
from ultralytics import YOLO


def train_defect_detector(
    data_yaml: str = "datasets/data.yaml",
    epochs: int = 50,
    batch_size: int = 16,
    img_size: int = 640
):
    """
    Fine-tunes YOLOv8n on road defect annotations using RTX 4050 GPU acceleration.
    Saves final weights to models/road_defects_best.pt.
    """
    if not os.path.exists(data_yaml):
        print("=" * 70)
        print("[!] ERROR: Dataset config 'datasets/data.yaml' not found.")
        print("=" * 70)
        print("Please download and place your road defect dataset in 'datasets/':")
        print("Example recommended datasets:")
        print("1. Roboflow Universe - Pothole Detection (Export format: YOLOv8)")
        print("2. RDD2020 / RDD2022 (Road Damage Dataset) in YOLO format")
        print("\nOnce extracted, run:")
        print("  python scripts/audit_dataset.py --yaml datasets/data.yaml")
        print("  python scripts/train_road_defects.py --yaml datasets/data.yaml --epochs 30")
        return False

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Starting training on device: {device} (RTX 4050 GPU Accelerated: {torch.cuda.is_available()})")

    # Load base pretrained model
    base_model_path = "models/yolov8n.pt" if os.path.exists("models/yolov8n.pt") else "yolov8n.pt"
    model = YOLO(base_model_path)

    # Train
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        device=device,
        amp=True,  # Automatic Mixed Precision for 6GB VRAM efficiency
        project="models/runs",
        name="road_defects",
        exist_ok=True,
        verbose=True
    )

    # Copy best weights to models/road_defects_best.pt
    best_weights = os.path.join("models/runs", "road_defects", "weights", "best.pt")
    target_weights = "models/road_defects_best.pt"

    if os.path.exists(best_weights):
        shutil.copy(best_weights, target_weights)
        print(f"\n[SUCCESS] Fine-tuned model saved to: {target_weights}")
        print("The backend API will automatically load this model on next reload!")
    else:
        print("[!] Training completed, but best.pt could not be located.")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune YOLOv8 on Road Defects")
    parser.add_argument("--yaml", default="datasets/data.yaml", help="Path to data.yaml")
    parser.add_argument("--epochs", type=int, default=30, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (16 recommended for 6GB GPU)")
    args = parser.parse_args()

    train_defect_detector(
        data_yaml=args.yaml,
        epochs=args.epochs,
        batch_size=args.batch
    )
