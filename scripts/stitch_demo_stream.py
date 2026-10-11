"""
SIH26124 - Continuous Onboard Stream Stitcher & Multi-Scenario Video Synthesizer
Stitches individual video clips from the SIH datasets (potholes, dense traffic, pedestrians, ANPR)
into a single continuous bus-mounted camera feed for an end-to-end hackathon demonstration.

Usage:
  # Synthesize a multi-scenario 5-in-1 demo stream without external files:
  python scripts/stitch_demo_stream.py --synthetic --output sample_videos/demo_road_run.mp4

  # Stitch user-downloaded clips:
  python scripts/stitch_demo_stream.py --clips path1.mp4 path2.mp4 path3.mp4 --output sample_videos/demo_road_run.mp4
"""

import os
import sys
import argparse
import math
import cv2
import numpy as np


def create_synthetic_multitask_stream(output_path: str, duration_sec: int = 15, fps: int = 24, width: int = 1280, height: int = 720):
    """
    Synthesizes a continuous onboard bus feed traversing 5 distinct scenarios:
    1. Road Defect Zone (Potholes on road surface)
    2. Dense Multimodal Traffic (Cars, buses, motorbikes with tracking continuity)
    3. Lateral Swerving Candidate (Rash driving trajectory pattern)
    4. Pedestrian Crossing Zone (Proximity conflict candidate)
    5. Tailgate Zone with clear Indian License Plate for ANPR (DL 01 AB 1234)
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, float(fps), (width, height))

    total_frames = duration_sec * fps
    print(f"[Synthesizer] Generating {total_frames} frames ({duration_sec}s) at {width}x{height} @ {fps}fps...")

    # Road perspective parameters
    horizon_y = int(height * 0.45)
    road_top_w = int(width * 0.20)
    road_bot_w = int(width * 0.95)

    road_tl = ((width - road_top_w) // 2, horizon_y)
    road_tr = ((width + road_top_w) // 2, horizon_y)
    road_br = ((width + road_bot_w) // 2, height)
    road_bl = ((width - road_bot_w) // 2, height)
    road_pts = np.array([road_tl, road_tr, road_br, road_bl], dtype=np.int32)

    for f in range(total_frames):
        t = f / float(fps)
        progress = f / float(total_frames)

        # 1. Base Environment
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Gradient Sky
        for y in range(horizon_y):
            blend = y / float(horizon_y)
            frame[y, :] = [int(180 - blend * 60), int(120 - blend * 40), int(70 + blend * 50)]
        # Grassy roadside
        frame[horizon_y:, :] = (45, 65, 40)
        # Dark Asphalt Road
        cv2.fillPoly(frame, [road_pts], (42, 45, 48))

        # Lane markings (moving downward to simulate forward bus motion)
        speed_factor = (f * 12) % 120
        for marker_y in range(horizon_y + 10, height, 80):
            cur_y = marker_y + speed_factor
            if cur_y >= height:
                continue
            scale = (cur_y - horizon_y) / float(height - horizon_y)
            lw = max(2, int(10 * scale))
            lh = max(6, int(30 * scale))
            cx = width // 2
            cv2.rectangle(frame, (cx - lw // 2, cur_y), (cx + lw // 2, min(height, cur_y + lh)), (230, 230, 230), -1)

        # -------------------------------------------------------------
        # SCENARIO 1: Pothole & Road Surface Defect (Frames 0 to 120, ~0-5s)
        # -------------------------------------------------------------
        if f < 140:
            pot_scale = 0.4 + 0.6 * (f / 140.0)
            pot_cx = int(width * 0.42 - f * 0.3)
            pot_cy = int(horizon_y + (height - horizon_y) * (0.3 + 0.6 * (f / 140.0)))
            pot_w = int(70 * pot_scale)
            pot_h = int(24 * pot_scale)
            if horizon_y < pot_cy < height - 10:
                cv2.ellipse(frame, (pot_cx, pot_cy), (pot_w, pot_h), 5, 0, 360, (18, 18, 18), -1)
                cv2.ellipse(frame, (pot_cx, pot_cy), (pot_w + 3, pot_h + 2), 5, 0, 360, (28, 30, 32), 2)

        # -------------------------------------------------------------
        # SCENARIO 2: Dense Multi-Vehicle Flow (Cars & Trucks) (Frames 60 to 240)
        # -------------------------------------------------------------
        if 50 <= f < 260:
            v_t = (f - 50) / 200.0
            # Car 1 in left lane moving forward
            c1_x = int(width * 0.35 - v_t * 80)
            c1_y = int(horizon_y + (height - horizon_y) * (0.25 + v_t * 0.65))
            c1_w = int(90 + v_t * 110)
            c1_h = int(55 + v_t * 75)
            if c1_y + c1_h < height:
                # Car body (Cyan/Blue)
                cv2.rectangle(frame, (c1_x, c1_y), (c1_x + c1_w, c1_y + c1_h), (160, 90, 30), -1)
                cv2.rectangle(frame, (c1_x, c1_y), (c1_x + c1_w, c1_y + c1_h), (220, 180, 50), 2)
                # Wheels
                cv2.rectangle(frame, (c1_x + 8, c1_y + c1_h - 10), (c1_x + 24, c1_y + c1_h + 4), (10, 10, 10), -1)
                cv2.rectangle(frame, (c1_x + c1_w - 24, c1_y + c1_h - 10), (c1_x + c1_w - 8, c1_y + c1_h + 4), (10, 10, 10), -1)

        # -------------------------------------------------------------
        # SCENARIO 3: Lateral Swerving Vehicle (Rash Driving) (Frames 120 to 260)
        # -------------------------------------------------------------
        if 110 <= f < 270:
            sw_phase = (f - 110) * 0.18
            # High lateral oscillation dx/dt
            sw_x = int(width * 0.62 + math.sin(sw_phase) * 55)
            sw_y = int(horizon_y + (height - horizon_y) * (0.3 + ((f - 110) / 160.0) * 0.55))
            sw_w = int(75 + ((f - 110) / 160.0) * 80)
            sw_h = int(50 + ((f - 110) / 160.0) * 50)
            if sw_y + sw_h < height:
                # Orange Car
                cv2.rectangle(frame, (sw_x, sw_y), (sw_x + sw_w, sw_y + sw_h), (25, 120, 220), -1)
                cv2.rectangle(frame, (sw_x, sw_y), (sw_x + sw_w, sw_y + sw_h), (40, 160, 255), 2)

        # -------------------------------------------------------------
        # SCENARIO 4: Pedestrian Crossing Zone (Frames 180 to 320)
        # -------------------------------------------------------------
        if 170 <= f < 310:
            ped_t = (f - 170) / 140.0
            # Pedestrian walking across right shoulder
            ped_x = int(width * 0.85 - ped_t * 140)
            ped_y = int(horizon_y + (height - horizon_y) * (0.45 + ped_t * 0.4))
            ped_w = int(22 + ped_t * 18)
            ped_h = int(60 + ped_t * 45)
            if ped_y + ped_h < height:
                # Head
                cv2.circle(frame, (ped_x + ped_w // 2, ped_y + 12), int(8 + ped_t * 3), (200, 180, 160), -1)
                # Torso
                cv2.rectangle(frame, (ped_x + 3, ped_y + 20), (ped_x + ped_w - 3, ped_y + ped_h - 22), (210, 50, 50), -1)
                # Legs
                cv2.line(frame, (ped_x + 6, ped_y + ped_h - 22), (ped_x + 4, ped_y + ped_h), (40, 40, 40), 3)
                cv2.line(frame, (ped_x + ped_w - 6, ped_y + ped_h - 22), (ped_x + ped_w - 4, ped_y + ped_h), (40, 40, 40), 3)

        # -------------------------------------------------------------
        # SCENARIO 5: Leading Vehicle with Indian License Plate (ANPR) (Frames 200+)
        # -------------------------------------------------------------
        if f >= 200:
            anpr_t = (f - 200) / float(total_frames - 200)
            plate_lead_x = int(width * 0.44)
            plate_lead_y = int(height * 0.52 + anpr_t * 60)
            lead_w = int(180 + anpr_t * 60)
            lead_h = int(120 + anpr_t * 40)

            # Lead car rear
            cv2.rectangle(frame, (plate_lead_x, plate_lead_y), (plate_lead_x + lead_w, plate_lead_y + lead_h), (30, 80, 180), -1)
            cv2.rectangle(frame, (plate_lead_x, plate_lead_y), (plate_lead_x + lead_w, plate_lead_y + lead_h), (255, 255, 255), 2)
            # Rear window
            cv2.rectangle(frame, (plate_lead_x + 20, plate_lead_y + 10), (plate_lead_x + lead_w - 20, plate_lead_y + 45), (10, 20, 30), -1)
            # Tail lights
            cv2.rectangle(frame, (plate_lead_x + 8, plate_lead_y + 55), (plate_lead_x + 28, plate_lead_y + 75), (0, 0, 240), -1)
            cv2.rectangle(frame, (plate_lead_x + lead_w - 28, plate_lead_y + 55), (plate_lead_x + lead_w - 8, plate_lead_y + 75), (0, 0, 240), -1)

            # High-Security Indian License Plate (HSRP)
            pw = int(lead_w * 0.48)
            ph = int(lead_h * 0.22)
            px = plate_lead_x + (lead_w - pw) // 2
            py = plate_lead_y + int(lead_h * 0.65)

            # White plate background with black border
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), (255, 255, 255), -1)
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), (10, 10, 10), 2)
            # Blue IND stripe on left
            ind_w = max(6, int(pw * 0.14))
            cv2.rectangle(frame, (px, py), (px + ind_w, py + ph), (180, 70, 20), -1)

            # Monospace Plate text: DL01AB1234
            plate_text = "DL01AB1234"
            font_scale = max(0.35, pw / 220.0)
            cv2.putText(
                frame,
                plate_text,
                (px + ind_w + 4, py + int(ph * 0.72)),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (10, 10, 10),
                2,
                cv2.LINE_AA
            )

        writer.write(frame)

    writer.release()
    print(f"[Synthesizer] Multi-scenario continuous feed saved successfully to: {output_path}")


def stitch_video_clips(clip_paths: list, output_path: str, target_width: int = 1280, target_height: int = 720, target_fps: float = 24.0):
    """Stitches multiple video files into a uniform resolution & FPS video."""
    valid_clips = [c for c in clip_paths if os.path.exists(c)]
    if not valid_clips:
        raise FileNotFoundError(f"None of the provided clips exist: {clip_paths}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, target_fps, (target_width, target_height))

    total_frames_written = 0
    print(f"[Stitcher] Stitching {len(valid_clips)} clips into: {output_path}")

    for idx, clip_path in enumerate(valid_clips):
        cap = cv2.VideoCapture(clip_path)
        clip_frames = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Resize frame to standard output dimensions
            resized = cv2.resize(frame, (target_width, target_height))
            writer.write(resized)
            clip_frames += 1
            total_frames_written += 1
        cap.release()
        print(f"  -> Added Clip {idx+1}/{len(valid_clips)}: {os.path.basename(clip_path)} ({clip_frames} frames)")

    writer.release()
    print(f"[Stitcher] Complete! Stitched {total_frames_written} frames into {output_path}")


def main():
    parser = argparse.ArgumentParser(description="SIH26124 Continuous Onboard Stream Stitcher & Synthesizer")
    parser.add_argument("--clips", nargs="+", help="Paths to individual MP4/AVI clips to stitch together")
    parser.add_argument("--synthetic", action="store_true", help="Generate a complete 5-in-1 multi-scenario synthetic road run")
    parser.add_argument("--output", default="sample_videos/demo_road_run.mp4", help="Output path for continuous video")
    parser.add_argument("--duration", type=int, default=15, help="Duration in seconds if generating synthetic stream")

    args = parser.parse_args()

    if args.clips:
        stitch_video_clips(args.clips, args.output)
    else:
        # Default or synthetic flag
        create_synthetic_multitask_stream(args.output, duration_sec=args.duration)


if __name__ == "__main__":
    main()
