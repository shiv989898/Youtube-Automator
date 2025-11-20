import os
import requests
import random


def get_visuals(topic, num_visuals: int = 8):
    """Gather horizontal (16:9) 1080p-friendly visuals for long-form videos.

    Prefers landscape clips (width >= height) from Pexels/Pixabay and avoids
    the portrait settings used by shorts.
    """
    print("Gathering horizontal visuals for long-form video...")
    visual_files = []

    # --- API Provider 1: Pexels (landscape) ---
    pexels_api_key = os.getenv("PEXELS_API_KEY")
    if pexels_api_key:
        print("Trying Pexels (landscape) for visuals...")
        headers = {"Authorization": pexels_api_key}
        params = {
            "query": topic,
            "per_page": num_visuals * 3,
            "orientation": "landscape",  # key change vs shorts
        }
        try:
            response = requests.get(
                "https://api.pexels.com/videos/search",
                headers=headers,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            pexels_data = response.json()

            videos = pexels_data.get("videos", [])
            random.shuffle(videos)

            for video in videos:
                if len(visual_files) >= num_visuals:
                    break

                video_files = video.get("video_files", [])
                if not video_files:
                    continue

                # Prefer landscape, at least 1080px wide when possible
                candidates = [
                    f
                    for f in video_files
                    if f.get("width", 0) >= f.get("height", 0)
                    and f.get("width", 0) >= 1280
                ]
                if not candidates:
                    continue

                best = max(
                    candidates,
                    key=lambda x: x.get("width", 0) * x.get("height", 0),
                )
                video_url = best.get("link")
                if not video_url:
                    continue

                print(f"Downloading horizontal video from Pexels: {video['id']}")
                video_response = requests.get(video_url, timeout=60)
                video_response.raise_for_status()
                filename = f"long_visual_{len(visual_files)}.mp4"
                with open(filename, "wb") as f:
                    f.write(video_response.content)
                visual_files.append(filename)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Pexels (landscape): {e}. Trying next provider.")

    # --- API Provider 2: Pixabay (landscape fallback) ---
    if len(visual_files) < num_visuals:
        pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        if pixabay_api_key:
            print("Pexels had insufficient landscape results. Trying Pixabay...")
            needed = num_visuals - len(visual_files)
            params = {
                "key": pixabay_api_key,
                "q": topic,
                "video_type": "film",
                "orientation": "horizontal",  # horizontal instead of vertical
                "per_page": needed * 3,
                "safesearch": "true",
            }
            try:
                response = requests.get(
                    "https://pixabay.com/api/videos/", params=params, timeout=30
                )
                response.raise_for_status()
                pixabay_data = response.json()

                videos = pixabay_data.get("hits", [])
                random.shuffle(videos)

                for video in videos:
                    if len(visual_files) >= num_visuals:
                        break

                    video_url = (
                        video.get("videos", {})
                        .get("large", {})
                        .get("url")
                    )
                    if not video_url:
                        continue

                    print(f"Downloading horizontal video from Pixabay: {video['id']}")
                    video_response = requests.get(video_url, timeout=60)
                    video_response.raise_for_status()
                    filename = f"long_visual_{len(visual_files)}.mp4"
                    with open(filename, "wb") as f:
                        f.write(video_response.content)
                    visual_files.append(filename)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from Pixabay (horizontal): {e}")

    print(f"Found {len(visual_files)} horizontal visuals.")
    return visual_files
