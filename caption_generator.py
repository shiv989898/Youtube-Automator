from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import re
import textwrap
import numpy as np

def add_captions_to_video(video_clip, script_text, voiceover_duration, scale=1.0):
    """
    Adds attractive animated captions to the video clip using PIL/Pillow.
    Captions appear in the lower-middle section with large, bold text.
    """
    print("Adding attractive captions to video...")
    
    # Clean and split the script into short phrases (2-3 words each for impact)
    words = script_text.split()
    phrases = []
    current_phrase = []
    
    for word in words:
        current_phrase.append(word)
        # Shorter phrases (2-3 words) for better emphasis and readability
        if len(current_phrase) >= 3 or word.endswith(('.', '!', '?', ',')):
            phrases.append(' '.join(current_phrase))
            current_phrase = []
    
    if current_phrase:
        phrases.append(' '.join(current_phrase))
    
    # Calculate timing for each phrase
    time_per_phrase = voiceover_duration / len(phrases) if phrases else 0
    
    caption_clips = []
    current_time = 0
    
    for phrase in phrases:
        if not phrase.strip():
            continue
        try:
            # Scaled caption dimensions to reduce memory usage for long-form videos
            # Slightly reduced height for long-format stability
            cap_width = max(200, min(1920, int(video_clip.w * 0.9 * scale)))
            cap_height = max(50, min(200, int(160 * scale)))

            # Create caption image
            caption_img = create_caption_image(
                phrase.strip(),
                width=cap_width,
                height=cap_height
            )

            # Convert to ImageClip (Pillow->numpy uint8 helps keep memory down)
            img_clip = ImageClip(caption_img)
            # Position lower-middle; use slightly lower placement for long-form when scaled
            position_y = int(video_clip.h * (0.78 if scale < 0.9 else 0.7))
            img_clip = img_clip.set_position(('center', position_y))
            img_clip = img_clip.set_start(current_time)
            img_clip = img_clip.set_duration(min(time_per_phrase, voiceover_duration - current_time))

            caption_clips.append(img_clip)
            current_time += time_per_phrase

            if current_time >= voiceover_duration:
                break
        except Exception as e:
            print(f"Warning: Could not create caption for phrase '{phrase[:30]}...': {e}")
            continue
    
    # Composite video with captions
    if caption_clips:
        video_with_captions = CompositeVideoClip([video_clip] + caption_clips)
        print(f"✨ Added {len(caption_clips)} attractive caption segments")
        return video_with_captions
    else:
        print("No captions to add")
        return video_clip


def create_caption_image(text, width=1080, height=350):
    """
    Creates an attractive caption image with large, bold text using PIL/Pillow.
    Features: bigger font, thicker outline, yellow highlight effect.
    Returns a numpy array suitable for MoviePy.
    """
    # Create transparent image (RGBA, 8-bit per channel)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Determine font size relative to width for better scaling across sizes
    font_size = max(18, int(width * 0.085))
    try:
        # Try to use Arial Black or Bold for maximum impact (Windows)
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # Try common Windows fonts
                font = ImageFont.truetype("impact.ttf", font_size)
            except:
                try:
                    # Linux/Ubuntu fonts (for GitHub Actions)
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
                    except:
                        # Fallback to default (will still be 350px if possible)
                        font = ImageFont.load_default()
    
    # Wrap text to fit width; approximate characters per line by width/font_size
    approx_chars = max(10, int(width / (font_size * 0.6)))
    wrapped_text = textwrap.fill(text, width=approx_chars)
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position (center)
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw a lighter outline for readability (reduced loops to cut CPU/memory)
    outline_width = max(2, font_size // 20)
    for adj in [(-outline_width, 0), (outline_width, 0), (0, -outline_width), (0, outline_width), (-outline_width, -outline_width), (outline_width, outline_width)]:
        draw.text((x + adj[0], y + adj[1]), wrapped_text, font=font, fill='black', align='center')

    # Draw subtle yellow glow using fewer offsets
    glow_width = max(1, font_size // 40)
    for adj in [(-glow_width, 0), (glow_width, 0), (0, -glow_width), (0, glow_width)]:
        draw.text((x + adj[0], y + adj[1]), wrapped_text, font=font, fill='#FFD700', align='center')
    
    # Draw main text (bright white for maximum contrast)
    draw.text((x, y), wrapped_text, font=font, fill='white', align='center')
    
    # Convert to numpy uint8 array with transparency (RGBA)
    arr = np.array(img, dtype=np.uint8)
    return arr

