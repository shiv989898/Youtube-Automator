import os
import asyncio
import pyttsx3
import random
import re
from edge_tts import Communicate
import ssl
import certifi
from gtts import gTTS

# Edge-TTS voices optimized for engaging, human-like delivery
# Prioritized by natural conversational quality
EDGE_VOICES = [
    "en-US-DavisNeural",      # Male, energetic & expressive - BEST for YouTube
    "en-US-JennyNeural",      # Female, friendly & natural
    "en-US-AriaNeural",       # Female, warm & conversational
    "en-US-TonyNeural",       # Male, confident storyteller
    "en-US-GuyNeural",        # Male, clear & engaging
    "en-GB-RyanNeural",       # Male, British, authoritative
    "en-GB-SoniaNeural",      # Female, British, warm
    "en-AU-NatashaNeural",    # Female, Australian, friendly
    "en-US-SaraNeural",       # Female, professional
    "en-CA-ClaraNeural",      # Female, Canadian
    "en-US-AmberNeural",      # Female, conversational
    "en-US-AnaNeural",        # Female, clear
]

# Voice styles that make speech sound more human and engaging
VOICE_STYLES = {
    "en-US-DavisNeural": "cheerful",      # Upbeat, engaging
    "en-US-JennyNeural": "chat",          # Conversational
    "en-US-AriaNeural": "narration-relaxed",  # Storytelling
    "en-US-TonyNeural": "excited",        # High energy
    "en-US-GuyNeural": "newscast",        # Professional but warm
    "en-GB-RyanNeural": "chat",           # Conversational British
    "en-GB-SoniaNeural": "cheerful",      # Friendly British
}

git add voiceover.py
git commit -m "Fix voiceover reading URLs and technical junk - Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
git push
async def _generate_edge_tts(text, filename, voice_name, use_ssml=True):
    """
    Generate voiceover using edge-tts with natural prosody.
    Uses simple rate/pitch adjustments (edge-tts doesn't support full SSML).
    """
    try:
        # Edge-tts uses simple parameters, not full SSML
        # Slight speed boost and pitch adjustment for energy
        communicate = Communicate(text, voice_name, rate="+5%", pitch="+2Hz")
        await communicate.save(filename)
    except Exception as e:
        raise Exception(f"Edge TTS error: {str(e)}")

def _preprocess_script_for_speech(text):
    """
    Preprocess script to make it more natural when spoken.
    Removes URLs, technical junk, and converts to speech-friendly format.
    """
    # Remove Host: markers and stage directions
    text = re.sub(r'\*?\*?Host:\*?\*?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[.*?\]', '', text)  # Remove stage directions like [pause]
    
    # Remove URLs completely (https://, http://, www.)
    text = re.sub(r'https?://[^\s]+', '', text)
    text = re.sub(r'www\.[^\s]+', '', text)
    text = re.sub(r'[a-zA-Z0-9.-]+\.(com|org|net|io|co|edu|gov)[^\s]*', '', text)
    
    # Remove any XML/SSML tags that might have leaked through
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'xmlns[^\s"]*', '', text)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* -> italic
    text = re.sub(r'__([^_]+)__', r'\1', text)      # __underline__
    text = re.sub(r'`([^`]+)`', r'\1', text)        # `code`
    text = re.sub(r'#{1,6}\s*', '', text)           # # headers
    
    # Remove special characters that sound weird when spoken
    text = re.sub(r'[<>{}|\\^~`]', '', text)
    text = re.sub(r'\s*[-–—]\s*', ', ', text)       # dashes to commas
    text = re.sub(r'\s*/\s*', ' or ', text)         # slash to "or"
    text = re.sub(r'&amp;', 'and', text)
    text = re.sub(r'&', ' and ', text)
    
    # Remove hashtags and mentions
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'@\w+', '', text)
    
    # Remove emoji (unicode ranges for common emoji)
    text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)  # emoticons
    text = re.sub(r'[\U0001F300-\U0001F5FF]', '', text)  # symbols & pictographs
    text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)  # transport & map
    text = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', text)  # flags
    text = re.sub(r'[\U00002702-\U000027B0]', '', text)  # dingbats
    
    # Convert numbers to be more speakable
    text = re.sub(r'\b(\d+)%', r'\1 percent', text)
    text = re.sub(r'\$(\d+)', r'\1 dollars', text)
    text = re.sub(r'(\d+)k\b', r'\1 thousand', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+)m\b', r'\1 million', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+)b\b', r'\1 billion', text, flags=re.IGNORECASE)
    
    # Add natural contractions (sounds more human)
    replacements = {
        "do not": "don't",
        "does not": "doesn't", 
        "did not": "didn't",
        "will not": "won't",
        "can not": "can't",
        "cannot": "can't",
        "should not": "shouldn't",
        "would not": "wouldn't",
        "could not": "couldn't",
        "it is": "it's",
        "that is": "that's",
        "what is": "what's",
        "here is": "here's",
        "there is": "there's",
        "you are": "you're",
        "we are": "we're",
        "they are": "they're",
        "I am": "I'm",
        "let us": "let's",
        "going to": "gonna",
        "want to": "wanna",
        "got to": "gotta",
    }
    for formal, casual in replacements.items():
        text = re.sub(rf'\b{formal}\b', casual, text, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    text = ' '.join(text.split())
    
    return text


def generate_voiceover(filename, text):
    """
    Generates natural, human-like voiceover optimized for YouTube retention.
    Uses SSML prosody for emotional delivery and varied pacing.
    Features: pauses, emphasis, pitch variation, and conversational tone.
    """
    print("🎙️ Generating human-like voiceover...")
    
    # Preprocess text for natural speech
    processed_text = _preprocess_script_for_speech(text)
    print(f"📝 Processed script for natural delivery ({len(processed_text)} chars)")
    
    # Prioritize best voices for engagement (not random - quality first)
    # First 4 voices are optimized for YouTube engagement
    priority_voices = EDGE_VOICES[:4]
    backup_voices = EDGE_VOICES[4:]
    random.shuffle(backup_voices)
    available_voices = priority_voices + backup_voices
    
    print(f"Attempting to generate voiceover with {len(available_voices)} voices...")
    
    # Try edge-tts first (best quality)
    for i, voice in enumerate(available_voices):
        try:
            progress = int(((i + 1) / len(available_voices)) * 100)
            bar_length = 20
            filled = int((progress / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            style = VOICE_STYLES.get(voice, "natural")
            print(f"\r  Voice [{bar}] {progress}% - {voice} ({style})", end="", flush=True)
            asyncio.run(_generate_edge_tts(processed_text, filename, voice))
            
            # Verify file
            if os.path.exists(filename) and os.path.getsize(filename) > 5000:
                bar = "█" * 20
                print(f"\r  Voice [{bar}] 100% - Success!")
                print(f"  ✅ Human-like voiceover generated with {voice}")
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
    print("\n[INFO] ⚠️ Edge-TTS failed, switching to gTTS...")
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
