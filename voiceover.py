import os
import asyncio
from edge_tts import Communicate

async def _generate_with_edge_tts(text, filename):
    """
    Async helper to generate voiceover with edge-tts.
    Uses Microsoft Jenny Neural voice (female, very natural, expressive).
    """
    # Best voices for YouTube Shorts (natural, expressive, engaging):
    # en-US-JennyNeural - Female, warm, conversational (BEST for shorts)
    # en-US-GuyNeural - Male, friendly, clear
    # en-US-AriaNeural - Female, cheerful, upbeat
    # en-GB-SoniaNeural - British female, professional
    
    voice = "en-US-JennyNeural"  # Natural, engaging female voice
    
    communicate = Communicate(text, voice, rate="+20%", pitch="+5Hz")  # Faster for more energy and engagement
    await communicate.save(filename)

def generate_voiceover(filename, text):
    """
    Generates a voiceover using edge-tts (Microsoft neural voices) for realistic, emotional speech.
    Falls back to pyttsx3 if edge-tts fails.
    No GPU or API keys required - completely free and local processing.
    """
    print("Generating voiceover...")
    
    # Try edge-tts first (Microsoft neural voices, no API key needed)
    try:
        # Run async edge-tts
        asyncio.run(_generate_with_edge_tts(text, filename))
        
        # Verify file was created
        if os.path.exists(filename) and os.path.getsize(filename) > 1000:
            print(f"[SUCCESS] Voiceover generated with edge-tts (Microsoft Jenny Neural - high quality)")
            return filename
        else:
            print("[WARNING] edge-tts generated invalid file. Falling back to system voice...")
            
    except Exception as e:
        print(f"[WARNING] edge-tts failed: {e}")
        print("Trying gTTS (Google Text-to-Speech)...")
    
    # Try gTTS (Google Text-to-Speech) as middle fallback
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False, tld='com')
        tts.save(filename)
        
        # Verify file was created
        if os.path.exists(filename) and os.path.getsize(filename) > 1000:
            print(f"[SUCCESS] Voiceover generated with gTTS (Google voice - reliable)")
            return filename
        else:
            print("[WARNING] gTTS generated invalid file. Trying system voice...")
            
    except Exception as e:
        print(f"[WARNING] gTTS failed: {e}")
        print("Falling back to system voice...")
    
    # Fallback to pyttsx3 if both edge-tts and gTTS fail
    try:
        import pyttsx3
        print("[INFO] Initializing system text-to-speech...")
        engine = pyttsx3.init()

        # --- Enhancements for more human-like voice ---
        # 1. Set a faster, more energetic rate for YouTube Shorts
        engine.setProperty('rate', 200)  # Faster, more engaging pace

        # 2. Set volume to maximum for clarity
        engine.setProperty('volume', 1.0)  # 100% volume

        # 3. Select the best available voice (prioritize female voices for better quality)
        voices = engine.getProperty('voices')
        
        if not voices:
            raise Exception("No system voices available")
        
        # Try to find Zira (female, high quality) or other premium voices
        zira = next((v for v in voices if 'zira' in v.name.lower()), None)
        hazel = next((v for v in voices if 'hazel' in v.name.lower()), None)
        susan = next((v for v in voices if 'susan' in v.name.lower()), None)
        david = next((v for v in voices if 'david' in v.name.lower()), None)

        if zira:
            engine.setProperty('voice', zira.id)
            print("[OK] Using premium 'Zira' voice (female, clear, professional)")
        elif hazel:
            engine.setProperty('voice', hazel.id)
            print("[OK] Using premium 'Hazel' voice (female, warm)")
        elif susan:
            engine.setProperty('voice', susan.id)
            print("[OK] Using 'Susan' voice (female)")
        elif david:
            engine.setProperty('voice', david.id)
            print("[OK] Using 'David' voice (male, clear)")
        else:
            # Use first available voice
            if voices:
                engine.setProperty('voice', voices[0].id)
                print(f"[OK] Using system voice: {voices[0].name}")
            else:
                print("[WARNING] Using default system voice")
        # --- End of Enhancements ---

        engine.save_to_file(text, filename)
        engine.runAndWait()
        
        # Verify file was created
        if os.path.exists(filename) and os.path.getsize(filename) > 1000:
            print(f"[SUCCESS] Voiceover saved to {filename} (System voice)")
            return filename
        else:
            raise Exception("pyttsx3 failed to generate valid audio file")
        
    except Exception as e:
        print(f"[ERROR] All voiceover methods failed: {e}")
        print("[CRITICAL] Cannot proceed without voiceover. Exiting...")
        raise Exception(f"Error generating voiceover: {e}")
    except Exception as e:
        print(f"[ERROR] Error generating voiceover: {e}")
        return None
