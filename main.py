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
    voiceover.generate_voiceover("voiceover.mp3", cleaned_script)
    voiceover_file = "voiceover.mp3"
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
    video_creator.create_video(visual_files, voiceover_file, "final_video.mp4", music_file, cleaned_script)
    print("Video created successfully: final_video.mp4")

    print("Uploading to YouTube...")
    video_id = youtube_uploader.upload_to_youtube(
        "final_video.mp4",
        topic,
        cleaned_script
    )
    if video_id:
        print(f"Upload successful! Video ID: {video_id}")
        print(f"Watch at: https://youtube.com/shorts/{video_id}")
    else:
        print("Upload failed.")

if __name__ == "__main__":
    main()
