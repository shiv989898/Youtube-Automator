from moviepy.editor import (VideoFileClip, AudioFileClip, CompositeAudioClip, 
                            ImageClip, concatenate_videoclips, CompositeVideoClip)
from moviepy.video.fx import all as vfx
import math
import random
import caption_generator

# Target 720x1280 output keeps Shorts-friendly 9:16 while lowering memory load
TARGET_WIDTH = 720
TARGET_HEIGHT = 1280
TARGET_FPS = 30  # Higher FPS for smoother motion (retention boost)

# Dynamic effects for visual engagement
VISUAL_EFFECTS = ['zoom_in', 'zoom_out', 'zoom_in_out', 'slow_zoom', 'pulse']


def _apply_visual_effect(clip, effect, duration):
    """Apply dynamic visual effect to clip for better engagement."""
    if effect == 'zoom_in':
        # Smooth zoom in (Ken Burns style)
        return clip.resize(lambda t: 1 + 0.18 * (t / duration))
    elif effect == 'zoom_out':
        # Smooth zoom out
        return clip.resize(lambda t: 1.18 - 0.18 * (t / duration))
    elif effect == 'zoom_in_out':
        # Zoom in then out (breathing effect)
        def zoom_func(t):
            progress = t / duration
            if progress < 0.5:
                return 1 + 0.12 * (progress * 2)
            else:
                return 1.12 - 0.12 * ((progress - 0.5) * 2)
        return clip.resize(zoom_func)
    elif effect == 'slow_zoom':
        # Very subtle slow zoom (professional look)
        return clip.resize(lambda t: 1 + 0.08 * (t / duration))
    elif effect == 'pulse':
        # Subtle pulse effect (attention-grabbing)
        import math as m
        def pulse_func(t):
            return 1 + 0.03 * m.sin(t * m.pi * 2)
        return clip.resize(pulse_func)
    return clip

