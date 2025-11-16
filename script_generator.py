import os
import google.generativeai as genai
from dotenv import load_dotenv
import random

load_dotenv()

def generate_script(topic):
    """
    Generates a script for a YouTube Short using the Google Gemini API.
    Script length varies between 20-40 seconds for variety.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
            
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
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
        
        Structure it with clear "Host:" cues for the voiceover.
        End with a quick call to action (like, subscribe, or comment).

        Example structure for {target_duration} seconds:
        **Host:** [One punchy opening hook - 1 sentence]
        **Host:** [One surprising fact or key point - 1-2 sentences]
        {"**Host:** [One additional interesting detail - 1 sentence]" if target_duration >= 30 else ""}
        **Host:** [Quick call to action - 1 sentence]

        Keep it to {word_count_min}-{word_count_max} words total. Make every word count!
        
        DO NOT include any meta information like "Word Count:", "Estimated Speaking Time:", or similar notes.
        ONLY provide the actual script content with Host: markers.
        
        Now, generate a {target_duration}-second script for: "{topic}".
        """
        
        response = model.generate_content(prompt)
        
        # Check for valid response and text
        if response and hasattr(response, 'text') and response.text:
            print("Script generated successfully by Gemini.")
            return response.text
        else:
            # Fallback in case the API returns an empty or invalid response
            print(f"Gemini API returned an invalid response: {response}. Using fallback template.")
            return f"**Host:** Let's talk about {topic}! It's a huge subject, so here's a quick look. First, the basics. Then, a surprising fact. And finally, what the future holds. Thanks for watching!"

    except Exception as e:
        print(f"Error generating script with Gemini: {e}")
        # Fallback to a simple template if the API fails
        return f"**Host:** Welcome back! Today we're exploring {topic}. It's more fascinating than you can imagine. From its origins to its future, there's so much to uncover. Join us for the journey and don't forget to subscribe!"
