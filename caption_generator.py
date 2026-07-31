from moviepy.editor import ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import re
import textwrap
import numpy as np
import random

# Color schemes for visual variety and engagement (High Contrast TikTok styles)
CAPTION_COLORS = [
    {'main': '#FFFFFF', 'glow': '#000000', 'outline': '#000000', 'emphasis_color': '#FFFF00'}, # Yellow emphasis
    {'main': '#FFFFFF', 'glow': '#000000', 'outline': '#000000', 'emphasis_color': '#FF0000'}, # Red emphasis
    {'main': '#FFFFFF', 'glow': '#000000', 'outline': '#000000', 'emphasis_color': '#00FF00'}, # Green emphasis
]

# Keywords that should be highlighted for emphasis
EMPHASIS_WORDS = [
    'secret', 'truth', 'crazy', 'wild', 'insane', 'shocking', 'amazing',
    'never', 'always', 'everyone', 'nobody', 'first', 'only', 'best', 'worst',
    'free', 'now', 'today', 'new', 'real', 'actually', 'literally', 'seriously',
    'wait', 'stop', 'look', 'watch', 'listen', 'here', 'this', 'why', 'how',
    'money', 'rich', 'famous', 'viral', 'hack', 'trick', 'tip', 'fact',
    'dangerous', 'warning', 'important', 'crucial', 'must', 'need'
]

def add_captions_to_video(video_clip, script_text, voiceover_duration, scale=1.0):
    """
    Adds eye-catching animated captions optimized for retention.
    Features: word-by-word animation, emphasis on key words, varied colors.
    """
    print("🎬 Adding retention-optimized captions...")
    
    # Clean and split the script into short phrases (2-3 words for impact)
    words = script_text.split()
    phrases = []
    current_phrase = []
    
    for word in words:
        current_phrase.append(word)
        # Ultra-short phrases (1-2 words max) create hyper-engaging captions (TikTok style)
        if len(current_phrase) >= 1 or word.endswith(('.', '!', '?', ',')):
            phrases.append(' '.join(current_phrase))
            current_phrase = []
    
    if current_phrase:
        phrases.append(' '.join(current_phrase))
    
    # Calculate total characters to distribute time proportionally
    total_chars = sum(len(p) for p in phrases)
    if total_chars == 0:
        total_chars = 1
    
    caption_clips = []
    pop_timestamps = []
    current_time = 0
    
    # Select color scheme for this video (consistent throughout)
    color_scheme = random.choice(CAPTION_COLORS)
    
    for idx, phrase in enumerate(phrases):
        if not phrase.strip():
            continue
            
        # Calculate proportional time for this phrase
        phrase_chars = len(phrase)
        time_per_phrase = voiceover_duration * (phrase_chars / total_chars)
        
        try:
            # Scaled caption dimensions
            cap_width = max(200, min(1920, int(video_clip.w * 0.9 * scale)))
            cap_height = max(50, min(350, int(250 * scale)))
            
            # Check if phrase contains emphasis words
            has_emphasis = any(word.lower().strip('.,!?') in EMPHASIS_WORDS 
                             for word in phrase.split())
                             
            if has_emphasis:
                pop_timestamps.append(current_time)

            # Create caption image with emphasis styling
            caption_img = create_caption_image(
                phrase.strip(),
                width=cap_width,
                height=cap_height,
                color_scheme=color_scheme,
                emphasize=has_emphasis
            )

            # Convert to ImageClip
            img_clip = ImageClip(caption_img)
            
            # Position: slightly higher placement for better visibility
            position_y = int(video_clip.h * (0.72 if scale < 0.9 else 0.68))
            img_clip = img_clip.set_position(('center', position_y))
            img_clip = img_clip.set_start(current_time)
            
            dur = min(time_per_phrase, voiceover_duration - current_time)
            img_clip = img_clip.set_duration(dur)
            
            # Add dynamic "overshoot" animation for springy bounce
            pop_duration = min(0.12, dur / 2)
            if pop_duration > 0:
                def scale_func(t):
                    if t < pop_duration / 2:
                        progress = t / (pop_duration / 2)
                        return 0.7 + (0.45 * progress)  # 0.7 -> 1.15
                    elif t < pop_duration:
                        progress = (t - (pop_duration / 2)) / (pop_duration / 2)
                        return 1.15 - (0.15 * progress) # 1.15 -> 1.0
                    else:
                        return 1.0
                img_clip = img_clip.resize(scale_func)

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
        print(f"✨ Added {len(caption_clips)} engaging caption segments")
        return video_with_captions, pop_timestamps
    else:
        print("No captions to add")
        return video_clip, []


