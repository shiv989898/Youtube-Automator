import os
import requests
import random


def get_visuals(topic, num_visuals: int = 8, target_duration: int = 180):
    """Gather horizontal (16:9) 1080p-friendly visuals for long-form videos.

    Prefers landscape clips (width >= height) from Pexels/Pixabay and avoids
    the portrait settings used by shorts.
    Optimized to download only videos matching the target duration to save time and bandwidth.
    """
    per_clip_duration = target_duration // num_visuals if num_visuals > 0 else 30
    print(f"Gathering {num_visuals} horizontal visuals (~{per_clip_duration}s each, total ~{target_duration}s)...")
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

                # Check video duration to avoid downloading unnecessarily long videos
                video_duration = video.get('duration', 0)
                # Skip videos that are way too long (more than 2x per-clip duration + 20s buffer)
                max_acceptable = (per_clip_duration * 2) + 20
                if video_duration > max_acceptable:
                    continue
                
                # Skip videos that are too short (less than half the per-clip duration)
                min_acceptable = max(5, per_clip_duration // 2)
                if video_duration < min_acceptable:
                    continue

                video_files = video.get("video_files", [])
                if not video_files:
                    continue

                # Prefer landscape, 1080p (avoid 4K to save bandwidth)
                # Prioritize 1920x1080 over higher resolutions
                candidates = [
                    f
                    for f in video_files
                    if f.get("width", 0) >= f.get("height", 0)
                    and f.get("width", 0) >= 1280
                    and f.get("width", 0) <= 2560  # Avoid 4K
                ]
                if not candidates:
                    continue

                # Select video closest to 1080p (1920x1080)
                best = min(
                    candidates,
                    key=lambda x: abs(x.get("width", 0) - 1920) + abs(x.get("height", 0) - 1080),
                )
                video_url = best.get("link")
                if not video_url:
                    continue

                print(f"Downloading video {len(visual_files)+1}/{num_visuals} from Pexels: {video['id']} (~{video_duration}s, {best.get('width')}x{best.get('height')})")
                filename = f"long_visual_{len(visual_files)}.mp4"
                
                # Stream download with progress bar
                try:
                    with requests.get(video_url, stream=True, timeout=60) as video_response:
                        video_response.raise_for_status()
                        total_size = int(video_response.headers.get('content-length', 0))
                        downloaded = 0
                        
                        with open(filename, "wb") as f:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    if total_size > 0:
                                        progress = int((downloaded / total_size) * 100)
                                        bar_length = 30
                                        filled = int((progress / 100) * bar_length)
                                        bar = "█" * filled + "░" * (bar_length - filled)
                                        print(f"\r  [{bar}] {progress}% ({downloaded//(1024*1024):.1f}/{total_size//(1024*1024):.1f} MB)", end="", flush=True)
                        print()  # New line after download
                    visual_files.append(filename)
                except Exception as e:
                    print(f"\n  ❌ Download failed: {e}")
                    if os.path.exists(filename):
                        os.remove(filename)
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
                    
                    # Check duration to avoid downloading long videos
                    video_duration = video.get('duration', 0)
                    max_acceptable = (per_clip_duration * 2) + 20
                    min_acceptable = max(5, per_clip_duration // 2)
                    
                    if video_duration > max_acceptable or video_duration < min_acceptable:
                        continue

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
