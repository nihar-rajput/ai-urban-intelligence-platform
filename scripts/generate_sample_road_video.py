import os
import cv2
import numpy as np


def generate_sample_road_video(
    output_path: str = "sample_videos/demo_road_run.mp4",
    duration_sec: int = 10,
    fps: int = 24,
    width: int = 1280,
    height: int = 720
):
    """
    Synthesize a realistic urban road drive video for computer vision testing.
    Includes perspective asphalt road, animated dashed lane markings, moving vehicles,
    and simulated road pothole depressions.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = duration_sec * fps

    # Road perspective parameters
    horizon_y = int(height * 0.45)
    road_top_left = (int(width * 0.42), horizon_y)
    road_top_right = (int(width * 0.58), horizon_y)
    road_bottom_left = (int(width * 0.05), height)
    road_bottom_right = (int(width * 0.95), height)

    road_pts = np.array([
        road_top_left,
        road_top_right,
        road_bottom_right,
        road_bottom_left
    ], np.int32)

    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # 1. Sky & Horizon
        frame[:horizon_y, :] = [45, 30, 20]  # Dark urban ambient sky

        # Distant city skyline buildings
        for bx in range(0, width, 80):
            b_height = 40 + (bx * 37) % 60
            cv2.rectangle(
                frame,
                (bx, horizon_y - b_height),
                (bx + 65, horizon_y),
                (35 + (bx % 20), 28, 22),
                -1
            )

        # 2. Road Asphalt
        cv2.fillPoly(frame, [road_pts], (42, 42, 44))

        # Road shoulders (sidewalks / curb)
        curb_left = np.array([(0, horizon_y), road_top_left, road_bottom_left, (0, height)], np.int32)
        curb_right = np.array([road_top_right, (width, horizon_y), (width, height), road_bottom_right], np.int32)
        cv2.fillPoly(frame, [curb_left], (30, 38, 30))
        cv2.fillPoly(frame, [curb_right], (30, 38, 30))

        # 3. Animated Dashed Lane Dividers (moving towards camera)
        lane_scroll = (frame_idx * 16) % 120
        center_top = ((road_top_left[0] + road_top_right[0]) // 2, horizon_y)
        center_bottom = ((road_bottom_left[0] + road_bottom_right[0]) // 2, height)

        for d in range(lane_scroll, height - horizon_y, 90):
            progress = d / (height - horizon_y)
            y_start = int(horizon_y + d)
            dash_len = int(25 + progress * 45)
            y_end = min(y_start + dash_len, height)

            x_center = int(center_top[0] + (center_bottom[0] - center_top[0]) * progress)
            thickness = int(3 + progress * 6)

            cv2.line(frame, (x_center, y_start), (x_center, y_end), (220, 220, 220), thickness)

        # 4. Simulated Potholes (Appears in lane at specific timestamps)
        # Pothole 1: between t=2.0s and t=5.0s
        if 2.0 <= t <= 5.0:
            p_prog = (t - 2.0) / 3.0  # Moves from horizon down towards viewer
            py = int(horizon_y + p_prog * (height - horizon_y - 80))
            px = int(width * 0.40 - p_prog * 80)
            prad_x = int(12 + p_prog * 36)
            prad_y = int(6 + p_prog * 18)

            # Outer rough crack edge
            cv2.ellipse(frame, (px, py), (prad_x + 4, prad_y + 3), 15, 0, 360, (20, 20, 20), -1)
            # Inner dark pothole depression
            cv2.ellipse(frame, (px, py), (prad_x, prad_y), 15, 0, 360, (10, 10, 12), -1)
            # Rough asphalt erosion texture
            cv2.ellipse(frame, (px - 4, py - 2), (prad_x // 2, prad_y // 2), 15, 0, 360, (5, 5, 5), -1)

        # Pothole 2: between t=6.5s and t=9.5s
        if 6.5 <= t <= 9.5:
            p2_prog = (t - 6.5) / 3.0
            py2 = int(horizon_y + p2_prog * (height - horizon_y - 60))
            px2 = int(width * 0.58 + p2_prog * 90)
            prad2_x = int(14 + p2_prog * 40)
            prad2_y = int(7 + p2_prog * 20)

            cv2.ellipse(frame, (px2, py2), (prad2_x + 5, prad2_y + 3), -10, 0, 360, (22, 22, 22), -1)
            cv2.ellipse(frame, (px2, py2), (prad2_x, prad2_y), -10, 0, 360, (12, 12, 14), -1)

        # 5. Simulated Vehicles in adjacent lane
        # Vehicle 1: Car approaching / passing in right lane
        v_prog = (frame_idx % (fps * 6)) / (fps * 6)
        vy = int(horizon_y + 30 + v_prog * (height - horizon_y - 140))
        vx = int(width * 0.56 + v_prog * 160)
        vw = int(45 + v_prog * 150)
        vh = int(30 + v_prog * 95)

        # Draw vehicle chassis
        cv2.rectangle(frame, (vx - vw // 2, vy), (vx + vw // 2, vy + vh), (180, 50, 40), -1)
        # Vehicle cabin / windshield
        cv2.rectangle(frame, (vx - vw // 3, vy + 4), (vx + vw // 3, vy + vh // 2), (70, 70, 80), -1)
        # Tail lights
        cv2.circle(frame, (vx - vw // 2 + 8, vy + vh - 10), int(3 + v_prog * 5), (0, 0, 220), -1)
        cv2.circle(frame, (vx + vw // 2 - 8, vy + vh - 10), int(3 + v_prog * 5), (0, 0, 220), -1)

        # 6. Simulated Bus Dashboard Overlay (bottom edges simulating bus windshield camera)
        cv2.putText(
            frame,
            f"SIMULATED BUS CAM [BUS-001] | T: {t:.2f}s | FRAME: {frame_idx:04d}",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 230, 255),
            2,
            cv2.LINE_AA
        )

        out.write(frame)

    out.release()
    print(f"Sample road video generated successfully: {output_path} ({total_frames} frames, {duration_sec}s)")


if __name__ == "__main__":
    generate_sample_road_video()
