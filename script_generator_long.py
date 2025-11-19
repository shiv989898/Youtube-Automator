import os
import google.generativeai as genai
from dotenv import load_dotenv
import random

load_dotenv()

def generate_long_script(topic):
    """
    Generates a script for a long-form YouTube video using the Google Gemini API.
    Script length varies between 3-8 minutes for engaging long-form content.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
            
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Randomly choose script length for long-form variety
        target_duration = random.choice([180, 240, 300, 360, 420, 480])  # 3-8 minutes
        word_count_min = int(target_duration * 2.2)  # ~2.2 words per second
        word_count_max = int(target_duration * 2.5)  # ~2.5 words per second
        
        prompt = f"""
        Create a comprehensive script for a {target_duration // 60}-minute YouTube video about the topic: "{topic}".

        IMPORTANT: Target {target_duration} seconds ({target_duration // 60} minutes) when spoken aloud (approximately {word_count_min}-{word_count_max} words total).
        
        The script should be:
        - Informative and educational
        - Well-structured with clear sections
        - Engaging and storytelling-driven
        - Professional and authoritative
        - Include interesting facts, examples, and explanations
        
        Structure for long-form content:
        **Host:** [Hook - capture attention with an intriguing question or statement - 2-3 sentences]
        **Host:** [Introduction - explain what the video will cover - 2-3 sentences]
        **Host:** [Section 1 - First major point with detailed explanation and examples - 4-6 sentences]
        **Host:** [Section 2 - Second major point with supporting details - 4-6 sentences]
        **Host:** [Section 3 - Third major point with interesting facts - 4-6 sentences]
        {"**Host:** [Section 4 - Additional insights or deeper dive - 4-6 sentences]" if target_duration >= 300 else ""}
        {"**Host:** [Section 5 - Real-world applications or implications - 4-6 sentences]" if target_duration >= 360 else ""}
        **Host:** [Conclusion - summarize key takeaways - 2-3 sentences]
        **Host:** [Call to action - encourage likes, comments, and subscriptions - 1-2 sentences]

        Keep the total word count between {word_count_min}-{word_count_max} words for a {target_duration // 60}-minute video.
        Make it informative, engaging, and valuable to viewers.
        
        DO NOT include any meta information like "Word Count:", "Estimated Speaking Time:", or similar notes.
        ONLY provide the actual script content with Host: markers.
        
        Now, generate a {target_duration // 60}-minute script for: "{topic}".
        """
        
        response = model.generate_content(prompt)
        
        # Check for valid response and text
        if response and hasattr(response, 'text') and response.text:
            print(f"Long-form script generated successfully by Gemini ({target_duration // 60} minutes).")
            return response.text
        else:
            raise ValueError("Gemini returned an empty or invalid response.")
            
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
