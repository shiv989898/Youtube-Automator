import os
import sys
import re
import urllib.parse
import time
import requests
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
if POLLINATIONS_API_KEY:
    HEADERS["Authorization"] = f"Bearer {POLLINATIONS_API_KEY}"


def _get_font(size: int = 56):
    """Finds a robust, bold font available on the system."""
    font_candidates = [
        "arialbd.ttf",       # Arial Bold (Windows standard)
        "segoeuib.ttf",      # Segoe UI Bold
        "impact.ttf",        # Classic YouTube thumbnail font
        "tahomabd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc"
    ]
    for font_path in font_candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_text_with_shadow(draw, position, text, font, fill_color=(255, 255, 255), shadow_color=(0, 0, 0), shadow_offset=4):
    """Draws text with heavy, legible drop shadow for YouTube thumbnails."""
    x, y = position
    # Draw shadow in 8 directions for a solid outline effect
    for dx in range(-shadow_offset, shadow_offset + 1, 2):
        for dy in range(-shadow_offset, shadow_offset + 1, 2):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
    # Draw primary text
    draw.text((x, y), text, font=font, fill=fill_color)


def create_ai_thumbnail(
    topic: str,
    output_path: str = "assets/thumbnail.jpg",
    custom_headline: Optional[str] = None,
    is_vertical: bool = False
) -> str:
    """
    Generates a high-impact AI thumbnail with Pollinations and overlays
    high-contrast, click-worthy YouTube typography.
    100% free with no API keys.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    width = 720 if is_vertical else 1280
    height = 1280 if is_vertical else 720

    # Build image prompt for Pollinations
    clean_topic = re.sub(r'^(the|a|an)\s+', '', topic, flags=re.IGNORECASE).strip()
    image_prompt = (
        f"extreme close up epic cinematic 8k shot of {clean_topic}, "
        f"advanced artificial intelligence future technology, glowing cyan and gold neon accents, "
        f"high tech laboratory background, dramatic volumetric lighting, photorealistic, 3D render artstation"
    )

    encoded = urllib.parse.quote(image_prompt[:250])
    seed = int(time.time() * 1000) % 1000000
    url = f"{POLLINATIONS_BASE_URL}{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

    print(f"Generating AI thumbnail image with Pollinations ({width}x{height})...")
    raw_img_path = output_path.replace(".jpg", "_raw.jpg")

    downloaded = False
    for attempt in range(2):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=40)
            if resp.status_code == 200 and len(resp.content) > 5000:
                with open(raw_img_path, "wb") as f:
                    f.write(resp.content)
                downloaded = True
                break
            elif resp.status_code == 402:
                try:
                    data = resp.json()
                    err_msg = data.get("error", {}).get("message", "")
                    match = re.search(r"Retry after (\d+)s", err_msg)
                    if match:
                        wait_sec = min(int(match.group(1)) + 2, 45)
                        print(f"Pollinations rate limit: waiting {wait_sec}s for thumbnail...")
                        time.sleep(wait_sec)
                        continue
                except Exception:
                    time.sleep(5)
            else:
                time.sleep(3)
        except Exception as e:
            print(f"Warning: Attempt {attempt+1} downloading thumbnail failed: {e}")
            time.sleep(3)

    # Open image or create blank fallback
    if downloaded and os.path.exists(raw_img_path):
        img = Image.open(raw_img_path).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
    else:
        print("Using gradient backdrop for thumbnail...")
        img = Image.new("RGBA", (width, height), color=(15, 18, 28))

    # Determine punchy thumbnail text
    if custom_headline and custom_headline.strip():
        headline = custom_headline.strip().upper()
    else:
        # Create a short, punchy 3-5 word headline from the topic
        words = clean_topic.split()
        if len(words) > 5:
            headline = " ".join(words[:4]).upper() + "!"
        else:
            headline = clean_topic.upper() + "!"

    # Add a subtle dark gradient overlay at the top/bottom so text pops
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Dark gradient banner in bottom third
    banner_height = int(height * 0.35)
    for y in range(banner_height):
        alpha = int((y / banner_height) * 190)
        overlay_draw.line([(0, height - banner_height + y), (width, height - banner_height + y)], fill=(0, 0, 0, alpha))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Render typography
    font_size = 58 if not is_vertical else 50
    font = _get_font(font_size)

    # Wrap text if long
    max_chars_per_line = 24 if not is_vertical else 16
    lines = []
    current_line = []
    for word in headline.split():
        if len(" ".join(current_line + [word])) <= max_chars_per_line:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    # Position text near the bottom
    line_height = font_size + 14
    total_text_height = len(lines) * line_height
    start_y = height - total_text_height - int(height * 0.08)

    colors = [(255, 220, 0), (255, 255, 255), (0, 240, 255)]  # Gold, White, Cyan

    for idx, line in enumerate(lines):
        line_color = colors[idx % len(colors)]
        # Center horizontally
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = max(24, (width - text_w) // 2)
        y = start_y + (idx * line_height)
        _draw_text_with_shadow(draw, (x, y), line, font, fill_color=line_color, shadow_offset=5)

    # Save final thumbnail as RGB JPEG
    final_thumbnail = img.convert("RGB")
    final_thumbnail.save(output_path, "JPEG", quality=95)

    # Clean up temporary raw image
    if os.path.exists(raw_img_path):
        try:
            os.remove(raw_img_path)
        except Exception:
            pass

    print(f"Thumbnail saved successfully to: {output_path}")
    return os.path.abspath(output_path)


if __name__ == "__main__":
    thumb = create_ai_thumbnail(
        topic="OpenAI GPT 6.1 Terra Released",
        output_path="assets/test_thumb.jpg",
        custom_headline="GPT 6.1 TERRA RELEASED!"
    )
    print("Thumbnail generated at:", thumb)
