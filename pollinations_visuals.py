import os
import sys
import re
import urllib.parse
import time
import requests
from typing import List, Optional

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Pollinations AI image endpoint (100% free, no API key required)
POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)


def generate_scene_prompts(topic: str, script_text: str, count: int) -> List[str]:
    """
    Splits the script into segments and generates tailored visual prompts
    specifically matching each part of the narration.
    """
    sentences = [s.strip() for s in re.split(r'[.!?]+', script_text) if len(s.strip()) > 15]
    if not sentences:
        sentences = [topic]

    prompts = []
    # If we have more visuals than sentences, duplicate or create topic variations
    for i in range(count):
        sentence_idx = i % len(sentences)
        sentence = sentences[sentence_idx]

        # Clean sentence of dialogue markers
        clean_sentence = re.sub(r'^(Host:|Narrator:)', '', sentence, flags=re.IGNORECASE).strip()
        # Extract core nouns and descriptors
        words = [w for w in clean_sentence.split() if len(w) > 3][:8]
        key_phrase = " ".join(words) if words else topic

        # Build highly descriptive, photorealistic prompt tailored to modern AI news
        prompt = (
            f"photorealistic 8k cinematic shot of {key_phrase}, "
            f"related to {topic}, advanced artificial intelligence technology, "
            f"futuristic glowing elements, deep depth of field, dramatic lighting, high tech lab"
        )
        prompts.append(prompt)

    return prompts


def download_pollinations_image(
    prompt: str,
    output_path: str,
    width: int = 720,
    height: int = 1280,
    model: str = "flux",
    retries: int = 2
) -> bool:
    """
    Downloads a single AI-generated image from Pollinations.ai.
    Handles free-tier rate limits gracefully.
    """
    clean_prompt = prompt[:200]
    encoded_prompt = urllib.parse.quote(clean_prompt)
    seed = int(time.time() * 1000) % 1000000
    url = f"{POLLINATIONS_BASE_URL}{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true&model={model}"

    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=35)
            if resp.status_code == 200 and len(resp.content) > 5000:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                return True
            elif resp.status_code == 402:
                # Free tier limit (1 image every 45s)
                try:
                    data = resp.json()
                    err_msg = data.get("error", {}).get("message", "")
                    match = re.search(r"Retry after (\d+)s", err_msg)
                    if match:
                        wait_sec = min(int(match.group(1)) + 2, 45)
                        print(f"Pollinations free tier rate limit: waiting {wait_sec}s...")
                        time.sleep(wait_sec)
                        continue
                except Exception:
                    time.sleep(10)
            else:
                print(f"Warning: Pollinations status {resp.status_code}, retrying...")
                time.sleep(3)
        except Exception as e:
            print(f"Warning: Attempt {attempt+1} failed for '{prompt[:40]}...': {e}")
            time.sleep(3)

    return False


def get_ai_visuals(
    topic: str,
    visual_count: int,
    is_vertical: bool = True,
    script_text: Optional[str] = None
) -> List[str]:
    """
    Generates a full set of custom AI visuals tailored to the script and topic.
    Saves them as .jpg files ready for MoviePy video rendering.
    """
    os.makedirs("assets", exist_ok=True)
    width = 720 if is_vertical else 1280
    height = 1280 if is_vertical else 720
    prefix = "ai_visual" if is_vertical else "ai_long_visual"

    print(f"\nGenerating {visual_count} custom AI visuals with Pollinations ({width}x{height})...")
    prompts = generate_scene_prompts(topic, script_text or topic, visual_count)

    visual_files = []
    for idx, prompt in enumerate(prompts):
        file_path = os.path.abspath(f"assets/{prefix}_{idx}.jpg")
        print(f"[{idx+1}/{visual_count}] Generating: {prompt[:65]}...")
        success = download_pollinations_image(prompt, file_path, width=width, height=height)
        if success:
            visual_files.append(file_path)
            print(f"Visual {idx+1} ready ({os.path.getsize(file_path)//1024} KB)")
        else:
            print(f"Failed to generate visual {idx+1}")

    if not visual_files:
        print("Falling back to stock footage...")
        import visuals
        return visuals.get_visuals(topic, visual_count, script_text=script_text)

    print(f"Successfully generated {len(visual_files)} AI visuals.\n")
    return visual_files


if __name__ == "__main__":
    files = get_ai_visuals("OpenAI GPT 6.1 Terra Architecture", visual_count=2, is_vertical=True)
    print("Generated files:", files)
