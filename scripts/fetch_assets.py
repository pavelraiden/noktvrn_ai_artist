import os
import json
import requests
from pathlib import Path
from tqdm import tqdm

PIXABAY_API_KEY = os.getenv("PIXABAY_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_KEY")

ASSETS_DIR = Path("assets/raw_sources/")

def fetch_pixabay(keyword, limit=1):
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={keyword}&per_page={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        hits = response.json().get("hits", [])
        if hits:
            return hits[0]["videos"]["medium"]["url"]
    except Exception as e:
        print(f"Pixabay error for {keyword}: {e}")
    return None

def fetch_pexels(keyword, limit=1):
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page={limit}"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        videos = response.json().get("videos", [])
        if videos:
            return videos[0]["video_files"][0]["link"]
    except Exception as e:
        print(f"Pexels error for {keyword}: {e}")
    return None

def fallback_mixkit(keyword):
    # Static fallback link from MixKit
    fallback_videos = {
        "drift cars": "https://assets.mixkit.co/videos/preview/mixkit-drifting-sports-car-4317-large.mp4",
        "neon city": "https://assets.mixkit.co/videos/preview/mixkit-city-billboards-at-night-2432-large.mp4",
        "models": "https://assets.mixkit.co/videos/preview/mixkit-fashion-model-posing-on-the-street-4225-large.mp4",
    }
    return fallback_videos.get(keyword.lower(), None)

def download_video(url, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True)
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def load_video_plan(plan_path):
    with open(plan_path) as f:
        return json.load(f)

def main(artist="noktvrn"):
    plan_path = Path(f"artists/{artist}/video/video_plan_{artist}.json")
    plan = load_video_plan(plan_path)
    fetched = {}

    for segment in tqdm(plan.get("segments", []), desc="Fetching assets"):
        for visual in segment.get("visuals", []):
            keyword = visual.replace("_", " ")
            folder = ASSETS_DIR / keyword.replace(" ", "_").lower()
            if any(folder.glob("*.mp4")):
                continue  # already exists

            url = fetch_pixabay(keyword) or fetch_pexels(keyword) or fallback_mixkit(keyword)
            if url:
                filename = keyword.replace(" ", "_").lower() + ".mp4"
                output_path = folder / filename
                try:
                    download_video(url, output_path)
                    fetched[visual] = str(output_path)
                except Exception as e:
                    fetched[visual] = f"Download error: {e}"
            else:
                fetched[visual] = "No asset found."

    with open("fetch_log.json", "w") as f:
        json.dump(fetched, f, indent=2)

    print("✅ Fetch complete. Log saved to fetch_log.json.")

if __name__ == "__main__":
    main()
