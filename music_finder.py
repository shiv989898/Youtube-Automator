import os
import random
import requests


ROYALTY_FREE_TRACKS = [
    # Kevin MacLeod classics
    ("Sneaky Snitch", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sneaky%20Snitch.mp3"),
    ("Carefree", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Carefree.mp3"),
    ("Happy Boy End Theme", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Happy%20Boy%20End%20Theme.mp3"),
    ("Monkeys Spinning Monkeys", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Monkeys%20Spinning%20Monkeys.mp3"),
    ("Wallpaper", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Wallpaper.mp3"),
    ("Cipher", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Cipher.mp3"),
    ("Darkest Child", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkest%20Child.mp3"),
    ("Future Gladiator", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Future%20Gladiator.mp3"),
    ("Pamgaea", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Pamgaea.mp3"),
    ("Sugar Plum Dark", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sugar%20Plum%20Dark.mp3"),

    # Additional incompetech tracks
    ("Splashing Around", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Splashing%20Around.mp3"),
    ("Marty Gots a Plan", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Marty%20Gots%20a%20Plan.mp3"),
    ("Amazing Plan", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Amazing%20Plan.mp3"),
    ("Limit 70", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Limit%2070.mp3"),
    ("Hard Boiled", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Hard%20Boiled.mp3"),
    ("Perspectives", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Perspectives.mp3"),
    ("Rumination", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Rumination.mp3"),
    ("Rocket Power", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Rocket%20Power.mp3"),
    ("Sunshine", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sunshine.mp3"),
    ("Crypto", "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Crypto.mp3"),

    # Free Music Archive highlights
    ("Solitude - Jahzzar", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Jahzzar_-_01_-_Solitude.mp3"),
    ("Comedie - Jahzzar", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Jahzzar_-_02_-_Comedie.mp3"),
    ("Patience - Jahzzar", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Jahzzar_-_03_-_Patience.mp3"),
    ("Inspiring Presentation - Scott Holmes", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Scott_Holmes_-_01_-_Inspiring_Presentation.mp3"),
    ("Upbeat Party - Scott Holmes", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Scott_Holmes_-_02_-_Upbeat_Party.mp3"),
    ("Corporate Success - Scott Holmes", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Scott_Holmes_-_03_-_Corporate_Success.mp3"),
    ("Overcome - Ugonna Onyekwe", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Ugonna_Onyekwe_-_03_-_Overcome.mp3"),
    ("Dreams Become Real - Kevin MacLeod", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Dreams_Become_Real.mp3"),
    ("Nimbus - Eveningland", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Nimbus.mp3"),
    ("Echoes - Density & Time", "https://ia903006.us.archive.org/29/items/Free_Music_Archive_CC_By/Echoes.mp3")
]


def find_and_download_music(query, filename="background_music.mp3", max_retries=5):
    """
    Finds and downloads royalty-free music from reliable sources.
    Sources are randomized each run to distribute usage and add variety.
    """
    print("Finding background music...")
    print("  ⏳ Selecting music track...", end="", flush=True)

    sources = ROYALTY_FREE_TRACKS.copy()
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
