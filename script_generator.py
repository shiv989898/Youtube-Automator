import os
import random
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()



ADDITIONAL_GEMINI_KEYS = []  # No hardcoded keys, use environment variables only


def _collect_gemini_keys() -> List[str]:
    """Gather every available API key, prioritizing environment variables."""
    keys = []

    multi_env = os.getenv("GEMINI_API_KEYS")
    if multi_env:
        keys.extend([key.strip() for key in multi_env.split(",") if key.strip()])

    single_env = os.getenv("GEMINI_API_KEY")
    if single_env:
        keys.append(single_env.strip())

    keys.extend(ADDITIONAL_GEMINI_KEYS)

    deduped = []
    for key in keys:
        if key and key not in deduped:
            deduped.append(key)
    return deduped


def _safe_key_label(key: str) -> str:
    return f"{key[:6]}..." if key else "<missing>"


def _generate_with_retry(prompt: str) -> str:
    keys = _collect_gemini_keys()
    if not keys:
        raise ValueError("No Gemini API keys available. Please set GEMINI_API_KEY or GEMINI_API_KEYS in your environment.")

    shuffled = keys[:]
    random.shuffle(shuffled)

    last_error = None
    for key in shuffled:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('models/gemma-3-12b-it')
            response = model.generate_content(prompt)
            if response and hasattr(response, 'text') and response.text:
                print(f"Script generated successfully by Gemini (key {_safe_key_label(key)}).")
                return response.text
            else:
                print(f"Gemini returned an invalid response with key {_safe_key_label(key)}. Trying another key...")
        except Exception as exc:
            last_error = exc
            print(f"Gemini request failed with key {_safe_key_label(key)}: {exc}. Trying another key...")

    if last_error:
        raise last_error
    raise ValueError("Gemini returned invalid responses for all configured keys.")

def generate_script(topic):
    """
    Generates a script for a YouTube Short using the Google Gemini API.
    Script length varies between 20-40 seconds for variety.
    """
    try:
        # Randomly choose script length for variety
        target_duration = random.choice([20, 25, 30, 35, 40])
        word_count_min = int(target_duration * 2.2)  # ~2.2 words per second
        word_count_max = int(target_duration * 2.8)  # ~2.8 words per second
        
        prompt = f"""
        Create a script for a {target_duration}-second YouTube Short about the topic: "{topic}".

        IMPORTANT: Keep it to {target_duration} seconds when spoken aloud (approximately {word_count_min}-{word_count_max} words total).
        
        The script should be:
        - Engaging and fast-paced
        - Easy to understand
        - Punchy and concise
        - Exciting and curious in tone
        - Optimized for audience retention from second 0

        Retention rules:
        - First line must be a strong hook (no greeting, no intro fluff)
        - Keep sentence length short and high-energy
        - Introduce one curiosity twist in the middle ("but here's the catch" style)
        - End with a quick payoff plus CTA
        - Avoid generic filler like "today we're talking about"
        
        Structure it with clear "Host:" cues for the voiceover.
        End with a quick call to action (like, subscribe, or comment).

        Example structure for {target_duration} seconds:
        **Host:** [One punchy opening hook - 1 sentence, max 8-12 words]
        **Host:** [One surprising fact or key point - 1-2 short sentences]
        {"**Host:** [One curiosity twist or contradiction - 1 sentence]" if target_duration >= 30 else ""}
        **Host:** [Quick payoff + call to action - 1 sentence]

        Keep it to {word_count_min}-{word_count_max} words total. Make every word count!
        
        DO NOT include any meta information like "Word Count:", "Estimated Speaking Time:", or similar notes.
        ONLY provide the actual script content with Host: markers.
        
        Now, generate a {target_duration}-second script for: "{topic}".
        """
        
        response_text = _generate_with_retry(prompt)
        if response_text:
            return response_text
        
        print("Gemini API returned empty responses across all keys. Using fallback template.")
        return f"**Host:** Let's talk about {topic}! It's a huge subject, so here's a quick look. First, the basics. Then, a surprising fact. And finally, what the future holds. Thanks for watching!"

    except Exception as e:
        print(f"Error generating script with Gemini: {e}")
        # Fallback to a simple template if the API fails
        return f"**Host:** Welcome back! Today we're exploring {topic}. It's more fascinating than you can imagine. From its origins to its future, there's so much to uncover. Join us for the journey and don't forget to subscribe!"
