from moviepy.editor import (VideoFileClip, AudioFileClip, CompositeAudioClip, 
                            ImageClip, TextClip, concatenate_videoclips, ColorClip, CompositeVideoClip)
from moviepy.video.fx import all as vfx
from moviepy.video.fx.all import crop
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
    # Target horizontal (16:9) size for long-form videos (720p to reduce memory)
    TARGET_W = 1280
    TARGET_H = 720
    
    try:
        voiceover = AudioFileClip(voiceover_file)
        total_duration = voiceover.duration

        # Cap maximum duration for long-form videos to avoid huge memory usage
        max_duration = 480  # seconds (8 minutes)
        if total_duration > max_duration:
            print(f"Note: Capping long-form video duration from {total_duration:.1f}s to {max_duration}s to reduce memory usage.")
            total_duration = max_duration
        duration_per_visual = math.ceil(total_duration / len(visual_files)) if visual_files else 0

        if duration_per_visual == 0:
            print("No visuals or zero duration. Cannot create video.")
            return

        for i, visual_file in enumerate(visual_files):
            clip = None
            try:
                if visual_file.lower().endswith(('.mp4', '.mov')):
                    clip = VideoFileClip(visual_file)

                    # Hard-crop every clip to 16:9 so final video is always
                    # properly horizontal with no vertical bars.
                    try:
                        target_ratio = TARGET_W / TARGET_H
                        clip_ratio = clip.w / clip.h
                        if abs(clip_ratio - target_ratio) > 0.01:
                            if clip_ratio < target_ratio:
                                # Too tall: crop top/bottom
                                new_h = int(clip.w / target_ratio)
                                if new_h < 1:
                                    new_h = clip.h
                                y1 = max((clip.h - new_h) // 2, 0)
                                y2 = min(y1 + new_h, clip.h)
                                clip = crop(clip, x1=0, x2=clip.w, y1=y1, y2=y2)
                            else:
                                # Too wide: crop sides
                                new_w = int(clip.h * target_ratio)
                                if new_w < 1:
                                    new_w = clip.w
                                x1 = max((clip.w - new_w) // 2, 0)
                                x2 = min(x1 + new_w, clip.w)
                                clip = crop(clip, x1=x1, x2=x2, y1=0, y2=clip.h)
                    except Exception:
                        pass
                    # Loop shorter clips to fit the required duration
                    if clip.duration < duration_per_visual:
                        clip = clip.fx(vfx.loop, duration=duration_per_visual)
                    else:
                        clip = clip.subclip(0, duration_per_visual)
                    
                    # Skip heavy zoom/pan effects for stability in long-form
                
                elif visual_file.lower().endswith(('.jpg', '.png')):
                    # Add variety of zoom and pan effects to static images
                    clip = ImageClip(visual_file).set_duration(duration_per_visual)
                    
                    # Keep images static for long-form to avoid memory spikes
                    
                    clip = clip.set_position(('center', 'center'))

                if clip:
                    # After cropping to 16:9, simply resize to target size and set duration
                    try:
                        clip = clip.resize((TARGET_W, TARGET_H)).set_duration(duration_per_visual)
                    except Exception:
                        clip = clip.set_duration(duration_per_visual)
                    
                    clips.append(clip)

            except Exception as e:
                print(f"Warning: Could not process visual file {visual_file}: {e}")

        if not clips:
            print("No valid clips were created. Aborting video creation.")
            return

        # Simple concatenation for maximum stability; all clips are TARGET_W x TARGET_H
        final_clip = concatenate_videoclips(clips, method="chain")
        final_clip = final_clip.set_duration(total_duration)  # Ensure total duration matches voiceover

        # Force final clip size to target dimensions as a safety net
        try:
            final_clip = final_clip.resize((TARGET_W, TARGET_H))
        except Exception:
            pass
        
        # --- Add lightweight hard subtitles using TextClip (no heavy images) ---
        if script_text:
            try:
                words = script_text.split()
                phrases = []
                current = []
                for w in words:
                    current.append(w)
                    if len(current) >= 7 or w.endswith((".", "!", "?")):
                        phrases.append(" ".join(current))
                        current = []
                if current:
                    phrases.append(" ".join(current))

                if phrases:
                    time_per = total_duration / len(phrases)
                    caption_clips = []
                    t = 0.0
                    for phrase in phrases:
                        txt = TextClip(
                            phrase,
                            fontsize=40,
                            color="white",
                            method="caption",
                            size=(int(TARGET_W * 0.9), None),
                            align="center",
                        )
                        txt = txt.set_position(("center", int(TARGET_H * 0.85)))
                        txt = txt.set_start(t).set_duration(min(time_per, total_duration - t))
                        caption_clips.append(txt)
                        t += time_per
                        if t >= total_duration:
                            break

                    if caption_clips:
                        final_clip = CompositeVideoClip([final_clip] + caption_clips)
                        print(f"✨ Added {len(caption_clips)} text caption segments (TextClip)")
            except Exception as e:
                print(f"Warning: Could not add text captions: {e}")
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
                      bitrate="6000k",  # Slightly lower bitrate for faster encoding
                                  threads=4,  # Use multiple threads for faster encoding
                                  logger=None)  # Reduce memory overhead from logging
        
        print(f"✨ Long-form video created successfully: {output_file}")

    except Exception as e:
        print(f"An error occurred during video creation: {e}")
    finally:
        # --- Memory Management: Clean up all clips ---
        for clip in clips:
            if isinstance(clip, (VideoFileClip, ImageClip)):
                clip.close()
        if 'voiceover' in locals() and voiceover:
            try:
                voiceover.close()
            except Exception:
                pass
        if 'background_music' in locals() and background_music:
            try:
                background_music.close()
            except Exception:
                pass
        if 'final_clip' in locals() and final_clip:
            try:
                final_clip.close()
            except Exception:
                pass
