import os
import requests
from bing_image_creator_api import api as bing_api

def get_visuals(topic, num_visuals=5):
    """
    Gathers visuals for the video from Pexels and Bing Image Creator.
    """
    visual_files = []
    
    # 1. Get videos from Pexels
    pexels_api_key = os.getenv("PEXELS_API_KEY")
    if pexels_api_key:
        headers = {"Authorization": pexels_api_key}
        # Query for high-resolution, vertical videos
        params = {
            "query": topic, 
            "per_page": num_visuals, 
            "orientation": "portrait",
            "size": "large" # Request large video files
        }
        try:
            response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
            response.raise_for_status()
            pexels_data = response.json()
            
            for i, video in enumerate(pexels_data.get("videos", [])):
                # Select the highest quality video link available
                video_files = video.get("video_files", [])
                if not video_files:
                    continue
                
                # Find the link for the highest resolution
                best_video = max(video_files, key=lambda x: x.get('height', 0) * x.get('width', 0))
                video_url = best_video.get("link")

                if video_url:
                    video_response = requests.get(video_url)
                    video_response.raise_for_status()
                    filename = f"visual_{i}.mp4"
                    with open(filename, "wb") as f:
                        f.write(video_response.content)
                    visual_files.append(filename)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Pexels: {e}")
            
    # 2. Get images from Bing Image Creator (if needed)
    bing_auth_cookie = os.getenv("BING_AUTH_COOKIE")
    if bing_auth_cookie and len(visual_files) < num_visuals:
        try:
            image_gen = bing_api.ImageGen(bing_auth_cookie)
            image_urls = image_gen.get_images(f"{topic}, digital art")
            for i, url in enumerate(image_urls):
                if len(visual_files) >= num_visuals:
                    break
                image_response = requests.get(url)
                image_response.raise_for_status()
                filename = f"visual_{len(visual_files)}.jpg"
                with open(filename, "wb") as f:
                    f.write(image_response.content)
                visual_files.append(filename)
        except Exception as e:
            print(f"Non-blocking error fetching from Bing: {e}")

    return visual_files
