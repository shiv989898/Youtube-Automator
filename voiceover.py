import os
import asyncio
import pyttsx3
import random
import re
import tempfile
from edge_tts import Communicate
import ssl
import certifi
from gtts import gTTS

# Global cache for Kokoro pipeline to prevent reloading 300MB model every generation
_KOKORO_PIPELINES = {}

# ---------------------------------------------------------------------------
# Best Kokoro voices for YouTube narration – sorted by quality/engagement
KOKORO_VOICES = [
    "af_heart",          # Female, warm & expressive – best overall
    "af_star",           # Female, bright & engaging
    "am_adam",           # Male, clear narrator
    "am_michael",        # Male, conversational
    "af_jessica",        # Female, professional
    "af_nicole",         # Female, friendly
    "am_fenrir",         # Male, deep & authoritative
    "af_sarah",          # Female, natural
    "af_bella",          # Female, warm
    "am_echo",           # Male, smooth
]

# ---------------------------------------------------------------------------
# Edge-TTS voices (fallback) – optimized for engaging, human-like delivery
# ---------------------------------------------------------------------------
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


# ===================================================================
# Kokoro TTS generation (PRIMARY)
# ===================================================================

def _generate_kokoro_tts(text, filename, voice_name="af_heart"):
    """
    Generate voiceover using Kokoro TTS (local, high-quality, free).
    Produces a WAV file then converts to MP3 for consistency with the rest
    of the pipeline.
    """
    from kokoro import KPipeline
    import soundfile as sf
    import numpy as np
    import torch

    global _KOKORO_PIPELINES

    # 'a' = American English, 'b' = British English
    lang_code = 'a'
    if voice_name.startswith('b'):
        lang_code = 'b'

    if lang_code not in _KOKORO_PIPELINES:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"  [Kokoro] Initializing model for '{lang_code}' on {device.upper()}...")
        _KOKORO_PIPELINES[lang_code] = KPipeline(lang_code=lang_code, device=device)
    
    pipeline = _KOKORO_PIPELINES[lang_code]

    # Kokoro streams audio in segments – collect them all
    audio_segments = []
    for _gs, _ps, audio in pipeline(text, voice=voice_name):
        if audio is not None:
            audio_segments.append(audio)

    if not audio_segments:
        raise Exception("Kokoro produced no audio segments")

    full_audio = np.concatenate(audio_segments)

    # Write WAV first (Kokoro outputs 24 kHz audio)
    wav_path = filename.rsplit('.', 1)[0] + '_kokoro.wav'
    sf.write(wav_path, full_audio, 24000)

    # Convert WAV -> MP3 using moviepy (already in the project)
    try:
        from moviepy.editor import AudioFileClip
        clip = AudioFileClip(wav_path)
        clip.write_audiofile(filename, codec='libmp3lame', bitrate='192k',
                             logger=None)
        clip.close()
    except Exception:
        # If moviepy conversion fails, try ffmpeg directly
        import subprocess
        subprocess.run(
            ['ffmpeg', '-y', '-i', wav_path, '-codec:a', 'libmp3lame',
             '-b:a', '192k', filename],
            capture_output=True, check=True,
        )

    # Clean up temp WAV
    if os.path.exists(wav_path):
        try:
            os.remove(wav_path)
        except OSError:
            pass

    return filename


