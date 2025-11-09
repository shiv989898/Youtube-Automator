from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, ImageClip, concatenate_videoclips
from PIL import Image
import numpy as np

def create_video(visual_files, voiceover_file, output_file, music_file=None, duration_per_visual=5):
    """
    Combines visuals and audio into a final video.
    """
    clips = []
    total_duration = 0

    for visual_file in visual_files:
        if visual_file.endswith(('.mp4', '.mov')):
            clip = VideoFileClip(visual_file).set_duration(duration_per_visual)
        elif visual_file.endswith(('.jpg', '.png')):
            # Simple zoom-in effect for images
            img = Image.open(visual_file)
            img_array = np.array(img)
            clip = ImageClip(img_array).set_duration(duration_per_visual)
            clip = clip.resize(lambda t: 1 + 0.05 * t) # Zoom in effect
            clip = clip.set_position(('center', 'center'))

        # Ensure all clips are the same size (e.g., 1080x1920 for Shorts)
        clip = clip.resize(width=1080, height=1920)
        clips.append(clip)
        total_duration += duration_per_visual

    if not clips:
        print("No valid visual files to create a video.")
        return

    final_clip = concatenate_videoclips(clips, method="compose")

    # Add audio
    voiceover = AudioFileClip(voiceover_file)
    
    # If voiceover is longer than visuals, loop the last visual
    if voiceover.duration > total_duration:
        final_clip = final_clip.fx(vfx.loop, duration=voiceover.duration)

    # If visuals are longer than voiceover, trim the video
    if total_duration > voiceover.duration:
        final_clip = final_clip.subclip(0, voiceover.duration)

    # Combine voiceover and background music
    if music_file:
        background_music = AudioFileClip(music_file).volumex(0.1) # Lower volume of music
        background_music = background_music.fx(vfx.loop, duration=final_clip.duration)
        final_audio = CompositeAudioClip([voiceover, background_music])
    else:
        final_audio = voiceover

    final_clip.audio = final_audio
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)