def create_caption_image(text, width=1080, height=350, color_scheme=None, emphasize=False):
    """
    Creates eye-catching caption image optimized for viewer retention.
    Features: dynamic colors, emphasis styling, bold readable fonts.
    Returns a numpy array suitable for MoviePy.
    """
    # Sanitize text: Keep only letters, numbers, spaces, and basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s?!.,\'-]', '', text)
    if not text.strip():
        text = " "
        
    if color_scheme is None:
        color_scheme = CAPTION_COLORS[0]
    
    # Create transparent image (RGBA, 8-bit per channel)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Larger font for emphasis words, slightly bigger base size for readability
    base_font_size = max(30, int(width * 0.135))
    font_size = int(base_font_size * 1.15) if emphasize else base_font_size
    
    def get_font(size):
        font_paths = [
            "impact.ttf", "arialbd.ttf", "arial.ttf",
            "C:\\Windows\\Fonts\\impact.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
        ]
        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
        print("Warning: No suitable TrueType font found. Falling back to default font (which is tiny).")
        return ImageFont.load_default()
                    
    font = get_font(font_size)
    
    # Force ALL text to uppercase for professional impact
    display_text = text.upper()
    
    # Wrap text to fit width
    approx_chars = max(5, int(width / (font_size * 0.55)))
    wrapped_text = textwrap.fill(display_text, width=approx_chars)
    
    # Get text bounding box and scale down if it overflows
    max_text_width = width - 40 # 20px padding on each side
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    
    while text_width > max_text_width and font_size > 10:
        font_size -= 2
        font = get_font(font_size)
        approx_chars = max(5, int(width / (font_size * 0.55)))
        wrapped_text = textwrap.fill(display_text, width=approx_chars)
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        
    text_height = bbox[3] - bbox[1]
    
    # Calculate position (center)
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 1. Draw 3D Extrusion Drop Shadow first (so it sits behind everything)
    shadow_depth = max(4, font_size // 12)
    shadow_color = '#000000'
    for d in range(1, shadow_depth + 1):
        # We draw a thick stroke for each step of the extrusion to ensure it's solid
        extrusion_thickness = max(2, font_size // 20)
        for adj_x in range(-extrusion_thickness, extrusion_thickness + 1):
            for adj_y in range(-extrusion_thickness, extrusion_thickness + 1):
                draw.text((x + d + adj_x, y + d + adj_y), wrapped_text, font=font, fill=shadow_color, align='center')
                
    # 2. Draw crisp outline around the main text
    outline_width = max(2, font_size // 20)
    outline_color = color_scheme['outline']
    for adj_x in range(-outline_width, outline_width + 1):
        for adj_y in range(-outline_width, outline_width + 1):
            if adj_x != 0 or adj_y != 0:
                draw.text((x + adj_x, y + adj_y), wrapped_text, font=font, fill=outline_color, align='center')

    # 3. Draw main text on top
    main_color = color_scheme.get('emphasis_color', '#FFFF00') if emphasize else color_scheme['main']
    draw.text((x, y), wrapped_text, font=font, fill=main_color, align='center')
    
    # Convert to numpy uint8 array with transparency (RGBA)
    arr = np.array(img, dtype=np.uint8)
    return arr

