import os
import base64
from dotenv import load_dotenv
import topic_finder
import script_generator_long
import voiceover
import visuals_long
import long_video_creator
import subtitle_generator_long
import youtube_uploader_long
import music_finder
import re
import math

def setup_credentials():
    """Decode credentials from environment variables for Render.com deployment."""
    # Decode client_secret.json if provided as base64
    if os.getenv('CLIENT_SECRET_BASE64'):
        try:
            secret_content = base64.b64decode(os.getenv('CLIENT_SECRET_BASE64'))
            with open('client_secret.json', 'wb') as f:
                f.write(secret_content)
            print("✓ Decoded client_secret.json from environment")
        except Exception as e:
            print(f"Warning: Could not decode CLIENT_SECRET_BASE64: {e}")
    
    # Decode token.pickle if provided as base64
    if os.getenv('TOKEN_PICKLE_BASE64'):
        try:
            token_content = base64.b64decode(os.getenv('TOKEN_PICKLE_BASE64'))
            with open('token.pickle', 'wb') as f:
                f.write(token_content)
            print("✓ Decoded token.pickle from environment")
        except Exception as e:
            print(f"Warning: Could not decode TOKEN_PICKLE_BASE64: {e}")

def main():
    """
    Main function to run the YouTube long-form video workflow.
    Creates horizontal format videos (1920x1080) for regular YouTube content.
    """
    os.makedirs('assets', exist_ok=True)
    load_dotenv()
    setup_credentials()

    print("\n" + "="*60)
    print("🎬 LONG VIDEO GENERATION STARTED")
    print("="*60 + "\n")
    total_steps = 9
    
    print(f"[STEP 1/{total_steps}] 🔍 Finding trending topic for long-form video...")
    print("Progress: [██░░░░░░░░] 11%")
    try:
        topic = topic_finder.get_trending_topic()
        print("✅ Topic found successfully!")
    except Exception as e:
        print(f"⚠️  Could not get trending topic: {e}. Using fallback topic.")
        topic = "The fascinating science behind everyday phenomena"

    print(f"📌 Topic: {topic}\n")

    print(f"[STEP 2/{total_steps}] 📝 Generating long-form script...")
    print("Progress: [████░░░░░░] 22%")
    script = script_generator_long.generate_long_script(topic)
    print("✅ Script generated successfully!")
    print(f"📄 Script preview: {script[:100]}...\n")

    # Clean the script for the voiceover
    cleaned_script = re.sub(r"^(Here's|Here is).*?script.*?:\s*", '', script, flags=re.IGNORECASE)
    cleaned_script = re.sub(r'\*\*\(Scene:.*?\)\*\*|\(Scene:.*?\)','', cleaned_script)
    cleaned_script = re.sub(r'\*\*Host:\*\*|\*\*|\(.*?\)','', cleaned_script).strip()
    cleaned_script = re.sub(r'(---|\*\*)?(\n)?(Word Count:.*?|Estimated Speaking Time:.*?)(\n)?', '', cleaned_script, flags=re.IGNORECASE)
    cleaned_script = re.sub(r'---+', '', cleaned_script)
    cleaned_script = " ".join(cleaned_script.split())
    
    if not cleaned_script:
        print("Could not extract any narrator lines from the script. Exiting.")
        return

    print(f"📄 Cleaned script ready ({len(cleaned_script)} characters)\n")

    print(f"[STEP 3/{total_steps}] 🎙️  Generating voiceover...")
    print("Progress: [██████░░░░] 33%")
    voiceover.generate_voiceover("assets/voiceover_long.mp3", cleaned_script)
    voiceover_file = "assets/voiceover_long.mp3"
    print(f"✅ Voiceover saved to {voiceover_file}\n")
    
    # Calculate voiceover duration to optimize video downloads
    from moviepy.editor import AudioFileClip
    audio_clip = AudioFileClip(voiceover_file)
    voiceover_duration = int(audio_clip.duration)
    audio_clip.close()
    print(f"⏱️  Voiceover duration: {voiceover_duration}s ({voiceover_duration//60}m {voiceover_duration%60}s)\n")

    # Match visual count to narration length so long-form videos stay visually active.
    target_seconds_per_visual = 10
    min_visuals = 12
    max_visuals = 36
    visual_count = max(min_visuals, math.ceil(voiceover_duration / target_seconds_per_visual))
    visual_count = min(max_visuals, visual_count)
    print(f"🎞️  Target visual count: {visual_count} (~{target_seconds_per_visual}s each)\n")

    print(f"[STEP 4/{total_steps}] 🎵 Finding background music...")
    print("Progress: [████████░░] 44%")
    music_file = music_finder.find_and_download_music("cinematic")
    if music_file:
        print(f"✅ Background music saved to {music_file}\n")
    else:
        print("⚠️  Could not find background music.\n")

    print(f"[STEP 5/{total_steps}] 🎥 Gathering horizontal visuals for long-form video...")
    print("Progress: [██████████] 56%")
    # Pass target duration to avoid downloading unnecessarily long videos
    visual_files = visuals_long.get_visuals(
        topic,
        visual_count,
        target_duration=voiceover_duration,
        script_text=cleaned_script,
    )
    print(f"✅ Found {len(visual_files)} visuals\n")

    if not visual_files:
        print("❌ No visuals found. Exiting.")
        return

    print(f"[STEP 6/{total_steps}] 🎬 Creating long-form video (this may take a while)...")
    print("Progress: [████████████] 67%")
    print("⏳ Processing video clips, adding effects, and rendering...")
    long_video_creator.create_long_video(visual_files, voiceover_file, "assets/final_long_video.mp4", music_file, cleaned_script)
    print("\n✅ Long-form video created successfully: assets/final_long_video.mp4\n")

    # Generate a soft subtitle file (.srt) alongside the video for YouTube
    print(f"[STEP 7/{total_steps}] 📝 Generating subtitles...")
    print("Progress: [██████████████] 78%")
    try:
        from moviepy.editor import AudioFileClip

        voice = AudioFileClip(voiceover_file)
        subtitle_generator_long.generate_srt_from_script(
            cleaned_script,
            voice.duration,
            "assets/final_long_video.srt",
        )
        voice.close()
        print("✅ Subtitle file generated: assets/final_long_video.srt\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not generate .srt subtitles: {e}\n")

    print(f"[STEP 8/{total_steps}] ☁️  Uploading to YouTube...")
    print("Progress: [████████████████] 89%")
    print("⏳ This may take several minutes depending on your connection...")
    video_id = youtube_uploader_long.upload_long_video(
        "assets/final_long_video.mp4",
        topic,
        cleaned_script
    )
    if video_id:
        print(f"\n[STEP 9/{total_steps}] ✅ COMPLETE!")
        print("Progress: [██████████████████] 100%\n")
        print("="*60)
        print("🎉 SUCCESS! VIDEO GENERATION COMPLETE")
        print("="*60)
        print(f"✅ Upload successful! Video ID: {video_id}")
        print(f"🔗 Watch at: https://youtube.com/watch?v={video_id}")
        print("="*60 + "\n")
    else:
        print("\n❌ Upload failed.\n")

if __name__ == "__main__":
    main()
