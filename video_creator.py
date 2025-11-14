from moviepy.editor import (VideoFileClip, AudioFileClip, CompositeAudioClip, 
                            ImageClip, concatenate_videoclips)
from moviepy.video.fx import all as vfx
import math
import caption_generator

def create_video(visual_files, voiceover_file, output_file, music_file=None, script_text=None):
    """
    Combines visuals and audio into a final video. The duration of each visual
    is dynamically calculated based on the voiceover length.
    Optionally adds captions if script_text is provided.
    """
    print("Creating video...")
    clips = []
    
    try:
        voiceover = AudioFileClip(voiceover_file)
        total_duration = voiceover.duration
        duration_per_visual = math.ceil(total_duration / len(visual_files)) if visual_files else 0

        if duration_per_visual == 0:
            print("No visuals or zero duration. Cannot create video.")
            return

        for visual_file in visual_files:
            clip = None
            try:
                if visual_file.lower().endswith(('.mp4', '.mov')):
                    clip = VideoFileClip(visual_file)
                    # Loop shorter clips to fit the required duration
                    if clip.duration < duration_per_visual:
                        clip = clip.fx(vfx.loop, duration=duration_per_visual)
                    else:
                        clip = clip.subclip(0, duration_per_visual)
                
                elif visual_file.lower().endswith(('.jpg', '.png')):
                    # Add a subtle zoom-in effect to static images
                    clip = ImageClip(visual_file).set_duration(duration_per_visual)
                    clip = clip.resize(lambda t: 1 + 0.02 * t).set_position(('center', 'center'))

                if clip:
                    # Standardize clip size for YouTube Shorts (1080x1920)
                    clip = clip.resize(height=1920).set_position(('center', 'center'))
                    clips.append(clip)

            except Exception as e:
                print(f"Warning: Could not process visual file {visual_file}: {e}")

        if not clips:
            print("No valid clips were created. Aborting video creation.")
            return

        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = final_clip.set_duration(total_duration) # Ensure total duration matches voiceover

        # --- Add Captions ---
        if script_text:
            try:
                final_clip = caption_generator.add_captions_to_video(final_clip, script_text, total_duration)
            except Exception as e:
                print(f"Warning: Could not add captions: {e}")
                print("Continuing without captions...")

        # --- Audio Composition ---
        audio_clips = [voiceover]
        if music_file:
            try:
                background_music = AudioFileClip(music_file).volumex(0.1) # Lower music volume
                # Loop or trim music to match the video duration
                if background_music.duration < total_duration:
                    background_music = background_music.fx(vfx.loop, duration=total_duration)
                else:
                    background_music = background_music.subclip(0, total_duration)
                audio_clips.append(background_music)
            except Exception as e:
                print(f"Warning: Could not process background music: {e}")
        
        final_audio = CompositeAudioClip(audio_clips)
        final_clip.audio = final_audio

        # Write the final video file
        final_clip.write_videofile(output_file, 
                                  codec="libx264", 
                                  audio_codec="aac", 
                                  temp_audiofile='temp-audio.m4a', 
                                  remove_temp=True)
        
        print(f"Video created successfully: {output_file}")

    except Exception as e:
        print(f"An error occurred during video creation: {e}")
    finally:
        # --- Memory Management: Clean up all clips ---
        for clip in clips:
            if isinstance(clip, (VideoFileClip, ImageClip)):
                clip.close()
        if 'voiceover' in locals() and voiceover:
            voiceover.close()
        if 'background_music' in locals() and background_music:
            background_music.close()
        if 'final_clip' in locals() and final_clip:
            final_clip.close()
