import os
import sys
import json
import argparse
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

def parse_args():
    parser = argparse.ArgumentParser(description="YouTube Shorts Automation")
    parser.add_argument("--config", type=str, help="Path to JSON configuration file")
    parser.add_argument("--topic", type=str, help="Custom topic for the video")
    parser.add_argument("--script", type=str, help="Custom script text")
    parser.add_argument("--script-file", type=str, help="Path to text file containing script")
    parser.add_argument("--title", type=str, help="Custom YouTube video title")
    parser.add_argument("--description", type=str, help="Custom YouTube video description")
    parser.add_argument("--description-file", type=str, help="Path to text file containing description")
    parser.add_argument("--thumbnail", type=str, help="Path to custom thumbnail image file")
    parser.add_argument("--skip-upload", action="store_true", help="Generate video locally and skip YouTube upload")
    parser.add_argument("--ai-visuals", action="store_true", help="Generate visuals with Pollinations AI instead of stock footage")
    parser.add_argument("--strict-ai", action="store_true", help="Force waiting for 100% pure AI visuals even without API key")
    return parser.parse_args()

def main():
    """
    Main function to run the YouTube Shorts workflow.
    """
    args = parse_args()
    config = {}
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read config file {args.config}: {e}")

    # Determine parameter values (CLI flags override config file)
    custom_topic = args.topic or config.get("topic")
    custom_script = args.script or config.get("script")
    if args.script_file and os.path.exists(args.script_file):
        try:
            with open(args.script_file, 'r', encoding='utf-8') as f:
                custom_script = f.read()
        except Exception as e:
            print(f"Warning: Could not read script file {args.script_file}: {e}")

    custom_title = args.title or config.get("title")
    custom_description = args.description or config.get("description")
    if args.description_file and os.path.exists(args.description_file):
        try:
            with open(args.description_file, 'r', encoding='utf-8') as f:
                custom_description = f.read()
        except Exception as e:
            print(f"Warning: Could not read description file {args.description_file}: {e}")

    custom_thumbnail = args.thumbnail or config.get("thumbnail")
    skip_upload = args.skip_upload or config.get("skip_upload", False)
    use_ai_visuals = args.ai_visuals or config.get("ai_visuals", True)
    strict_ai = args.strict_ai or config.get("strict_ai", False)

    os.makedirs('assets', exist_ok=True)
    load_dotenv()
    setup_credentials()

    if custom_topic and custom_topic.strip():
        topic = custom_topic.strip()
        print(f"Using custom topic: {topic}")
    else:
        print("Finding trending topic...")
        try:
            topic = topic_finder.get_trending_topic()
        except Exception as e:
            print(f"Could not get trending topic: {e}. Using fallback topic.")
            topic = "The history of the internet"
        print(f"Trending topic: {topic}")

    if custom_script and custom_script.strip():
        script = custom_script.strip()
        print(f"Using custom script ({len(script)} chars).")
    else:
        print("Generating script...")
        script = script_generator.generate_script(topic)
        print(f"Script:\n{script}")

    # Clean the script for the voiceover by removing cues and extra formatting
    # Remove introductory lines like "Here's a 60-second YouTube Short script on..."
    cleaned_script = re.sub(r"^(Here's|Here is).*?script.*?:\s*", '', script, flags=re.IGNORECASE)
    # Remove scene descriptions in parentheses or double asterisks
    cleaned_script = re.sub(r'\*\*\(Scene:.*?\)\*\*|\(Scene:.*?\)','', cleaned_script)
    # Remove **Host:** markers and all parenthetical notes
    cleaned_script = re.sub(r'\*\*Host:\*\*|\*\*|\(.*?\)','', cleaned_script).strip()
    # Remove word count and timing information (e.g., "Word Count: 78 words", "Estimated Speaking Time: 30-35 seconds")
    cleaned_script = re.sub(r'(---|\*\*)?(\n)?(Word Count:.*?|Estimated Speaking Time:.*?)(\n)?', '', cleaned_script, flags=re.IGNORECASE)
    # Remove any triple dashes or separators
    cleaned_script = re.sub(r'---+', '', cleaned_script)
    # Remove any extra newlines or whitespace
    cleaned_script = " ".join(cleaned_script.split())
    
    if not cleaned_script:
        print("Could not extract any narrator lines from the script. Exiting.")
        return

    print(f"Cleaned script for voiceover:\n{cleaned_script}")

    print("Generating voiceover...")
    voiceover.generate_voiceover("assets/voiceover.mp3", cleaned_script)
    voiceover_file = "assets/voiceover.mp3"
    print(f"Voiceover saved to {voiceover_file}")
    
    # Calculate voiceover duration to optimize video downloads
    from moviepy.editor import AudioFileClip
    audio_clip = AudioFileClip(voiceover_file)
    voiceover_duration = int(audio_clip.duration)
    audio_clip.close()
    print(f"Voiceover duration: {voiceover_duration}s")

    # Adapt visual count to narration length for smoother pacing and less looping.
    target_seconds_per_visual = 3
    min_visuals = 6
    max_visuals = 16
    visual_count = max(min_visuals, math.ceil(voiceover_duration / target_seconds_per_visual))
    visual_count = min(max_visuals, visual_count)
    print(f"Target visual count: {visual_count} (~{target_seconds_per_visual}s per cut)")

    print("Finding background music...")
    music_file = music_finder.find_and_download_music("upbeat")
    if music_file:
        print(f"Background music saved to {music_file}")
    else:
        print("Could not find background music.")

    print("Gathering visuals...")
    visual_files = []
    if use_ai_visuals:
        try:
            import pollinations_visuals
            visual_files = pollinations_visuals.get_ai_visuals(
                topic,
                visual_count,
                is_vertical=True,
                script_text=cleaned_script,
                strict_ai=strict_ai
            )
        except Exception as e:
            print(f"Notice: AI visual generation fallback ({e}). Using stock footage...")

    if not visual_files:
        visual_files = visuals.get_visuals(
            topic,
            visual_count,
            target_duration=voiceover_duration,
            script_text=cleaned_script,
        )
    print(f"Found {len(visual_files)} visuals.")

    if not visual_files:
        print("No visuals found. Exiting.")
        return

    print("Creating video...")
    video_creator.create_video(visual_files, voiceover_file, "assets/final_video.mp4", music_file, cleaned_script)
    print("Video created successfully: assets/final_video.mp4")

    # Generate custom AI thumbnail with Pollinations if none provided
    if not custom_thumbnail or not os.path.exists(custom_thumbnail):
        try:
            import thumbnail_generator
            print("Creating custom AI thumbnail with Pollinations...")
            custom_thumbnail = thumbnail_generator.create_ai_thumbnail(
                topic,
                output_path="assets/thumbnail_shorts.jpg",
                custom_headline=custom_title,
                is_vertical=False
            )
        except Exception as e:
            print(f"Notice: Automatic thumbnail creation skipped ({e})")

    if skip_upload:
        print("Video generated successfully: assets/final_video.mp4")
        if custom_thumbnail and os.path.exists(custom_thumbnail):
            print(f"Thumbnail ready: {custom_thumbnail}")
        print("Skipping YouTube upload (--skip-upload enabled).")
        return

    print("Uploading to YouTube...")
    video_id = youtube_uploader.upload_to_youtube(
        "assets/final_video.mp4",
        topic,
        cleaned_script,
        custom_title=custom_title,
        custom_description=custom_description,
        thumbnail_file=custom_thumbnail
    )
    if video_id:
        print(f"Upload successful! Video ID: {video_id}")
        print(f"Watch at: https://youtube.com/shorts/{video_id}")
    else:
        print("Upload failed.")

if __name__ == "__main__":
    main()
