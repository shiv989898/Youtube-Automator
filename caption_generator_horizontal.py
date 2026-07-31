from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import re
import textwrap
import numpy as np

def add_captions_to_video(video_clip, script_text, voiceover_duration):
    """
    Adds attractive animated captions to horizontal videos (1920x1080).
    Captions appear at the bottom with professional styling.
    """
    print("Adding captions to horizontal video...")
    
    # Clean and split the script into short phrases (3-5 words each for readability)
    words = script_text.split()
    phrases = []
    current_phrase = []
    
    for word in words:
        current_phrase.append(word)
        # Longer phrases for horizontal format (3-5 words)
        if len(current_phrase) >= 4 or word.endswith(('.', '!', '?', ',')):
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
            # Create caption image for horizontal format
            caption_img = create_caption_image(
                phrase.strip(),
                width=video_clip.w,
                height=300  # Smaller height for horizontal format
            )
            
            # Convert to ImageClip
            img_clip = ImageClip(caption_img)
            # Position at bottom of screen (85% down)
            img_clip = img_clip.set_position(('center', int(video_clip.h * 0.85)))
            img_clip = img_clip.set_start(current_time).set_duration(time_per_phrase)
            
            caption_clips.append(img_clip)
            current_time += time_per_phrase
        except Exception as e:
            print(f"Warning: Could not create caption for phrase '{phrase[:30]}...': {e}")
            continue
    
    # Composite video with captions
    if caption_clips:
        video_with_captions = CompositeVideoClip([video_clip] + caption_clips)
        print(f"✨ Added {len(caption_clips)} caption segments to horizontal video")
        return video_with_captions
    else:
        print("No captions to add")
        return video_clip


def create_caption_image(text, width=1920, height=300):
    """
    Creates an attractive caption image for horizontal videos using PIL/Pillow.
    Features: professional font, outline, positioned for 16:9 format.
    Returns a numpy array suitable for MoviePy.
    """
    # Create transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Use professional font size for horizontal format
    font_size = 100  # Reduced font size for better viewing
    font_paths = [
        "arialbd.ttf", "arial.ttf", "impact.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\impact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
    ]
    font = None
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except:
            continue
    if font is None:
        print("Warning: No suitable TrueType font found. Falling back to default font (which is tiny).")
        font = ImageFont.load_default()
    
    # Wrap text to fit width (more characters per line for horizontal format)
    wrapped_text = textwrap.fill(text, width=30)  # More characters for 1920px width
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text with thick black outline for readability
    outline_width = 6  # Thicker outline for visibility
    
    # Draw outline
    for adj_x in range(-outline_width, outline_width + 1):
        for adj_y in range(-outline_width, outline_width + 1):
            if adj_x != 0 or adj_y != 0:
                draw.text((x + adj_x, y + adj_y), wrapped_text, font=font, fill=(0, 0, 0, 255))
    
    # Draw main text in white
    draw.text((x, y), wrapped_text, font=font, fill=(255, 255, 255, 255))
    
    # Add subtle glow effect
    glow_width = 3
    for adj_x in range(-glow_width, glow_width + 1):
        for adj_y in range(-glow_width, glow_width + 1):
            if adj_x != 0 or adj_y != 0:
                distance = (adj_x**2 + adj_y**2)**0.5
                if distance <= glow_width:
                    alpha = int(50 * (1 - distance / glow_width))
                    draw.text((x + adj_x, y + adj_y), wrapped_text, font=font, fill=(255, 255, 255, alpha))
    
    # Convert PIL Image to numpy array for MoviePy
    return np.array(img)
