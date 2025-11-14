from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import re
import textwrap
import numpy as np

def add_captions_to_video(video_clip, script_text, voiceover_duration):
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
            # Create larger, more attractive caption image
            caption_img = create_caption_image(
                phrase.strip(),
                width=video_clip.w,
                height=300  # Increased height for bigger captions
            )
            
            # Convert to ImageClip
            img_clip = ImageClip(caption_img)
            # Position in lower-middle section (about 60% down the screen)
            img_clip = img_clip.set_position(('center', int(video_clip.h * 0.6)))
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


def create_caption_image(text, width=1080, height=300):
    """
    Creates an attractive caption image with large, bold text using PIL/Pillow.
    Features: bigger font, thicker outline, yellow highlight effect.
    Returns a numpy array suitable for MoviePy.
    """
    # Create transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Use much larger font for impact
    font_size = 120  # Increased from 70 to 120 for bigger captions
    try:
        # Try to use Arial Black or Bold for maximum impact
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # Try common Windows fonts
                font = ImageFont.truetype("impact.ttf", font_size)
            except:
                font = ImageFont.load_default()
    
    # Wrap text to fit width (fewer characters per line due to larger font)
    wrapped_text = textwrap.fill(text, width=15)
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position (center)
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw thick black outline for better readability
    outline_width = 12  # Increased from 8 to 12 for thicker outline
    for adj_x in range(-outline_width, outline_width + 1):
        for adj_y in range(-outline_width, outline_width + 1):
            draw.text((x + adj_x, y + adj_y), wrapped_text, font=font, fill='black', align='center')
    
    # Draw yellow highlight/glow effect (optional - makes text pop)
    glow_width = 6
    for adj_x in range(-glow_width, glow_width + 1):
        for adj_y in range(-glow_width, glow_width + 1):
            if abs(adj_x) > outline_width - 3 or abs(adj_y) > outline_width - 3:
                draw.text((x + adj_x, y + adj_y), wrapped_text, font=font, fill='#FFD700', align='center')
    
    # Draw main text (bright white for maximum contrast)
    draw.text((x, y), wrapped_text, font=font, fill='white', align='center')
    
    # Convert to numpy array with transparency (RGBA to keep transparent background)
    return np.array(img)

