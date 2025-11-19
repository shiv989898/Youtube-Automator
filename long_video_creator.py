from moviepy.editor import (VideoFileClip, AudioFileClip, CompositeAudioClip, 
                            ImageClip, concatenate_videoclips, ColorClip, CompositeVideoClip)
from moviepy.video.fx import all as vfx
import math
import random
import caption_generator  # Using same caption generator as shorts

def create_long_video(visual_files, voiceover_file, output_file, music_file=None, script_text=None):
    """
    Creates a long-form horizontal video (1920x1080) for regular YouTube content.
    Similar to shorts but optimized for longer viewing and horizontal format.
    """
    print("Creating long-form horizontal video...")
    clips = []
    
    try:
        voiceover = AudioFileClip(voiceover_file)
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
                    
                    # Add subtle professional effects to video clips
                    effect = random.choice(['zoom_in', 'zoom_out', 'pan_left', 'pan_right', 'none'])
                    if effect == 'zoom_in':
                        clip = clip.resize(lambda t: 1 + 0.1 * (t / duration_per_visual))
                    elif effect == 'zoom_out':
                        clip = clip.resize(lambda t: 1.1 - 0.1 * (t / duration_per_visual))
                
                elif visual_file.lower().endswith(('.jpg', '.png')):
                    # Add variety of zoom and pan effects to static images
                    clip = ImageClip(visual_file).set_duration(duration_per_visual)
                    
                    # Randomly choose an effect for variety
                    effect = random.choice(['zoom_in', 'zoom_out', 'pan_right', 'pan_left', 'none'])
                    
                    if effect == 'zoom_in':
                        # Smooth zoom in (Ken Burns effect)
                        clip = clip.resize(lambda t: 1 + 0.15 * (t / duration_per_visual))
                    elif effect == 'zoom_out':
                        # Smooth zoom out
                        clip = clip.resize(lambda t: 1.15 - 0.15 * (t / duration_per_visual))
                    
                    clip = clip.set_position(('center', 'center'))

                if clip:
                    # Standardize clip size for YouTube horizontal format (1920x1080)
                    clip = clip.resize(width=1920).set_position(('center', 'center'))
                    
                    # Add subtle fade transitions between clips for smoother viewing
                    if i > 0:  # Not the first clip
                        clip = clip.crossfadein(0.5)
                    if i < len(visual_files) - 1:  # Not the last clip
                        clip = clip.crossfadeout(0.5)
                    
                    clips.append(clip)

            except Exception as e:
                print(f"Warning: Could not process visual file {visual_file}: {e}")

        if not clips:
            print("No valid clips were created. Aborting video creation.")
            return

        # Concatenate with crossfade method for smooth transitions
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = final_clip.set_duration(total_duration) # Ensure total duration matches voiceover
        
        # Add subtle vignette effect for professional look
        try:
            w, h = final_clip.size
            vignette = ColorClip(size=(w, h), color=(0, 0, 0))
            vignette = vignette.set_duration(total_duration)
            vignette = vignette.set_opacity(0)
            
            def vignette_mask(get_frame, t):
                import numpy as np
                frame = get_frame(t)
                h, w = frame.shape[:2]
                # Create radial gradient for vignette
                Y, X = np.ogrid[:h, :w]
                center_y, center_x = h // 2, w // 2
                dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
                max_dist = np.sqrt(center_x**2 + center_y**2)
                mask = 1 - (dist_from_center / max_dist) * 0.25  # 25% darkening at edges (more subtle)
                mask = np.clip(mask, 0.75, 1.0)  # Keep it subtle
                return (frame * mask[:, :, np.newaxis]).astype('uint8')
            
            final_clip = final_clip.fl(vignette_mask)
        except Exception as e:
            print(f"Note: Vignette effect skipped: {e}")

        # Long-form videos don't need captions (viewers can use YouTube's auto-captions)
        # Skipping caption generation for cleaner professional look
        
        # --- Add Captions (same style as Shorts) ---
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
                background_music = AudioFileClip(music_file).volumex(0.06) # Lower music volume for long-form content
                # Loop or trim music to match the video duration
                if background_music.duration < total_duration:
                    background_music = background_music.fx(vfx.loop, duration=total_duration)
                else:
                    background_music = background_music.subclip(0, total_duration)
                
                # Add fade in/out to music for professional sound
                background_music = background_music.audio_fadein(2.0).audio_fadeout(2.0)
                audio_clips.append(background_music)
            except Exception as e:
                print(f"Warning: Could not process background music: {e}")
        
        final_audio = CompositeAudioClip(audio_clips)
        final_clip.audio = final_audio

        # Write the final video file with optimized settings for YouTube
        final_clip.write_videofile(output_file, 
                                  codec="libx264",
                                  audio_codec="aac",
                                  temp_audiofile='temp-audio-long.m4a',
                                  remove_temp=True,
                                  fps=30,  # Smooth 30fps for better quality
                                  preset='medium',  # Balance between quality and encoding speed
                                  bitrate="10000k")  # Higher bitrate for long-form content
        
        print(f"✨ Long-form video created successfully: {output_file}")

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
