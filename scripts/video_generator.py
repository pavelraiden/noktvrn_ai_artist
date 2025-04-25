""" 
video_generator.py
Main module for building shortform video teasers based on artist profile and video plan.
"""

import json
import os
from pathlib import Path
from scripts.ffmpeg_controller import cut_video_segment, apply_effects, concatenate_segments
from tqdm import tqdm

# Constants
ARTIST_NAME = "noktvrn"
BASE_DIR = Path(__file__).resolve().parent.parent
ARTIST_DIR = BASE_DIR / "artists" / ARTIST_NAME
VIDEO_PLAN_PATH = ARTIST_DIR / "video" / "video_plan_noktvrn.json"
RAW_ASSETS_DIR = BASE_DIR / "assets" / "raw_sources"
TEASER_OUTPUT_DIR = ARTIST_DIR / "video" / "teaser_output"
RENDER_LOG_PATH = ARTIST_DIR / "video" / "render_log.json"

# Ensure output directory exists
TEASER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_video_plan():
    with open(VIDEO_PLAN_PATH, "r") as f:
        return json.load(f)

def find_video_clip(keywords):
    """Mock: find a local video matching one of the keywords."""
    for keyword in keywords:
        candidate_dir = RAW_ASSETS_DIR / keyword.replace(" ", "_").lower()
        if candidate_dir.exists() and any(candidate_dir.glob("*.mp4")):
            return list(candidate_dir.glob("*.mp4"))[0]  # Return first match
    return None

def build_teaser():
    plan = load_video_plan()
    segments = plan.get("segments", [])
    teaser_clips = []
    render_log = []

    print(f"Building teaser for artist: {plan.get('artist')} ({plan.get('genre')})")
    
    for segment in tqdm(segments, desc="Processing segments"):
        visuals = segment.get("visuals", [])
        effects = segment.get("effects", [])
        duration = segment.get("duration_sec", 3)
        label = segment.get("label", "SEGMENT")

        clip_path = find_video_clip(visuals)
        if clip_path:
            segment_output = TEASER_OUTPUT_DIR / f"{label.lower()}_segment.mp4"
            cut_video_segment(clip_path, segment_output, duration)
            apply_effects(segment_output, effects)
            teaser_clips.append(segment_output)
            render_log.append({
                "segment": label,
                "source": str(clip_path),
                "duration_sec": duration,
                "effects_applied": effects
            })
        else:
            print(f"⚠️ Warning: No source found for visuals {visuals}")

    final_teaser_path = TEASER_OUTPUT_DIR / "noktvrn_teaser_v1.mp4"
    concatenate_segments(teaser_clips, final_teaser_path)

    with open(RENDER_LOG_PATH, "w") as f:
        json.dump(render_log, f, indent=2)

    print(f"✅ Teaser built successfully: {final_teaser_path}")

if __name__ == "__main__":
    build_teaser()
