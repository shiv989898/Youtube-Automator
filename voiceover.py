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


def _add_ssml_prosody(text, voice_name):
    """
    Add SSML markup to make speech more natural and human-like.
    Adds pauses, emphasis, and varied pacing for better retention.
    """
    # Get voice style if available
    style = VOICE_STYLES.get(voice_name, "")
    
    # Add natural pauses after punctuation
    text = re.sub(r'([.!?])\s+', r'\1<break time="400ms"/> ', text)
    text = re.sub(r'([,;:])\s+', r'\1<break time="200ms"/> ', text)
    
    # Add emphasis to key retention phrases (hooks)
    hook_phrases = [
        r"(but here's (?:the|what's))",
        r"(the (?:crazy|wild|shocking|surprising) (?:thing|part|fact))",
        r"(you won't believe)",
        r"(here's why)",
        r"(the secret is)",
        r"(what if I told you)",
        r"(most people don't know)",
        r"(this is (?:crazy|wild|insane))",
    ]
    for pattern in hook_phrases:
        text = re.sub(pattern, r'<emphasis level="strong">\1</emphasis>', text, flags=re.IGNORECASE)
    
    # Add slight rate variation for more natural delivery
    # Start slightly faster (hook), slow down for key info
    sentences = text.split('<break time="400ms"/>')
    processed = []
    for i, sentence in enumerate(sentences):
        if i == 0:
            # First sentence: slightly faster for hook energy
            sentence = f'<prosody rate="+8%">{sentence}</prosody>'
        elif i == len(sentences) - 1:
            # Last sentence: slow down for CTA impact
            sentence = f'<prosody rate="-5%" pitch="+5%">{sentence}</prosody>'
        else:
            # Middle: natural variation
            rate_var = random.choice(["+3%", "+0%", "-3%"])
            sentence = f'<prosody rate="{rate_var}">{sentence}</prosody>'
        processed.append(sentence)
    
    text = '<break time="400ms"/>'.join(processed)
    
    # Wrap in SSML with voice style if supported
    if style:
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                   xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{voice_name}">
                <mstts:express-as style="{style}" styledegree="1.2">
                    <prosody pitch="+2%">
                        {text}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>'''
    else:
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="{voice_name}">
                <prosody pitch="+2%">
                    {text}
                </prosody>
            </voice>
        </speak>'''
    
    return ssml


async def _generate_edge_tts(text, filename, voice_name, use_ssml=True):
    """
    Generate voiceover using edge-tts with natural prosody.
    Uses SSML for human-like speech patterns and emotional delivery.
    """
    try:
        if use_ssml:
            # Use SSML for more natural, human-like speech
            ssml_text = _add_ssml_prosody(text, voice_name)
            # Edge-tts with rate adjustment for energy
            communicate = Communicate(ssml_text, voice_name, rate="+5%", pitch="+2Hz")
        else:
            # Fallback to plain text with slight speed boost for energy
            communicate = Communicate(text, voice_name, rate="+5%", pitch="+2Hz")
        
        await communicate.save(filename)
    except Exception as e:
        # If SSML fails, try without it
        if use_ssml:
            communicate = Communicate(text, voice_name, rate="+5%", pitch="+2Hz")
            await communicate.save(filename)
        else:
            raise Exception(f"Edge TTS error: {str(e)}")

def _preprocess_script_for_speech(text):
    """
    Preprocess script to make it more natural when spoken.
    Converts written text to speech-friendly format.
    """
    # Remove Host: markers
    text = re.sub(r'\*?\*?Host:\*?\*?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[.*?\]', '', text)  # Remove stage directions
    
    # Convert numbers to be more speakable
    text = re.sub(r'\b(\d+)%', r'\1 percent', text)
    text = re.sub(r'\$(\d+)', r'\1 dollars', text)
    
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
    
    # Try edge-tts first (best quality) with SSML for natural speech
    for i, voice in enumerate(available_voices):
        try:
            progress = int(((i + 1) / len(available_voices)) * 100)
            bar_length = 20
            filled = int((progress / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            style = VOICE_STYLES.get(voice, "natural")
            print(f"\r  Voice [{bar}] {progress}% - {voice} ({style})", end="", flush=True)
            asyncio.run(_generate_edge_tts(processed_text, filename, voice, use_ssml=True))
            
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
