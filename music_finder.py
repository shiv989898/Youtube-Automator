import os
import requests

def find_and_download_music(query, filename="background_music.mp3"):
    """
    Finds and downloads royalty-free music from Pixabay.
    """
    pixabay_api_key = os.getenv("PIXABAY_API_KEY")
    if not pixabay_api_key:
        print("Pixabay API key not found.")
        return None

    params = {
        "key": pixabay_api_key,
        "q": query,
        "music_type": "music",
        "category": "background",
        "safesearch": "true",
        "order": "popular",
        "per_page": 3
    }
    
    try:
        response = requests.get("https://pixabay.com/api/music/", params=params)
        response.raise_for_status()
        music_data = response.json()
        
        if music_data.get("hits"):
            music_url = music_data["hits"][0]["downloadURL"]
            music_response = requests.get(music_url)
            music_response.raise_for_status()
            with open(filename, "wb") as f:
                f.write(music_response.content)
            return filename
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Pixabay: {e}")
    
    return None