# ===================================================================
# Edge TTS generation (FALLBACK)
# ===================================================================

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
    Removes URLs, technical junk, filler words, and converts to speech-friendly format.
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
    
    # Remove AI-generated filler phrases and meta content
    filler_patterns = [
        # Intro fillers
        r"\b(hey |hi |hello |hey there |hi there |hello there )",
        r"\bwelcome back[,!.]?\s*",
        r"\bthanks for (watching|tuning in|being here)[,!.]?\s*",
        r"\btoday we('re| are) (going to |gonna )?(talk about |discuss |explore |look at |cover )",
        r"\bin this video[,]?\s*(we('ll| will)|I('ll| will))?\s*",
        r"\blet me (tell you|show you|explain)\s*",
        r"\bso[,]?\s+basically[,]?\s*",
        r"\bbasically[,]?\s*",
        r"\b(so |well |now |okay |alright |right )[,]?\s*(?=\w)",
        
        # Meta content / stage directions
        r"\(.*?\)",  # anything in parentheses
        r"word count[:\s]*\d+\s*",
        r"estimated (speaking |reading )?time[:\s]*[\d\w\s]+",
        r"duration[:\s]*[\d\w\s]+",
        r"script (length|duration)[:\s]*[\d\w\s]+",
        r"approximately \d+ (words|seconds)",
        r"note[:\s].*?[.!?]",
        
        # Outro fillers
        r"\bthat's (all for today|it for today|a wrap)[,!.]?\s*",
        r"\buntil next time[,!.]?\s*",
        r"\bsee you (in the next (one|video)|soon|later)[,!.]?\s*",
        r"\bpeace out[,!.]?\s*",
        r"\bbye[,!.]?\s*$",
        r"\btake care[,!.]?\s*$",
        
        # Generic fillers
        r"\byou know[,]?\s*",
        r"\blike[,]?\s+(?=\w)",
        r"\bum+[,]?\s*",
        r"\buh+[,]?\s*",
        r"\bactually[,]?\s*",
        r"\bliterally[,]?\s*",
        r"\bhonestly[,]?\s*",
        r"\bseriously[,]?\s*",
        r"\bobviously[,]?\s*",
        r"\bclearly[,]?\s*",
        r"\bof course[,]?\s*",
        r"\bas you (know|can see)[,]?\s*",
        r"\bin fact[,]?\s*",
        r"\bto be honest[,]?\s*",
        r"\bI mean[,]?\s*",
        r"\bkind of[,]?\s*",
        r"\bsort of[,]?\s*",
        r"\bmore or less[,]?\s*",
        r"\bpretty much[,]?\s*",
        r"\bat the end of the day[,]?\s*",
        r"\blong story short[,]?\s*",
        r"\banyway[s]?[,]?\s*",
        r"\bmoving on[,]?\s*",
        r"\bwith that (said|being said)[,]?\s*",
        r"\bhaving said that[,]?\s*",
        
        # Redundant YouTube phrases
        r"\b(smash |hit )?(that )?(like |subscribe )button[,!.]?\s*",
        r"\bdon't forget to (like|subscribe|comment|share)[,!.]?\s*",
        r"\bmake sure (to |you )(like|subscribe|comment|share)[,!.]?\s*",
        r"\bleave a (like|comment) (below|down below)[,!.]?\s*",
        r"\bturn on (the )?notifications[,!.]?\s*",
        r"\bbell icon[,!.]?\s*",
        r"\bwithout further ado[,]?\s*",
        
        # Part 2/follow-up teases
        r"\bfollow for part \d+[,!.]?\s*",
        r"\bpart \d+ (coming soon|is coming|drops soon)[,!.]?\s*",
        r"\bstay tuned for part \d+[,!.]?\s*",
        r"\bcheck out part \d+[,!.]?\s*",
        r"\bwatch part \d+[,!.]?\s*",
        r"\bmore (in|on) part \d+[,!.]?\s*",
        r"\bcontinued in part \d+[,!.]?\s*",
        r"\bto be continued[,!.]?\s*",
        r"\bfollow for more[,!.]?\s*",
        r"\bmore (coming soon|to come)[,!.]?\s*",
    ]
    
    for pattern in filler_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
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
    
    # Clean up extra whitespace and punctuation
    text = re.sub(r'\s+', ' ', text)           # multiple spaces to single
    text = re.sub(r'\s+([.,!?])', r'\1', text) # remove space before punctuation
    text = re.sub(r'([.,!?])\1+', r'\1', text) # remove duplicate punctuation
    text = re.sub(r'^[,.\s]+', '', text)       # remove leading punctuation
    text = text.strip()
    
    return text


def generate_voiceover(filename, text):
    """
    Generates natural, human-like voiceover optimized for YouTube retention.
    
    Priority chain:
      1. Kokoro TTS (local, free, highest quality)
      2. Edge TTS  (cloud, free, good quality)
      3. gTTS      (cloud, free, basic)
      4. pyttsx3   (local, free, last resort)
    """
    print("🎙️ Generating human-like voiceover...")
    
    # Preprocess text for natural speech
    processed_text = _preprocess_script_for_speech(text)
    print(f"📝 Processed script for natural delivery ({len(processed_text)} chars)")
    
    # ------------------------------------------------------------------
    # 1) Try Kokoro TTS first (best quality, fully local)
    # ------------------------------------------------------------------
    print("\n🌟 Attempting Kokoro TTS (high-quality local engine)...")
    random.shuffle(KOKORO_VOICES)
    # Always try af_heart first – it's the best voice
    voices_to_try = ["af_heart"] + [v for v in KOKORO_VOICES if v != "af_heart"]
    
    for i, voice in enumerate(voices_to_try[:5]):  # Try up to 5 voices
        try:
            print(f"  🔊 Trying Kokoro voice: {voice} ({i+1}/5)...")
            _generate_kokoro_tts(processed_text, filename, voice)
            
            if os.path.exists(filename) and os.path.getsize(filename) > 5000:
                size_kb = os.path.getsize(filename) / 1024
                print(f"  ✅ Kokoro voiceover generated with '{voice}' ({size_kb:.0f} KB)")
                return filename
            else:
                print(f"  ⚠️  Invalid file from Kokoro voice {voice}, trying next...")
                if os.path.exists(filename):
                    os.remove(filename)
        except ImportError as e:
            print(f"  ❌ Kokoro not installed: {e}")
            print("  💡 Install with: pip install kokoro soundfile")
            print("  💡 Also need espeak-ng: https://github.com/espeak-ng/espeak-ng/releases")
            break  # No point trying other Kokoro voices if import fails
        except Exception as e:
            print(f"  ⚠️  Kokoro failed with {voice}: {e}")
            continue
    
    # ------------------------------------------------------------------
    # 2) Fallback to Edge TTS
    # ------------------------------------------------------------------
    print("\n⚡ Falling back to Edge TTS...")
    # Prioritize best voices for engagement (not random - quality first)
    priority_voices = EDGE_VOICES[:4]
    backup_voices = EDGE_VOICES[4:]
    random.shuffle(backup_voices)
    available_voices = priority_voices + backup_voices
    
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
                print(f"  ✅ Edge TTS voiceover generated with {voice}")
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
    
    # ------------------------------------------------------------------
    # 3) Fallback to gTTS
    # ------------------------------------------------------------------
    print("\n\n[INFO] ⚠️ Edge-TTS failed, switching to gTTS...")
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
        
        # ------------------------------------------------------------------
        # 4) Last resort: pyttsx3 (local, reliable)
        # ------------------------------------------------------------------
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
