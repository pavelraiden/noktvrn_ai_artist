"""
ffmpeg_controller.py
Helper module for ffmpeg-based video editing operations.
"""

import subprocess
from pathlib import Path


def cut_video_segment(input_path: Path, output_path: Path, duration: float):
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-t",
        str(duration),
        "-c",
        "copy",
        str(output_path),
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def apply_effects(input_output_path: Path, effects: list):
    if not effects:
        return
    temp_path = input_output_path.with_suffix(".temp.mp4")
    filters = []

    if "CRT overlay" in effects:
        filters.append("noise=alls=20:allf=t+u")
    if "glitch" in effects:
        filters.append("format=yuv420p,geq='r=X/W*255:g=Y/H*255:b=(X+Y)/2'")
    if "shake" in effects:
        filters.append("vibrance=3")

    filter_str = ",".join(filters)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_output_path),
        "-vf",
        filter_str,
        str(temp_path),
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    temp_path.rename(input_output_path)


def concatenate_segments(segment_paths: list, output_path: Path):
    list_file = output_path.with_suffix(".txt")
    with open(list_file, "w") as f:
        for seg in segment_paths:
            f.write(f"file '{str(seg.resolve())}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(output_path),
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    list_file.unlink()
