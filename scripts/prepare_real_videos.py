"""
SIH26124 - Real-World Video Ingestion & Preparation Utility
Transcodes real-world road and traffic footage into web-native H.264 MP4s
and places them into sample_videos/ for immediate dashboard testing.
"""

import os
import subprocess
import imageio_ffmpeg


RAW_DIR = os.path.join("datasets", "raw_clips")
SAMPLE_DIR = "sample_videos"
os.makedirs(SAMPLE_DIR, exist_ok=True)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def transcode(in_path: str, out_path: str, duration_sec: int = None, target_w: int = 1280, target_h: int = 720):
    if not os.path.exists(in_path):
        print(f"[Skip] Missing: {in_path}")
        return

    cmd = [
        FFMPEG, "-y",
        "-i", in_path,
    ]
    if duration_sec:
        cmd += ["-t", str(duration_sec)]

    cmd += [
        "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "23",
        out_path
    ]

    print(f"[Transcoding] {os.path.basename(in_path)} -> {out_path}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        sz_mb = round(os.path.getsize(out_path) / (1024 * 1024), 2)
        print(f"[Success] Generated: {out_path} ({sz_mb} MB)")
    else:
        print(f"[Error] Failed: {res.stderr[:200]}")


def main():
    # 1. Real Indian State Highway Dashcam (Sambalpur - Rourkela Highway, India)
    indian_highway_raw = [f for f in os.listdir(RAW_DIR) if "Sambalpur" in f or "SH_" in f]
    if indian_highway_raw:
        raw_clip = os.path.join(RAW_DIR, indian_highway_raw[0])
        transcode(raw_clip, os.path.join(SAMPLE_DIR, "indian_highway_dashcam.mp4"), duration_sec=25)

    # 2. Real Urban Multimodal Traffic (Cars, autos, buses, pedestrians)
    dhaka_clip = os.path.join(RAW_DIR, "dhaka_traffic.mp4")
    if os.path.exists(dhaka_clip):
        transcode(dhaka_clip, os.path.join(SAMPLE_DIR, "urban_multimodal_traffic.mp4"), duration_sec=20)

    # 3. Real Intersection Flow
    inter_clip = os.path.join(RAW_DIR, "traffic_detection.mp4")
    if os.path.exists(inter_clip):
        transcode(inter_clip, os.path.join(SAMPLE_DIR, "intersection_flow.mp4"), duration_sec=20)

    # 4. Quick Road Traffic Test
    quick_clip = os.path.join(RAW_DIR, "road_trafifc.mp4")
    if os.path.exists(quick_clip):
        transcode(quick_clip, os.path.join(SAMPLE_DIR, "quick_traffic_test.mp4"))

    print("\n[Done] All real-world test videos staged in sample_videos/.")


if __name__ == "__main__":
    main()
