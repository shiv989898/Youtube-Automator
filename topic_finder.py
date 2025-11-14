import random
from pytrends.request import TrendReq

def get_trending_topic():
    """
    Gets a trending topic from a predefined list.
    """
    fallback_topics = [
        "The Future of Artificial Intelligence", "Mysteries of the Deep Ocean",
        "The World's Most Amazing Architecture", "The Science of Sleep & Dreams",
        "A History of Video Games", "Secrets of the Amazon Rainforest",
        "The Evolution of Music Genres", "The Psychology of Happiness",
        "Exploring Ancient Civilizations", "The Science Behind Superheroes",
        "Incredible Animal Migrations", "The Magic of Movie Special Effects",
        "The Rise and Fall of the Roman Empire", "Understanding Black Holes",
        "The Art of Storytelling", "The World's Strangest Foods",
        "The Power of Renewable Energy", "The History of the Internet",
        "Life on Mars: What Would It Take?", "The Philosophy of Stoicism",
        "The Mystery of the Bermuda Triangle", "How Cryptocurrencies Work",
        "The Secrets of Ancient Egypt", "The Science of Climate Change",
        "The World's Most Dangerous Animals", "The Future of Space Exploration",
        "The Hidden History of Lost Civilizations", "The Psychology of Social Media",
        "The Science of Time Travel", "The World's Most Beautiful Natural Wonders",
        "The Evolution of Human Language", "The Mystery of Dark Matter",
        "The Art of Meditation and Mindfulness", "The History of Photography",
        "The Science of Memory and Learning", "The World's Most Extreme Weather",
        "The Future of Virtual Reality", "The Secrets of the Universe",
        "The Psychology of Fear and Phobias", "The History of Ancient Rome",
        "The Science Behind Lightning", "The World's Most Intelligent Animals",
        "The Evolution of Transportation", "The Mystery of Consciousness",
        "The Art of Creative Writing", "The History of Ancient Greece",
        "The Science of Earthquakes and Volcanoes", "The World's Rarest Gemstones",
        "The Future of Robotics and Automation", "The Secrets of Quantum Physics",
        "The Psychology of Motivation", "The History of Ancient China",
        "The Science of Ocean Currents", "The World's Most Innovative Inventions",
        "The Evolution of Computers", "The Mystery of UFOs and Aliens",
        "The Art of Public Speaking", "The History of World War II",
        "The Science of Genetics and DNA", "The World's Most Haunted Places",
        "The Future of Medicine and Healthcare", "The Secrets of the Human Brain",
        "The Psychology of Love and Relationships", "The History of Ancient India"
    ]
    try:
        # The pytrends library is currently unreliable, so we will rely on the fallback list.
        # This ensures a topic is always found.
        print("Choosing a topic from the curated list.")
        return random.choice(fallback_topics)
    except Exception as e:
        print(f"An error occurred: {e}. Using a random fallback topic as a last resort.")
        return random.choice(fallback_topics)