def create_video(visual_files, voiceover_file, output_file, music_file=None, script_text=None):
    """
    Creates retention-optimized video with dynamic effects and pacing.
    Features: faster cuts, varied effects, higher FPS for smooth motion.
    """
    print("🎬 Creating retention-optimized video...")
    clips = []
    
    try:
        voiceover = AudioFileClip(voiceover_file).volumex(0.92)
        total_duration = voiceover.duration
        
        # Shorter clip durations = faster cuts = better retention
        # Max 2-2.5 seconds per visual keeps viewers hyper-engaged (TikTok style)
        max_visual_duration = 2.2
        duration_per_visual = min(max_visual_duration, 
                                  math.ceil(total_duration / len(visual_files))) if visual_files else 0

        if duration_per_visual == 0:
            print("No visuals or zero duration. Cannot create video.")
            return
        
        # Track which effects were used to ensure variety
        used_effects = []
        cut_timestamps = []
        current_time_for_cuts = 0

        for i, visual_file in enumerate(visual_files):
            clip = None
            try:
                # Select effect ensuring variety
                available_effects = [e for e in VISUAL_EFFECTS if e not in used_effects[-2:]]
                if not available_effects:
                    available_effects = VISUAL_EFFECTS
                effect = random.choice(available_effects)
                used_effects.append(effect)
                
                if visual_file.lower().endswith(('.mp4', '.mov')):
                    clip = VideoFileClip(visual_file)
                    # Loop shorter clips to fit the required duration
                    if clip.duration < duration_per_visual:
                        clip = clip.fx(vfx.loop, duration=duration_per_visual)
                    else:
                        # Start from a random point for variety
                        max_start = max(0, clip.duration - duration_per_visual)
                        start_time = random.uniform(0, max_start) if max_start > 0 else 0
                        clip = clip.subclip(start_time, start_time + duration_per_visual)
                    
                    # Apply dynamic effect
                    clip = _apply_visual_effect(clip, effect, duration_per_visual)
                
                elif visual_file.lower().endswith(('.jpg', '.png')):
                    clip = ImageClip(visual_file).set_duration(duration_per_visual)
                    clip = _apply_visual_effect(clip, effect, duration_per_visual)
                    clip = clip.set_position(('center', 'center'))

                if clip:
                    # Standardize clip size for YouTube Shorts
                    clip = clip.resize(height=TARGET_HEIGHT)
                    if clip.w > TARGET_WIDTH:
                        clip = clip.fx(vfx.crop, width=TARGET_WIDTH, x_center=clip.w / 2)
                    elif clip.w < TARGET_WIDTH:
                        # Fill side space with a dimmed backdrop from the same clip (instead of black bars).
                        backdrop = clip.resize(width=TARGET_WIDTH)
                        if backdrop.h < TARGET_HEIGHT:
                            backdrop = backdrop.resize(height=TARGET_HEIGHT)
                        if backdrop.w > TARGET_WIDTH:
                            backdrop = backdrop.fx(vfx.crop, width=TARGET_WIDTH, x_center=backdrop.w / 2)
                        if backdrop.h > TARGET_HEIGHT:
                            backdrop = backdrop.fx(vfx.crop, height=TARGET_HEIGHT, y_center=backdrop.h / 2)
                        backdrop = backdrop.fx(vfx.colorx, 0.42)
                        clip = CompositeVideoClip(
                            [backdrop.set_position(('center', 'center')), clip.set_position(('center', 'center'))],
                            size=(TARGET_WIDTH, TARGET_HEIGHT)
                        )
                    clip = clip.set_position(('center', 'center')).set_duration(duration_per_visual)
                    
                    # Hard cuts for high-energy pacing (no crossfades)
                    # (Removed crossfades here for better retention)
                    
                    clips.append(clip)
                    if i > 0:
                        cut_timestamps.append(current_time_for_cuts)
                    current_time_for_cuts += duration_per_visual

            except Exception as e:
                print(f"Warning: Could not process visual file {visual_file}: {e}")

        if not clips:
            print("No valid clips were created. Aborting video creation.")
            return

        # Concatenate with crossfade method for smooth transitions
        assembled_duration = sum((c.duration or 0) for c in clips)
        print(f"Visual coverage before alignment: {assembled_duration:.2f}s vs audio {total_duration:.2f}s")

        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = final_clip.resize((TARGET_WIDTH, TARGET_HEIGHT))
        final_clip = final_clip.set_fps(TARGET_FPS)
        # Ensure visual timeline fully covers the voiceover to avoid black-screen tails.
        if final_clip.duration < total_duration:
            print(f"Extending visuals by looping timeline from {final_clip.duration:.2f}s to {total_duration:.2f}s")
            final_clip = final_clip.fx(vfx.loop, duration=total_duration)
        else:
            print(f"Trimming visuals from {final_clip.duration:.2f}s to {total_duration:.2f}s")
            final_clip = final_clip.subclip(0, total_duration)
        
        # Skip vignette effect to reduce memory usage on high-resolution sources
        print("Note: Vignette effect disabled for stability")

        # --- Add Captions ---
        pop_timestamps = []
        if script_text:
            try:
                final_clip, pop_timestamps = caption_generator.add_captions_to_video(final_clip, script_text, total_duration)
            except Exception as e:
                print(f"Warning: Could not add captions: {e}")
                print("Continuing without captions...")

        # --- Audio Composition ---
        import music_finder
        import os
        pop_sfx_file, whoosh_sfx_file = music_finder.download_sfx()
        
        audio_clips = [voiceover]
        
        # Add whoosh on cuts
        if whoosh_sfx_file and os.path.exists(whoosh_sfx_file):
            for t in cut_timestamps:
                if t < total_duration:
                    whoosh_clip = AudioFileClip(whoosh_sfx_file).set_start(t).volumex(0.2)
                    audio_clips.append(whoosh_clip)
                    
        # Add pop on emphasis words
        if pop_sfx_file and os.path.exists(pop_sfx_file):
            for t in pop_timestamps:
                if t < total_duration:
                    pop_clip = AudioFileClip(pop_sfx_file).set_start(t).volumex(0.4)
                    audio_clips.append(pop_clip)

        if music_file:
            try:
                # Slightly louder background music for energy (but still below voice)
                background_music = AudioFileClip(music_file).volumex(0.12)
                # Loop or trim music to match the video duration
                if background_music.duration < total_duration:
                    background_music = background_music.fx(vfx.loop, duration=total_duration)
                else:
                    background_music = background_music.subclip(0, total_duration)
                
                # Add fade in/out to music for professional sound
                background_music = background_music.audio_fadein(0.8).audio_fadeout(0.8)
                audio_clips.append(background_music)
            except Exception as e:
                print(f"Warning: Could not process background music: {e}")
        
        final_audio = CompositeAudioClip(audio_clips)
        final_clip.audio = final_audio

        # Write the final video file with optimized settings for YouTube Shorts
        final_clip.write_videofile(output_file, 
                                  codec="libx264",
                                  audio_codec="aac",
                                  temp_audiofile='assets/temp-audio.m4a',
                                  remove_temp=True,
                                  fps=TARGET_FPS,  # Reduced FPS for lower memory footprint
                                  preset='faster',  # Faster encoding speed
                                  bitrate="8000k",  # High bitrate for crisp quality
                                  threads=8,  # Use more CPU threads
                                  logger='bar')  # Progress bar keeps terminal responsive
        
        print(f"✨ Retention-optimized video created: {output_file}")

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
