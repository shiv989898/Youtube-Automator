import os
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

def main():
    """
    Main function to run the YouTube long-form video workflow.
    Creates horizontal format videos (1920x1080) for regular YouTube content.
    """
    load_dotenv()

    print("Finding trending topic for long-form video...")
    try:
        topic = topic_finder.get_trending_topic()
    except Exception as e:
        print(f"Could not get trending topic: {e}. Using fallback topic.")
        topic = "The fascinating science behind everyday phenomena"

    print(f"Topic for long-form video: {topic}")

    print("Generating long-form script...")
    script = script_generator_long.generate_long_script(topic)
    print(f"Script:\n{script}")

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

    print(f"Cleaned script for voiceover:\n{cleaned_script}")

    print("Generating voiceover...")
    voiceover.generate_voiceover("voiceover_long.mp3", cleaned_script)
    voiceover_file = "voiceover_long.mp3"
    print(f"Voiceover saved to {voiceover_file}")

    print("Finding background music...")
    music_file = music_finder.find_and_download_music("cinematic")
    if music_file:
        print(f"Background music saved to {music_file}")
    else:
        print("Could not find background music.")

    print("Gathering horizontal visuals for long-form video...")
    visual_files = visuals_long.get_visuals(topic, 12)  # Fewer but longer landscape clips
    print(f"Found {len(visual_files)} visuals.")

    if not visual_files:
        print("No visuals found. Exiting.")
        return

    print("Creating long-form video...")
    long_video_creator.create_long_video(visual_files, voiceover_file, "final_long_video.mp4", music_file, cleaned_script)
    print("Long-form video created successfully: final_long_video.mp4")

    # Generate a soft subtitle file (.srt) alongside the video for YouTube
    try:
        from moviepy.editor import AudioFileClip

        voice = AudioFileClip(voiceover_file)
        subtitle_generator_long.generate_srt_from_script(
            cleaned_script,
            voice.duration,
            "final_long_video.srt",
        )
        voice.close()
        print("Subtitle file generated: final_long_video.srt")
    except Exception as e:
        print(f"Warning: Could not generate .srt subtitles: {e}")

    print("Uploading to YouTube...")
    video_id = youtube_uploader_long.upload_long_video(
        "final_long_video.mp4",
        topic,
        cleaned_script
    )
    if video_id:
        print(f"Upload successful! Video ID: {video_id}")
        print(f"Watch at: https://youtube.com/watch?v={video_id}")
    else:
        print("Upload failed.")

if __name__ == "__main__":
    main()
