import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Curated high-relevance search queries for AI news
AI_SEARCH_QUERIES = [
    "Artificial Intelligence model release",
    "OpenAI ChatGPT GPT",
    "Anthropic Claude AI",
    "Google DeepMind Gemini AI",
    "DeepSeek AI",
    "AI robotics humanoid",
    "NVIDIA AI GPU",
    "OpenAI Sora generative video"
]


def clean_headline(title: str) -> str:
    """Removes source names like ' - TechCrunch', ' - The Verge', etc."""
    cleaned = re.sub(r"\s*-\s*[A-Za-z0-9\s\.\&]+$", "", title)
    return cleaned.strip()


def get_latest_ai_news(category_query: Optional[str] = None, limit: int = 10) -> List[Dict[str, str]]:
    """
    Fetches real-time breaking AI news from Google News RSS for 100% free with no API key.
    """
    query = category_query if category_query else "Artificial Intelligence OR OpenAI OR Anthropic OR DeepSeek when:3d"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    news_items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                desc_elem = item.find("description")
                pub_elem = item.find("pubDate")

                if title_elem is not None and title_elem.text:
                    raw_title = title_elem.text
                    clean_title = clean_headline(raw_title)

                    # Extract plain text from description HTML if available
                    desc_text = ""
                    if desc_elem is not None and desc_elem.text:
                        desc_text = re.sub(r"<[^>]+>", " ", desc_elem.text).strip()

                    news_items.append({
                        "raw_title": raw_title,
                        "title": clean_title,
                        "summary": desc_text,
                        "date": pub_elem.text if pub_elem is not None else ""
                    })

                    if len(news_items) >= limit:
                        break
    except Exception as e:
        print(f"Warning: Failed to fetch live AI news: {e}")

    return news_items


def search_topic_facts(topic: str, max_results: int = 5) -> str:
    """
    Searches the web for verified news and facts about a specific topic.
    Returns a structured text block for Gemini grounding.
    """
    # Clean topic for search query
    clean_query = re.sub(r"[#]", "", topic)
    encoded = urllib.parse.quote(clean_query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"

    facts = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            for item in root.findall(".//item")[:max_results]:
                title = item.find("title").text if item.find("title") is not None else ""
                desc = item.find("description").text if item.find("description") is not None else ""
                clean_desc = re.sub(r"<[^>]+>", " ", desc).strip()
                if title:
                    facts.append(f"• {title}: {clean_desc}")
    except Exception as e:
        print(f"Warning: Error searching topic facts for '{topic}': {e}")

    if not facts:
        return f"Topic: {topic} (Latest general developments and technical analysis)"

    return "\n".join(facts)


def get_trending_ai_topic() -> str:
    """
    Returns a single fresh, trending AI news topic from the live internet.
    Falls back gracefully if offline.
    """
    news = get_latest_ai_news(limit=6)
    if news:
        # Return the top breaking headline
        for item in news:
            title = item["title"]
            if len(title) > 15:
                return title

    # Fallback topics if news feeds are unreachable
    return "OpenAI Announces Major Next-Generation AI Architecture"


if __name__ == "__main__":
    print("Testing Live AI News Search...")
    topic = get_trending_ai_topic()
    print("Trending AI Topic:", topic)
    print("\nFacts for topic:")
    print(search_topic_facts(topic))
