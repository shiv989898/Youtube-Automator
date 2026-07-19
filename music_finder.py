import os
import random
import requests


MUSIC_CATEGORIES = {
    "UPBEAT": [
        ("Sneaky Snitch", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sneaky%20Snitch.mp3"),
        ("Monkeys Spinning Monkeys", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Monkeys%20Spinning%20Monkeys.mp3"),
        ("Upbeat Party - Scott Holmes", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Scott_Holmes_-_02_-_Upbeat_Party.mp3"),
        ("Comedie - Jahzzar", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Jahzzar_-_02_-_Comedie.mp3"),
        ("Happy Boy End Theme", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Happy%20Boy%20End%20Theme.mp3"),
        ("Splashing Around", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Splashing%20Around.mp3")
    ],
    "MYSTERIOUS": [
        ("Darkest Child", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkest%20Child.mp3"),
        ("Cipher", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Cipher.mp3"),
        ("Echoes - Density & Time", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Echoes.mp3"),
        ("Dreams Become Real - Kevin MacLeod", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Dreams_Become_Real.mp3")
    ],
    "TECH_CORPORATE": [
        ("Corporate Success - Scott Holmes", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Scott_Holmes_-_03_-_Corporate_Success.mp3"),
        ("Inspiring Presentation - Scott Holmes", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Scott_Holmes_-_01_-_Inspiring_Presentation.mp3"),
        ("Crypto", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Crypto.mp3")
    ],
    "CALM_NATURE": [
        ("Carefree", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Carefree.mp3"),
        ("Solitude - Jahzzar", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Jahzzar_-_01_-_Solitude.mp3"),
        ("Nimbus - Eveningland", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Nimbus.mp3"),
        ("Perspectives", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Perspectives.mp3")
    ]
}

def determine_category(topic):
    topic = (topic or "").lower()
    if any(w in topic for w in ["scary", "mystery", "space", "secret", "crime", "dark", "truth", "shocking"]):
        return "MYSTERIOUS"
    elif any(w in topic for w in ["tech", "ai", "coding", "business", "finance", "crypto", "money"]):
        return "TECH_CORPORATE"
    elif any(w in topic for w in ["nature", "calm", "relax", "health", "water", "forest"]):
        return "CALM_NATURE"
    return "UPBEAT"

def download_sfx():
    """Generates synthetic pop and whoosh SFX files if they don't exist."""
    import numpy as np
    import soundfile as sf
    import os
    
    os.makedirs('assets', exist_ok=True)
    
    # 1. Generate "Pop"
    pop_path = 'assets/pop.wav'
    if not os.path.exists(pop_path):
        sample_rate = 44100
        t = np.linspace(0, 0.05, int(sample_rate * 0.05), False) # 50ms
        freq = np.linspace(800, 200, len(t))
        pop = np.sin(2 * np.pi * freq * t)
        envelope = np.exp(-t * 100) # fast decay
        sf.write(pop_path, pop * envelope * 0.5, sample_rate)
        
    # 2. Generate "Whoosh"
    whoosh_path = 'assets/whoosh.wav'
    if not os.path.exists(whoosh_path):
        sample_rate = 44100
        t = np.linspace(0, 0.3, int(sample_rate * 0.3), False) # 300ms
        noise = np.random.normal(0, 1, len(t))
        # envelope: attack then decay
        envelope = np.sin(np.pi * t / 0.3) ** 2
        sf.write(whoosh_path, noise * envelope * 0.15, sample_rate)
        
    return pop_path, whoosh_path


def find_and_download_music(query, filename="assets/background_music.mp3", max_retries=5, topic=None):
    """
    Finds and downloads royalty-free music from reliable sources.
    Uses topic analysis to select the right vibe for the video.
    """
    category = determine_category(topic)
    print(f"Finding background music (Vibe: {category})...")
    print("  ⏳ Selecting music track...", end="", flush=True)

    sources = MUSIC_CATEGORIES.get(category, MUSIC_CATEGORIES["UPBEAT"]).copy()
    random.shuffle(sources)
    attempts = min(max_retries, len(sources))

    for attempt in range(attempts):
        track_name, music_url = sources[attempt]

        try:
            print(f"\r  ⏳ Attempt {attempt + 1}/{attempts}: '{track_name}'..." + " " * 20, end="", flush=True)
            # Stream download with timeout to prevent hanging
            response = requests.get(music_url, timeout=30, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))

            # Download in chunks to avoid memory issues and timeouts
            chunk_size = 8192
            downloaded_size = 0
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Show progress bar if we know the total size
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            bar_length = 20
                            filled = int((progress / 100) * bar_length)
                            bar = "█" * filled + "░" * (bar_length - filled)
                            print(f"\r  Downloading: [{bar}] {progress}% ({downloaded_size//1024}KB/{total_size//1024}KB)", end="", flush=True)

            # Check if we got actual content
            if downloaded_size < 10000:  # Less than 10KB is suspicious
                print(f"\n  ⚠️  Downloaded file too small, trying another source...")
                if os.path.exists(filename):
                    os.remove(filename)
                continue

            print(f"\r  ✅ Saved '{track_name}' ({downloaded_size/1024:.1f}KB)" + " " * 30)
            print(f"  📜 License: Creative Commons / Royalty-Free (safe for YouTube)")
            return filename

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)[:80]}")
            if attempt < attempts - 1:
                print("Trying another source...")
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {str(e)[:80]}")
            if attempt < attempts - 1:
                print("Trying another source...")

    print("[WARNING] All music download attempts failed. Video will be created without background music.")
    return None
