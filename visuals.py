import os
import requests
import random

def get_visuals(topic, num_visuals=5):
    """
    Gathers visuals for the video. It tries Pexels first, then falls back to Pixabay.
    """
    print("Gathering visuals...")
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
                
                # Filter for high-resolution videos (HD 1080p portrait)
                high_res_videos = [f for f in video_files if f.get('height', 0) >= 1920 and f.get('width', 0) >= 1080]
                if not high_res_videos:
                    continue

                best_video = max(high_res_videos, key=lambda x: x.get('height', 0) * x.get('width', 0))
                video_url = best_video.get("link")

                if video_url:
                    print(f"Downloading video from Pexels: {video['id']}")
                    video_response = requests.get(video_url)
                    video_response.raise_for_status()
                    filename = f"visual_{len(visual_files)}.mp4"
                    with open(filename, "wb") as f:
                        f.write(video_response.content)
                    visual_files.append(filename)
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
                    
                    # Pixabay provides different sizes, 'large' is a good balance
                    video_url = video.get("videos", {}).get("large", {}).get("url")
                    if video_url:
                        print(f"Downloading video from Pixabay: {video['id']}")
                        video_response = requests.get(video_url)
                        video_response.raise_for_status()
                        filename = f"visual_{len(visual_files)}.mp4"
                        with open(filename, "wb") as f:
                            f.write(video_response.content)
                        visual_files.append(filename)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from Pixabay: {e}")

    print(f"Found {len(visual_files)} visuals.")
    return visual_files
