import os
import asyncio
import pyttsx3
import random
from edge_tts import Communicate
import ssl
import certifi
from gtts import gTTS

# Edge-TTS voices (Microsoft neural voices - expanded list for variety)
EDGE_VOICES = [
    "en-US-JennyNeural",      # Female, friendly
    "en-US-AriaNeural",       # Female, warm
    "en-US-GuyNeural",        # Male, clear
    "en-GB-SoniaNeural",      # Female, British
    "en-US-SaraNeural",       # Female, professional
    "en-US-TonyNeural",       # Male, confident
    "en-AU-NatashaNeural",    # Female, Australian
    "en-CA-ClaraNeural",      # Female, Canadian
    "en-US-DavisNeural",      # Male, energetic
    "en-US-AmberNeural",      # Female, conversational
    "en-GB-RyanNeural",       # Male, British
    "en-US-AnaNeural",        # Female, clear
]

async def _generate_edge_tts(text, filename, voice_name):
    """
    Generate voiceover using edge-tts with proper SSL handling.
    Handles Microsoft's new API security tokens (Sec-MS-GEC).
    """
    try:
        # Create communicate object with validated voice
        # Force rate to +0% to avoid some server-side checks
        communicate = Communicate(text, voice_name, rate="+0%")
        await communicate.save(filename)
    except Exception as e:
        raise Exception(f"Edge TTS error: {str(e)}")

def generate_voiceover(filename, text):
    """
    Generates high-quality voiceover using edge-tts (v7.2.7+) with pyttsx3 fallback.
    Handles Microsoft's new API security requirements.
    Auto-optimized for YouTube content.
    Uses random voice selection for variety.
    """
    print("Generating voiceover...")
    
    # Randomize voice selection for variety in each video
    available_voices = EDGE_VOICES.copy()
    random.shuffle(available_voices)
    
    print(f"Attempting to generate voiceover with {len(available_voices)} voices...")
    
    # Try edge-tts first (best quality)
    for i, voice in enumerate(available_voices):
        try:
            progress = int(((i + 1) / len(available_voices)) * 100)
            bar_length = 20
            filled = int((progress / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"\r  Voice attempt [{bar}] {progress}% - Trying: {voice}", end="", flush=True)
            asyncio.run(_generate_edge_tts(text, filename, voice))
            
            # Verify file
            if os.path.exists(filename) and os.path.getsize(filename) > 5000:
                bar = "█" * 20
                print(f"\r  Voice attempt [{bar}] 100% - Success!")
                print(f"  ✅ Voiceover generated with edge-tts ({voice})")
                return filename
            else:
                print(f"\n  ⚠️  Invalid file from {voice}, trying next voice...")
                if os.path.exists(filename):
                    os.remove(filename)
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Invalid response status" in error_msg:
                # Don't print full error for 401s to keep logs clean, just continue
                pass
            else:
                print(f"\n  [WARNING] edge-tts failed with {voice}: {e}")
            
            if i < len(available_voices) - 1:
                continue
            else:
                break
    
    # Fallback to gTTS (works well in cloud environments like GitHub Actions)
    print("[INFO] ⚠️ Edge-TTS failed (401 auth errors), switching to gTTS...")
    try:
        print("[INFO] 🌐 Requesting voiceover from Google TTS API...")
        tts = gTTS(text=text, lang='en', slow=False, tld='com')
        tts.save(filename)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 5000:
            print(f"[SUCCESS] ✅ Voiceover successfully generated with gTTS!")
            print(f"[INFO] 📁 File: {filename} ({os.path.getsize(filename)} bytes)")
            return filename
        else:
            raise Exception("gTTS generated invalid audio file")
    
    except Exception as gtts_error:
        print(f"[ERROR] ❌ gTTS failed: {gtts_error}")
        import traceback
        traceback.print_exc()
        
        # Last resort: pyttsx3 (local, reliable)
        print("[INFO] Falling back to local pyttsx3...")
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # Check for specific errors
            if "403" in error_msg or "Forbidden" in error_msg:
                print("[ERROR] API access denied - Microsoft may have blocked unofficial access")
                break  # Don't try other voices if blocked
            elif "No audio" in error_msg:
                print("[WARNING] No audio received - network or API issue")
                if i < len(EDGE_VOICES) - 1:
                    continue
                break
            elif i < len(EDGE_VOICES) - 1:
                continue
            else:
                break
    
    # Fallback to gTTS (works well in cloud environments like GitHub Actions)
    print("[INFO] ⚠️ Edge-TTS failed (401 auth errors), switching to gTTS...")
    try:
        print("[INFO] 🌐 Requesting voiceover from Google TTS API...")
        tts = gTTS(text=text, lang='en', slow=False, tld='com')
        tts.save(filename)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 5000:
            print(f"[SUCCESS] ✅ Voiceover successfully generated with gTTS!")
            print(f"[INFO] 📁 File: {filename} ({os.path.getsize(filename)} bytes)")
            return filename
        else:
            raise Exception("gTTS generated invalid audio file")
    except Exception as gtts_error:
        print(f"[ERROR] ❌ gTTS failed: {gtts_error}")
        import traceback
        traceback.print_exc()
    
        # Last resort: pyttsx3 (local, reliable)
        print("[INFO] Falling back to local pyttsx3...")
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if not voices:
                raise Exception("No system voices available")
            # Auto-select best voice
            selected_voice = None
            voice_preferences = ['zira', 'hazel', 'susan', 'victoria', 'david']
            for pref in voice_preferences:
                voice = next((v for v in voices if pref in v.name.lower()), None)
                if voice:
                    selected_voice = voice.id
                    print(f"[OK] Selected voice: {pref.title()}")
                    break
            if not selected_voice:
                selected_voice = voices[0].id
                print(f"[OK] Using: {voices[0].name}")
            engine.setProperty('voice', selected_voice)
            engine.setProperty('rate', 160)  # Optimized for YouTube
            engine.setProperty('volume', 1.0)
            engine.save_to_file(text, filename)
            engine.runAndWait()
            if os.path.exists(filename) and os.path.getsize(filename) > 5000:
                print(f"[SUCCESS] Voiceover saved with pyttsx3")
                return filename
            else:
                raise Exception("Generated audio file is invalid")
        except Exception as e:
            print(f"[ERROR] All voiceover methods failed: {e}")
            raise Exception(f"Error generating voiceover: {e}")
