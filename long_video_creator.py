from moviepy.editor import (VideoFileClip, AudioFileClip, CompositeAudioClip, 
                            ImageClip, concatenate_videoclips, CompositeVideoClip)
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
    print("\n📹 Initializing long-form video creation...")
    clips = []
    # Target horizontal (16:9) size for long-form videos (720p to reduce memory)
    TARGET_W = 1280
    TARGET_H = 720
    
    try:
        voiceover = AudioFileClip(voiceover_file).volumex(0.9)
        total_duration = voiceover.duration

        # Cap maximum duration for long-form videos to 3 minutes
        max_duration = 180  # seconds (3 minutes)
        if total_duration > max_duration:
            print(f"Note: Capping long-form video duration from {total_duration:.1f}s to {max_duration}s.")
            total_duration = max_duration
            voiceover = voiceover.subclip(0, max_duration) # Trim the voiceover clip
            
        duration_per_visual = math.ceil(total_duration / len(visual_files)) if visual_files else 0

        if duration_per_visual == 0:
            print("No visuals or zero duration. Cannot create video.")
            return

        total_clips = len(visual_files)
        for i, visual_file in enumerate(visual_files):
            progress_pct = int((i / total_clips) * 100)
            bar_length = 20
            filled = int((progress_pct / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"\r⏳ Processing clips: [{bar}] {progress_pct}% ({i}/{total_clips})", end="", flush=True)
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
            print("\n❌ No valid clips were created. Aborting video creation.")
            return

        bar = "█" * 20
        print(f"\r⏳ Processing clips: [{bar}] 100% ({len(clips)}/{total_clips})")
        print(f"✅ Processed {len(clips)} clips successfully!")
        assembled_duration = sum((c.duration or 0) for c in clips)
        print(f"📏 Visual coverage before alignment: {assembled_duration:.2f}s vs audio {total_duration:.2f}s")
        print("\n⏳ Concatenating clips (0%)...", end="", flush=True)
        # Simple concatenation for maximum stability; all clips are TARGET_W x TARGET_H
        final_clip = concatenate_videoclips(clips, method="chain")
        print("\r⏳ Concatenating clips (100%)...")
        print("✅ Clips concatenated!")
        # Ensure visual timeline fully covers voiceover to prevent black frames.
        if final_clip.duration < total_duration:
            print(f"🔁 Extending visuals by looping timeline from {final_clip.duration:.2f}s to {total_duration:.2f}s")
            final_clip = final_clip.fx(vfx.loop, duration=total_duration)
        else:
            print(f"✂️  Trimming visuals from {final_clip.duration:.2f}s to {total_duration:.2f}s")
            final_clip = final_clip.subclip(0, total_duration)

        # Force final clip size to target dimensions as a safety net
        try:
            final_clip = final_clip.resize((TARGET_W, TARGET_H))
        except Exception:
            pass
        
        # --- Captions have been removed for performance ---

        # --- Audio Composition ---
        print("\n⏳ Composing audio track (0%)...", end="", flush=True)
        audio_clips = [voiceover]
        print("\r⏳ Composing audio track (33%)...", end="", flush=True)
        if music_file:
            try:
                background_music = AudioFileClip(music_file).volumex(0.066) # Slightly louder background bed
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
        
        print("\r⏳ Composing audio track (66%)...", end="", flush=True)
        final_audio = CompositeAudioClip(audio_clips)
        final_clip.audio = final_audio
        print("\r⏳ Composing audio track (100%)...")
        print("✅ Audio composed!")

        # Write the final video file with optimized settings for YouTube
        print("\n⏳ Rendering final video (this may take several minutes)...")
        print("💡 Tip: MoviePy's progress bar below shows encoding progress\n")
        final_clip.write_videofile(output_file, 
                                  codec="libx264",
                                  audio_codec="aac",
                                  temp_audiofile='assets/temp-audio-long.m4a',
                                  remove_temp=True,
                                  fps=24,  # 24fps for faster processing
                                  preset='faster',  # Faster encoding speed
                                  bitrate="6000k",  # Slightly lower bitrate for faster encoding
                                  threads=8,  # Use more CPU threads
                                  logger='bar')  # Show progress bar
        
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
