import os
import random
import requests

def find_and_download_music(query, filename="background_music.mp3", max_retries=3):
    """
    Finds and downloads royalty-free music from reliable sources.
    Prioritizes fast, reliable Kevin MacLeod tracks, then falls back to other sources.
    These tracks are 100% copyright-free and safe for YouTube.
    """
    print("Finding background music...")
    
    # PRIMARY: Kevin MacLeod (incompetech.com) - HIGHLY RELIABLE, fast servers, royalty-free
    reliable_sources = [
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sneaky%20Snitch.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Carefree.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Happy%20Boy%20End%20Theme.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Monkeys%20Spinning%20Monkeys.mp3",
        "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Wallpaper.mp3",
    ]
    
    # FALLBACK: Free Music Archive via archive.org (slower, sometimes unreliable)
    fallback_sources = [
        "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Jahzzar_-_01_-_Solitude.mp3",
        "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Jahzzar_-_02_-_Comedie.mp3",
        "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Jahzzar_-_03_-_Patience.mp3",
        "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Scott_Holmes_-_01_-_Inspiring_Presentation.mp3",
        "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Scott_Holmes_-_02_-_Upbeat_Party.mp3",
    ]
    
    # Try reliable sources first (up to max_retries times)
    all_sources = reliable_sources + fallback_sources
    attempted_urls = set()
    
    for attempt in range(max_retries):
        # Pick from reliable sources first, then fallback
        if attempt < len(reliable_sources):
            music_url = reliable_sources[attempt % len(reliable_sources)]
        else:
            # Try remaining sources we haven't attempted yet
            remaining = [url for url in all_sources if url not in attempted_urls]
            if not remaining:
                break
            music_url = random.choice(remaining)
        
        attempted_urls.add(music_url)
        
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Downloading copyright-free background music...")
            print(f"Source: {music_url.split('/')[-1][:50]}")
            
            response = requests.get(music_url, timeout=30)  # Shorter timeout for faster fails
            response.raise_for_status()
            
            # Check if we got actual content
            if len(response.content) < 10000:  # Less than 10KB is suspicious
                print("Downloaded file too small, trying another...")
                continue
            
            with open(filename, "wb") as f:
                f.write(response.content)
            
            print(f"[SUCCESS] Copyright-free music saved to {filename} (Size: {len(response.content)/1024:.1f}KB)")
            print("Music: Royalty-Free licensed (Kevin MacLeod / Creative Commons)")
            return filename
                
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)[:80]}")
            if attempt < max_retries - 1:
                print("Trying another source...")
                continue
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {str(e)[:80]}")
            if attempt < max_retries - 1:
                continue
    
    print("[WARNING] All music download attempts failed. Video will be created without background music.")
    return None
