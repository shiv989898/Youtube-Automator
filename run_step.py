import os
import sys
import json
import base64
from dotenv import load_dotenv
import topic_finder
import script_generator
import voiceover
import visuals
import video_creator
import youtube_uploader
import music_finder
import re
import math

STATE_FILE = "state.json"

def setup_credentials():
    """Decode credentials from environment variables for Render.com deployment."""
    if os.getenv('CLIENT_SECRET_BASE64'):
        try:
            secret_content = base64.b64decode(os.getenv('CLIENT_SECRET_BASE64'))
            with open('client_secret.json', 'wb') as f:
                f.write(secret_content)
        except Exception as e:
            print(f"Warning: Could not decode CLIENT_SECRET_BASE64: {e}")
    
    if os.getenv('TOKEN_PICKLE_BASE64'):
        try:
            token_content = base64.b64decode(os.getenv('TOKEN_PICKLE_BASE64'))
            with open('token.pickle', 'wb') as f:
                f.write(token_content)
        except Exception as e:
            print(f"Warning: Could not decode TOKEN_PICKLE_BASE64: {e}")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

def run_step(step_name):
    os.makedirs('assets', exist_ok=True)
    load_dotenv()
    setup_credentials()
    state = load_state()

    if step_name == "topic":
        print("Finding trending topic...")
        try:
            topic = topic_finder.get_trending_topic()
        except Exception as e:
            print(f"Could not get trending topic: {e}. Using fallback topic.")
            topic = "The history of the internet"
        print(f"Trending topic: {topic}")
        state["topic"] = topic
        save_state(state)

    elif step_name == "script":
        topic = state.get("topic", "The history of the internet")
        print("Generating script...")
        script = script_generator.generate_script(topic)
        print(f"Script:\n{script}")

        cleaned_script = re.sub(r"^(Here's|Here is).*?script.*?:\s*", '', script, flags=re.IGNORECASE)
        cleaned_script = re.sub(r'\*\*\(Scene:.*?\)\*\*|\(Scene:.*?\)','', cleaned_script)
        cleaned_script = re.sub(r'\*\*Host:\*\*|\*\*|\(.*?\)','', cleaned_script).strip()
        cleaned_script = re.sub(r'(---|\*\*)?(\n)?(Word Count:.*?|Estimated Speaking Time:.*?)(\n)?', '', cleaned_script, flags=re.IGNORECASE)
        cleaned_script = re.sub(r'---+', '', cleaned_script)
        cleaned_script = " ".join(cleaned_script.split())
        
        if not cleaned_script:
            print("Could not extract any narrator lines from the script. Exiting.")
            sys.exit(1)

        print(f"Cleaned script for voiceover:\n{cleaned_script}")
        state["script"] = script
        state["cleaned_script"] = cleaned_script
        save_state(state)

    elif step_name == "voiceover":
        cleaned_script = state.get("cleaned_script")
        if not cleaned_script:
            print("No cleaned_script found in state. Run 'script' step first.")
            sys.exit(1)
            
        print("Generating voiceover...")
        voiceover_file = "assets/voiceover.mp3"
        voiceover.generate_voiceover(voiceover_file, cleaned_script)
        print(f"Voiceover saved to {voiceover_file}")
        
        from moviepy.editor import AudioFileClip
        audio_clip = AudioFileClip(voiceover_file)
        voiceover_duration = int(audio_clip.duration)
        audio_clip.close()
        print(f"Voiceover duration: {voiceover_duration}s")
        
        target_seconds_per_visual = 3
        min_visuals = 6
        max_visuals = 16
        visual_count = max(min_visuals, math.ceil(voiceover_duration / target_seconds_per_visual))
        visual_count = min(max_visuals, visual_count)
        print(f"Target visual count: {visual_count} (~{target_seconds_per_visual}s per cut)")

        state["voiceover_file"] = voiceover_file
        state["voiceover_duration"] = voiceover_duration
        state["visual_count"] = visual_count
        save_state(state)

    elif step_name == "music":
        print("Finding background music...")
        music_file = music_finder.find_and_download_music("upbeat")
        if music_file:
            print(f"Background music saved to {music_file}")
        else:
            print("Could not find background music.")
            
        state["music_file"] = music_file
        save_state(state)

    elif step_name == "visuals":
        topic = state.get("topic")
        visual_count = state.get("visual_count")
        voiceover_duration = state.get("voiceover_duration")
        cleaned_script = state.get("cleaned_script")
        
        if not all([topic, visual_count, voiceover_duration, cleaned_script]):
            print("Missing state data. Run previous steps first.")
            sys.exit(1)
            
        print("Gathering visuals...")
        visual_files = visuals.get_visuals(
            topic,
            visual_count,
            target_duration=voiceover_duration,
            script_text=cleaned_script,
        )
        print(f"Found {len(visual_files)} visuals.")
        if not visual_files:
            print("No visuals found. Exiting.")
            sys.exit(1)
            
        state["visual_files"] = visual_files
        save_state(state)

    elif step_name == "video":
        visual_files = state.get("visual_files")
        voiceover_file = state.get("voiceover_file")
        music_file = state.get("music_file")
        cleaned_script = state.get("cleaned_script")
        
        if not all([visual_files, voiceover_file, cleaned_script]):
            print("Missing state data. Run previous steps first.")
            sys.exit(1)
            
        print("Creating video...")
        video_creator.create_video(visual_files, voiceover_file, "assets/final_video.mp4", music_file, cleaned_script)
        print("Video created successfully: assets/final_video.mp4")

    elif step_name == "upload":
        topic = state.get("topic")
        cleaned_script = state.get("cleaned_script")
        
        if not all([topic, cleaned_script]):
            print("Missing state data. Run previous steps first.")
            sys.exit(1)
            
        print("Uploading to YouTube...")
        video_id = youtube_uploader.upload_to_youtube(
            "assets/final_video.mp4",
            topic,
            cleaned_script
        )
        if video_id:
            print(f"Upload successful! Video ID: {video_id}")
            print(f"Watch at: https://youtube.com/shorts/{video_id}")
            state["video_id"] = video_id
            save_state(state)
        else:
            print("Upload failed.")
            sys.exit(1)
    else:
        print(f"Unknown step: {step_name}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_step.py <step_name>")
        sys.exit(1)
    
    step = sys.argv[1]
    run_step(step)
