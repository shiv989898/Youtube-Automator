import random
from pytrends.request import TrendReq

def get_trending_topic():
    """
    Gets a trending topic from a predefined list.
    """
    fallback_topics = [
        # Science & Technology
        "The Future of Artificial Intelligence", "Mysteries of the Deep Ocean",
        "Understanding Black Holes", "The Science Behind Superheroes",
        "How Quantum Computers Work", "The Truth About 5G Technology",
        "The Science of Time Travel", "The Mystery of Dark Matter",
        "The Future of Space Exploration", "The Secrets of Quantum Physics",
        "The Science Behind Lightning", "How Cryptocurrencies Really Work",
        "The Evolution of Computers", "The Future of Virtual Reality",
        "The Science of Genetics and DNA", "The Mystery of Consciousness",
        "The Future of Robotics", "The Truth About Parallel Universes",
        "How AI Will Change Everything", "The Science of Teleportation",
        
        # Nature & Animals
        "Secrets of the Amazon Rainforest", "Incredible Animal Migrations",
        "The World's Most Dangerous Animals", "The World's Most Intelligent Animals",
        "The World's Most Beautiful Natural Wonders", "Amazing Animal Superpowers",
        "The Deadliest Creatures on Earth", "How Animals Survive Extreme Conditions",
        "The Secret Life of Whales", "The Most Venomous Snakes Alive",
        "Why Octopuses Are So Intelligent", "The Fastest Animals on Earth",
        "How Birds Navigate Thousands of Miles", "The World's Rarest Animals",
        "Why Cats Always Land on Their Feet", "The Secret Language of Dolphins",
        
        # History & Culture
        "The Secrets of Ancient Egypt", "The Rise and Fall of the Roman Empire",
        "Exploring Ancient Civilizations", "The History of Ancient Rome",
        "The History of Ancient Greece", "The History of Ancient China",
        "The History of Ancient India", "The Mystery of the Bermuda Triangle",
        "The Hidden History of Lost Civilizations", "The History of World War II",
        "The Truth About the Pyramids", "How Vikings Really Lived",
        "The Mystery of Stonehenge", "The Fall of the Mayan Civilization",
        "The Real Story of Cleopatra", "How Ancient Rome Fell Apart",
        "The Secrets of Samurai Warriors", "The Truth About Medieval Knights",
        
        # Psychology & Mind
        "The Psychology of Happiness", "The Science of Sleep & Dreams",
        "The Psychology of Social Media", "The Psychology of Fear and Phobias",
        "The Psychology of Motivation", "The Psychology of Love and Relationships",
        "The Science of Memory and Learning", "The Art of Meditation and Mindfulness",
        "The Secrets of the Human Brain", "Why We Procrastinate",
        "The Science of First Impressions", "How to Read Body Language",
        "Why We Get Deja Vu", "The Truth About Multitasking",
        "How Your Brain Creates Reality", "The Psychology of Success",
        
        # Space & Universe
        "Life on Mars: What Would It Take?", "The Secrets of the Universe",
        "The Mystery of Dark Energy", "How the Universe Will End",
        "What's Inside a Black Hole", "The Truth About Wormholes",
        "How Stars Are Born and Die", "The Biggest Things in the Universe",
        "Could We Live on Other Planets", "The Mystery of Alien Life",
        "What Happens When Galaxies Collide", "The Truth About Time Dilation",
        
        # Technology & Innovation
        "The Evolution of Music Genres", "A History of Video Games",
        "The Magic of Movie Special Effects", "The History of the Internet",
        "The History of Photography", "The World's Most Innovative Inventions",
        "The Evolution of Transportation", "The Power of Renewable Energy",
        "The Future of Medicine and Healthcare", "How Smartphones Changed Everything",
        "The Evolution of Social Media", "The Truth About Electric Cars",
        
        # Mysteries & Unexplained
        "The Mystery of UFOs and Aliens", "The World's Most Haunted Places",
        "The Truth About the Loch Ness Monster", "Unsolved Mysteries That Baffle Scientists",
        "The Mystery of Crop Circles", "The Truth About Area 51",
        "Real Ghost Encounters Explained", "The Mystery of Atlantis",
        "The Strangest Things Found in Space", "Unexplained Ocean Phenomena",
        
        # Extreme & Records
        "The World's Most Amazing Architecture", "The World's Strangest Foods",
        "The World's Most Extreme Weather", "The World's Rarest Gemstones",
        "The Tallest Mountains on Earth", "The Deepest Ocean Trenches",
        "The Fastest Vehicles Ever Built", "The Strongest Materials Known",
        "The Loudest Sounds in History", "The Most Expensive Things Ever",
        
        # Skills & Arts
        "The Art of Storytelling", "The Art of Creative Writing",
        "The Art of Public Speaking", "How to Master Any Skill Faster",
        "The Science of Perfect Timing", "How Magic Tricks Really Work",
        "The Secret to Learning Languages Fast", "How Professional Athletes Train",
        
        # Climate & Earth
        "The Science of Climate Change", "The Science of Earthquakes and Volcanoes",
        "The Science of Ocean Currents", "How Weather Prediction Works",
        "The Truth About Global Warming", "How Hurricanes Form and Move",
        "Why the Earth Has Seasons", "The Science of Tsunamis"
    ]
    try:
        # The pytrends library is currently unreliable, so we will rely on the fallback list.
        # This ensures a topic is always found.
        print("Choosing a topic from the curated list.")
        return random.choice(fallback_topics)
    except Exception as e:
        print(f"An error occurred: {e}. Using a random fallback topic as a last resort.")
        return random.choice(fallback_topics)
