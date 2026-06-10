import os
import random
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()



ADDITIONAL_GEMINI_KEYS = []  # No hardcoded keys, use environment variables only


def _collect_gemini_keys() -> List[str]:
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
        raise ValueError("No Gemini API keys available. Please configure GEMINI_API_KEY or GEMINI_API_KEYS in your environment.")

    shuffled = keys[:]
    random.shuffle(shuffled)

    last_error = None
    for key in shuffled:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            response = model.generate_content(prompt)
            if response and hasattr(response, 'text') and response.text:
                print(f"Long-form script generated successfully by Gemini using key {_safe_key_label(key)}.")
                return response.text
            else:
                print(f"Gemini returned an invalid response with key {_safe_key_label(key)}. Trying another key...")
        except Exception as exc:
            last_error = exc
            print(f"Gemini request failed with key {_safe_key_label(key)}: {exc}. Trying another key...")

    if last_error:
        raise last_error
    raise ValueError("Gemini returned invalid responses for all configured keys.")

def generate_long_script(topic):
    """
    Generates a script for a long-form YouTube video using the Google Gemini API.
    Script length is capped at 3 minutes for concise, engaging content.
    """
    print("  ⏳ Preparing AI prompt...", end="", flush=True)
    try:
        # Script length is now capped at 3 minutes (180 seconds)
        target_duration = random.choice([60, 90, 120, 150, 180])  # 1-3 minutes
        word_count_min = int(target_duration * 2.2)  # ~2.2 words per second
        word_count_max = int(target_duration * 2.5)  # ~2.5 words per second
        print("\r  ✅ Prompt ready, contacting AI..." + " " * 20, end="", flush=True)
        
        prompt = f"""
        Create a comprehensive script for a {target_duration // 60}-minute YouTube video about the topic: "{topic}".

        IMPORTANT: Target {target_duration} seconds ({target_duration // 60} minutes) when spoken aloud (approximately {word_count_min}-{word_count_max} words total).
        
        The script should be:
        - Informative and educational
        - Well-structured with clear sections
        - Engaging and storytelling-driven
        - Professional and authoritative
        - Include interesting facts, examples, and explanations
        - Optimized to retain viewers throughout the video

        Retention rules:
        - Open with a strong 1-sentence hook (no greeting, no slow setup)
        - Add a mini open-loop every 2-3 sections (tease what is coming next)
        - Keep sentences concise and avoid repetitive wording
        - Include at least one surprising or counterintuitive point
        - End with a clear payoff summary before CTA
        
        Structure for long-form content:
        **Host:** [Hook - attention-grabbing statement/question - 1-2 sentences]
        **Host:** [Quick setup - what viewers will learn and why it matters - 2 sentences]
        **Host:** [Section 1 - First major point with detailed explanation and examples - 4-6 sentences]
        **Host:** [Section 2 - Second major point with supporting details - 4-6 sentences]
        **Host:** [Section 3 - Third major point with interesting facts + one curiosity tease - 4-6 sentences]
        {"**Host:** [Section 4 - Additional insights or deeper dive - 4-6 sentences]" if target_duration >= 300 else ""}
        {"**Host:** [Section 5 - Real-world applications or implications - 4-6 sentences]" if target_duration >= 360 else ""}
        **Host:** [Conclusion - high-value takeaway/payoff summary - 2-3 sentences]
        **Host:** [Call to action - encourage likes, comments, and subscriptions - 1-2 sentences]

        Keep the total word count between {word_count_min}-{word_count_max} words for a {target_duration // 60}-minute video.
        Make it informative, engaging, and valuable to viewers.
        
        DO NOT include any meta information like "Word Count:", "Estimated Speaking Time:", or similar notes.
        ONLY provide the actual script content with Host: markers.
        
        Now, generate a {target_duration // 60}-minute script for: "{topic}".
        """
        
        response_text = _generate_with_retry(prompt)
        if response_text:
            return response_text
        raise ValueError("Gemini returned empty responses across all keys.")
            
    except Exception as e:
        print(f"Error generating long-form script with Gemini: {e}")
        # Fallback script
        return f"""
        **Host:** Have you ever wondered about {topic}? Today, we're diving deep into this fascinating subject.

        **Host:** Let me start by explaining the basics. {topic} is an incredibly interesting area that affects many aspects of our daily lives.

        **Host:** First, let's look at the history and origins. Understanding where this comes from helps us appreciate its significance today.

        **Host:** Now, here's something really interesting. The way this works is actually more complex than most people realize, involving several key components that work together.

        **Host:** Let's break down the main points one by one, starting with the fundamentals that everyone should know.

        **Host:** Another fascinating aspect is how this connects to other related topics and influences various fields of study.

        **Host:** As we can see, {topic} is truly remarkable when you explore it in depth. The more you learn, the more interesting it becomes.

        **Host:** Thanks for watching! If you found this video informative, please like, comment, and subscribe for more deep dives into fascinating topics.
        """
