import os
import requests
import random

def get_visuals(topic, num_visuals=5, target_duration=20):
    """
    Gathers visuals for the video. It tries Pexels first, then falls back to Pixabay.
    Optimized to download only videos matching the target duration to save time.
    """
    print(f"Gathering {num_visuals} visuals for ~{target_duration}s duration...")
    visual_files = []

    # --- API Provider 1: Pexels ---
    pexels_api_key = os.getenv("PEXELS_API_KEY")
    if pexels_api_key:
        print("Trying Pexels for visuals...")
        headers = {"Authorization": pexels_api_key}
        params = {
            "query": topic, 
            "per_page": num_visuals * 2, # Fetch more to filter down
            "orientation": "portrait"
        }
        try:
            response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
            response.raise_for_status()
            pexels_data = response.json()
            
            videos = pexels_data.get("videos", [])
            random.shuffle(videos) # Randomize results to get variety

            for video in videos:
                if len(visual_files) >= num_visuals:
                    break

                video_files = video.get("video_files", [])
                if not video_files:
                    continue
                
                # Check video duration to avoid downloading long videos
                video_duration = video.get('duration', 0)
                if video_duration > target_duration + 10:  # Skip videos much longer than needed
                    continue
                
                # Filter for optimal portrait resolution (1080x1920 for YouTube Shorts)
                # Avoid 4K to save bandwidth, 1080p is perfect quality for Shorts
                portrait_videos = [f for f in video_files 
                                 if f.get('height', 0) >= 1920 
                                 and f.get('width', 0) >= 1080
                                 and f.get('height', 0) <= 2160]  # Max 2K, avoid 4K
                
                if not portrait_videos:
                    continue

                # Select optimal video (prefer 1080p over 4K for speed)
                best_video = min(portrait_videos, key=lambda x: abs(x.get('height', 0) - 1920))
                video_url = best_video.get("link")

                if video_url:
                    print(f"Downloading Pexels video {video['id']} (~{video_duration}s, {best_video.get('height')}x{best_video.get('width')})")
                    
                    # Stream download with chunks for faster processing
                    filename = f"visual_{len(visual_files)}.mp4"
                    try:
                        with requests.get(video_url, stream=True, timeout=30) as video_response:
                            video_response.raise_for_status()
                            total_size = int(video_response.headers.get('content-length', 0))
                            
                            with open(filename, "wb") as f:
                                downloaded = 0
                                for chunk in video_response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                                        downloaded += len(chunk)
                                        # Show progress for large files
                                        if total_size > 1024 * 1024:  # > 1MB
                                            progress = (downloaded / total_size) * 100
                                            print(f"\rProgress: {progress:.1f}%", end="")
                            
                            if total_size > 1024 * 1024:
                                print()  # New line after progress
                            
                        visual_files.append(filename)
                        print(f"[OK] Downloaded {total_size / (1024*1024):.1f} MB")
                    except requests.exceptions.RequestException as e:
                        print(f"\n[ERROR] Download failed: {e}")
                        if os.path.exists(filename):
                            os.remove(filename)
                        continue
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Pexels: {e}. Trying next provider.")
            
    # --- API Provider 2: Pixabay (Fallback) ---
    if len(visual_files) < num_visuals:
        pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        if pixabay_api_key:
            print("Pexels failed or had insufficient results. Trying Pixabay...")
            needed = num_visuals - len(visual_files)
            params = {
                "key": pixabay_api_key,
                "q": topic,
                "video_type": "film",
                "orientation": "vertical",
                "per_page": needed * 2,
                "safesearch": "true"
            }
            try:
                response = requests.get("https://pixabay.com/api/videos/", params=params)
                response.raise_for_status()
                pixabay_data = response.json()

                videos = pixabay_data.get("hits", [])
                random.shuffle(videos)

                for video in videos:
                    if len(visual_files) >= num_visuals:
                        break
                    
                    # Check duration to avoid long videos
                    video_duration = video.get('duration', 0)
                    if video_duration > target_duration + 10:
                        continue
                    
                    # Pixabay: use 'medium' for optimal balance (faster than 'large')
                    video_data = video.get("videos", {})
                    video_url = video_data.get("medium", {}).get("url") or video_data.get("large", {}).get("url")
                    
                    if video_url:
                        print(f"Downloading Pixabay video {video['id']} (~{video_duration}s)")
                        
                        # Stream download with chunks
                        filename = f"visual_{len(visual_files)}.mp4"
                        try:
                            with requests.get(video_url, stream=True, timeout=30) as video_response:
                                video_response.raise_for_status()
                                total_size = int(video_response.headers.get('content-length', 0))
                                
                                with open(filename, "wb") as f:
                                    downloaded = 0
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                            downloaded += len(chunk)
                                            if total_size > 1024 * 1024:
                                                progress = (downloaded / total_size) * 100
                                                print(f"\rProgress: {progress:.1f}%", end="")
                                
                                if total_size > 1024 * 1024:
                                    print()
                                
                            visual_files.append(filename)
                            print(f"[OK] Downloaded {total_size / (1024*1024):.1f} MB")
                        except requests.exceptions.RequestException as e:
                            print(f"\n[ERROR] Download failed: {e}")
                            if os.path.exists(filename):
                                os.remove(filename)
                            continue
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from Pixabay: {e}")

    print(f"Found {len(visual_files)} visuals.")
    return visual_files
