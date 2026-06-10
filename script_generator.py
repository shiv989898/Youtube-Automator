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
            model = genai.GenerativeModel('gemini-2.5-flash')
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
    Generates a viral-optimized script for YouTube Shorts.
    Engineered for maximum retention with proven hook formulas.
    """
    try:
        # Randomly choose script length for variety
        target_duration = random.choice([20, 25, 30, 35, 40])
        word_count_min = int(target_duration * 2.2)  # ~2.2 words per second
        word_count_max = int(target_duration * 2.8)  # ~2.8 words per second
        
        # Proven hook formulas that boost retention
        hook_styles = [
            "a shocking statistic or fact",
            "a controversial statement that challenges common belief",
            "a 'what if' scenario that sparks curiosity",
            "a bold claim followed by proof",
            "a relatable problem the viewer faces",
        ]
        selected_hook = random.choice(hook_styles)
        
        prompt = f"""
        Create a {target_duration}-second YouTube Short script about: "{topic}"

        CRITICAL RETENTION RULES (YouTube algorithm favors these):
        
        1. HOOK (First 3 seconds - MOST IMPORTANT):
           - Use this hook style: {selected_hook}
           - NO greetings, NO "today we'll talk about"
           - First words must create instant curiosity or shock
           - Pattern interrupt: Start mid-thought or with a question
           
        2. LOOP STRUCTURE (Keeps viewers watching):
           - Tease something coming ("but wait, it gets crazier")
           - Use open loops: hint at info, deliver later
           - Each sentence should make them want the next
           
        3. PACING (Prevents drop-off):
           - Short punchy sentences (5-10 words max)
           - Vary sentence rhythm: short, short, medium, short
           - Add verbal "speed bumps": "Here's the thing...", "But get this..."
           
        4. PAYOFF + CTA (Last 3 seconds):
           - Deliver on the hook's promise
           - End with curiosity for more: "Follow for part 2" or "Comment your guess"
           - Never end flat - end on emotion or question

        TONE: Conversational, like telling a friend something wild you just learned.
        Use contractions (don't, can't, it's) to sound natural.

        FORMAT:
        **Host:** [Hook - ONE powerful sentence, 8-12 words]
        **Host:** [Setup - build intrigue, 1-2 sentences]
        **Host:** [Twist/reveal - the "but here's the thing" moment]
        **Host:** [Payoff + CTA - deliver value, ask for engagement]

        Word count: {word_count_min}-{word_count_max} words total.
        
        DO NOT include meta notes like "Word Count:" or "Speaking Time:".
        ONLY output the script with Host: markers.

        Generate the script now for: "{topic}"
        """
        
        response_text = _generate_with_retry(prompt)
        if response_text:
            return response_text
        
        print("Gemini API returned empty responses across all keys. Using fallback template.")
        return f"**Host:** You won't believe what happens with {topic}! Most people get this completely wrong. Here's what they miss. The truth? It's way more interesting than you think. Drop a comment if you knew this!"

    except Exception as e:
        print(f"Error generating script with Gemini: {e}")
        return f"**Host:** Stop scrolling - {topic} is about to blow your mind! Everyone talks about it, but nobody mentions this part. Here's the secret most people miss. Follow for more wild facts like this!"
