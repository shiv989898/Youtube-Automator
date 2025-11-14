import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def generate_script(topic):
    """
    Generates a script for a YouTube Short using the Google Gemini API.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
            
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Create a script for a 30-40 second YouTube Short about the topic: "{topic}".

        IMPORTANT: Keep it SHORT - aim for 30-40 seconds when spoken aloud (approximately 75-100 words total).
        
        The script should be:
        - Engaging and fast-paced
        - Easy to understand
        - Punchy and concise
        - Exciting and curious in tone
        
        Structure it with clear "Host:" cues for the voiceover.
        End with a quick call to action (like, subscribe, or comment).

        Example structure (SHORT version):
        **Host:** [One punchy opening hook - 1 sentence]
        **Host:** [One surprising fact - 1-2 sentences]
        **Host:** [One mind-blowing point - 1-2 sentences]
        **Host:** [Quick call to action - 1 sentence]

        Keep it under 100 words total. Make every word count!
        
        DO NOT include any meta information like "Word Count:", "Estimated Speaking Time:", or similar notes.
        ONLY provide the actual script content with Host: markers.
        
        Now, generate a SHORT 30-40 second script for: "{topic}".
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
