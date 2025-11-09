import os
from dotenv import load_dotenv
import topic_finder
import script_generator
import voiceover
import visuals
import video_creator
import youtube_uploader
import music_finder
import re

def main():
    """
    Main function to run the YouTube Shorts workflow.
    """
    load_dotenv()

    print("Finding trending topic...")
    try:
        topic = topic_finder.get_trending_topic()
    except Exception as e:
        print(f"Could not get trending topic: {e}. Using fallback topic.")
        topic = "The history of the internet"

    print(f"Trending topic: {topic}")

    print("Generating script...")
    script = script_generator.generate_script(topic)
    print(f"Script:\n{script}")

    # Clean the script for the voiceover
    narrator_lines = []
    for line in script.split('\n'):
        if line.strip().startswith('**Host:**'):
            cleaned_line = line.replace('**Host:**', '').strip()
            # Remove any remaining formatting like asterisks
            cleaned_line = re.sub(r'\*', '', cleaned_line)
            if cleaned_line:
                narrator_lines.append(cleaned_line)
    
    narrator_script = " ".join(narrator_lines)
    
    if not narrator_script:
        print("Could not extract any narrator lines from the script. Exiting.")
        return

    print(f"Cleaned script for voiceover:\n{narrator_script}")

    print("Generating voiceover...")
    voiceover_file = voiceover.create_voiceover(narrator_script, "voiceover.mp3")
    print(f"Voiceover saved to {voiceover_file}")

    print("Finding background music...")
    music_file = music_finder.find_and_download_music("upbeat")
    if music_file:
        print(f"Background music saved to {music_file}")
    else:
        print("Could not find background music.")

    print("Gathering visuals...")
    visual_files = visuals.get_visuals(topic, 5)
    print(f"Found {len(visual_files)} visuals.")

    if not visual_files:
        print("No visuals found. Exiting.")
        return

    print("Creating video...")
    video_creator.create_video(visual_files, voiceover_file, "final_video.mp4", music_file)
    print("Video created successfully: final_video.mp4")

    print("Uploading to YouTube...")
    video_id = youtube_uploader.upload_to_youtube(
        "final_video.mp4",
        f"YouTube Short about {topic}",
        f"A short video about {topic}. #shorts #{topic.replace(' ', '')}",
        ["shorts", topic]
    )
    if video_id:
        print(f"Upload successful! Video ID: {video_id}")
    else:
        print("Upload failed.")

if __name__ == "__main__":
    main()
