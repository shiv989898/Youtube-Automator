from moviepy.editor import (VideoFileClip, AudioFileClip, CompositeAudioClip, 
                            ImageClip, concatenate_videoclips, ColorClip, CompositeVideoClip)
from moviepy.video.fx import all as vfx
import math
import random
import caption_generator

# Target 720x1280 output keeps Shorts-friendly 9:16 while lowering memory load
TARGET_WIDTH = 720
TARGET_HEIGHT = 1280
TARGET_FPS = 24

def create_video(visual_files, voiceover_file, output_file, music_file=None, script_text=None):
    """
    Combines visuals and audio into a final video. The duration of each visual
    is dynamically calculated based on the voiceover length.
    Optionally adds captions if script_text is provided.
    """
    print("Creating video...")
    clips = []
    
    try:
        voiceover = AudioFileClip(voiceover_file).volumex(0.9)
        total_duration = voiceover.duration
        duration_per_visual = math.ceil(total_duration / len(visual_files)) if visual_files else 0

        if duration_per_visual == 0:
            print("No visuals or zero duration. Cannot create video.")
            return

        for i, visual_file in enumerate(visual_files):
            clip = None
            try:
                if visual_file.lower().endswith(('.mp4', '.mov')):
                    clip = VideoFileClip(visual_file)
                    # Loop shorter clips to fit the required duration
                    if clip.duration < duration_per_visual:
                        clip = clip.fx(vfx.loop, duration=duration_per_visual)
                    else:
                        clip = clip.subclip(0, duration_per_visual)
                    
                    # Add random attractive effects to video clips
                    effect = random.choice(['zoom_in', 'zoom_out', 'pan_left', 'pan_right'])
                    if effect == 'zoom_in':
                        clip = clip.resize(lambda t: 1 + 0.15 * (t / duration_per_visual))
                    elif effect == 'zoom_out':
                        clip = clip.resize(lambda t: 1.15 - 0.15 * (t / duration_per_visual))
                
                elif visual_file.lower().endswith(('.jpg', '.png')):
                    # Add variety of zoom and pan effects to static images
                    clip = ImageClip(visual_file).set_duration(duration_per_visual)
                    
                    # Randomly choose an effect for variety
                    effect = random.choice(['zoom_in', 'zoom_out', 'zoom_in_out', 'pan_right', 'pan_left'])
                    
                    if effect == 'zoom_in':
                        # Smooth zoom in (Ken Burns effect)
                        clip = clip.resize(lambda t: 1 + 0.2 * (t / duration_per_visual))
                    elif effect == 'zoom_out':
                        # Smooth zoom out
                        clip = clip.resize(lambda t: 1.2 - 0.2 * (t / duration_per_visual))
                    elif effect == 'zoom_in_out':
                        # Zoom in then out (more dynamic)
                        def zoom_in_out(t):
                            progress = t / duration_per_visual
                            if progress < 0.5:
                                return 1 + 0.15 * (progress * 2)
                            else:
                                return 1.15 - 0.15 * ((progress - 0.5) * 2)
                        clip = clip.resize(zoom_in_out)
                    
                    clip = clip.set_position(('center', 'center'))

                if clip:
                    # Standardize clip size for YouTube Shorts (reduced resolution to save memory)
                    clip = clip.resize(height=TARGET_HEIGHT)
                    if clip.w > TARGET_WIDTH:
                        clip = clip.fx(vfx.crop, width=TARGET_WIDTH, x_center=clip.w / 2)
                    elif clip.w < TARGET_WIDTH:
                        background = ColorClip(size=(TARGET_WIDTH, TARGET_HEIGHT), color=(0, 0, 0)).set_duration(clip.duration)
                        clip = CompositeVideoClip([background, clip.set_position(('center', 'center'))], size=(TARGET_WIDTH, TARGET_HEIGHT))
                    clip = clip.set_position(('center', 'center')).set_duration(duration_per_visual)
                    
                    # Shorter fades to reduce overlapping frames in memory
                    if i > 0:  # Not the first clip
                        clip = clip.crossfadein(0.2)
                    if i < len(visual_files) - 1:  # Not the last clip
                        clip = clip.crossfadeout(0.2)
                    
                    clips.append(clip)

            except Exception as e:
                print(f"Warning: Could not process visual file {visual_file}: {e}")

        if not clips:
            print("No valid clips were created. Aborting video creation.")
            return

        # Concatenate with crossfade method for smooth transitions
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = final_clip.resize((TARGET_WIDTH, TARGET_HEIGHT))
        final_clip = final_clip.set_fps(TARGET_FPS)
        final_clip = final_clip.set_duration(total_duration)  # Ensure total duration matches voiceover
        
        # Skip vignette effect to reduce memory usage on high-resolution sources
        print("Note: Vignette effect disabled for stability")

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
                background_music = AudioFileClip(music_file).volumex(0.088) # Slightly louder music for energy
                # Loop or trim music to match the video duration
                if background_music.duration < total_duration:
                    background_music = background_music.fx(vfx.loop, duration=total_duration)
                else:
                    background_music = background_music.subclip(0, total_duration)
                
                # Add fade in/out to music for professional sound
                background_music = background_music.audio_fadein(1.0).audio_fadeout(1.0)
                audio_clips.append(background_music)
            except Exception as e:
                print(f"Warning: Could not process background music: {e}")
        
        final_audio = CompositeAudioClip(audio_clips)
        final_clip.audio = final_audio

        # Write the final video file with optimized settings for YouTube Shorts
        final_clip.write_videofile(output_file, 
                                  codec="libx264",
                                  audio_codec="aac",
                                  temp_audiofile='temp-audio.m4a',
                                  remove_temp=True,
                                  fps=TARGET_FPS,  # Reduced FPS for lower memory footprint
                                  preset='faster',  # Faster encoding speed
                                  bitrate="8000k",  # High bitrate for crisp quality
                                  threads=8,  # Use more CPU threads
                                  logger='bar')  # Progress bar keeps terminal responsive
        
        print(f"✨ Video created successfully with professional effects: {output_file}")

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
