import os
import requests
import re


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than", "this", "that", "these", "those",
    "with", "from", "into", "about", "over", "under", "between", "during", "while", "where", "when",
    "what", "why", "how", "who", "whom", "which", "your", "you", "are", "for", "to", "of", "in",
    "on", "at", "by", "is", "was", "were", "be", "been", "being", "it", "its", "as", "we", "our",
    "they", "their", "them", "he", "she", "his", "her", "will", "would", "can", "could", "should",
    "today", "video", "short", "shorts", "host", "like", "comment", "subscribe", "watch"
}

# High-signal anchors used to keep stock footage tightly aligned to topic category.
CATEGORY_KEYWORDS = {
    "dogs": {"dog", "dogs", "puppy", "puppies", "canine", "retriever", "husky", "beagle"},
    "cats": {"cat", "cats", "kitten", "kittens", "feline"},
    "technology": {"tech", "technology", "software", "computer", "coding", "programming", "ai", "robot", "gadget", "smartphone"},
    "finance": {"finance", "financial", "money", "investing", "investment", "stock", "market", "crypto", "bitcoin", "economy"},
    "health": {"health", "medical", "wellness", "fitness", "workout", "nutrition", "doctor", "hospital", "mental"},
    "food": {"food", "cooking", "kitchen", "recipe", "meal", "chef", "restaurant", "dish"},
    "travel": {"travel", "trip", "tourism", "vacation", "destination", "beach", "mountain", "city"},
    "sports": {"sport", "sports", "football", "soccer", "basketball", "tennis", "baseball", "training"},
    "nature": {"nature", "wildlife", "forest", "ocean", "animal", "landscape", "river", "mountain"},
    "business": {"business", "office", "startup", "corporate", "entrepreneur", "meeting", "strategy"},
    "education": {"education", "school", "student", "teacher", "learning", "classroom", "study"},
}

CATEGORY_PRIMARY_TERMS = {
    "dogs": "dog",
    "cats": "cat",
    "technology": "technology",
    "finance": "finance",
    "health": "health",
    "food": "food",
    "travel": "travel",
    "sports": "sports",
    "nature": "nature",
    "business": "business",
    "education": "education",
}


def _tokenize(text):
    return [w for w in re.findall(r"[a-zA-Z]{3,}", (text or "").lower()) if w not in STOPWORDS]


def _detect_category_anchor(topic, script_text=None):
    """Detect dominant topic category and return strict anchor terms for queries."""
    text = f"{topic or ''} {script_text or ''}".lower()
    token_set = set(_tokenize(text))
    best_category = None
    best_hits = set()

    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = token_set.intersection(keywords)
        if len(hits) > len(best_hits):
            best_category = category
            best_hits = hits

    if best_category and best_hits:
        # Keep at least one canonical category term as hard anchor.
        primary_anchor = CATEGORY_PRIMARY_TERMS.get(best_category, best_category)
        ordered_hits = [primary_anchor] + [h for h in sorted(best_hits) if h != primary_anchor]
        return best_category, ordered_hits[:4]

    # Fallback: use strongest topic tokens as anchors if no known category is matched.
    topic_terms = _tokenize(topic)
    if topic_terms:
        dedup = []
        for term in topic_terms:
            if term not in dedup:
                dedup.append(term)
        return "topic", dedup[:3]

    return None, []


def _video_relevance_score(video, matched_query, topic_terms, anchor_terms):
    user = video.get("user", {}) if isinstance(video.get("user"), dict) else {}
    metadata = " ".join(
        [
            str(video.get("url", "")),
            str(video.get("image", "")),
            str(user.get("name", "")),
            str(video.get("id", "")),
        ]
    ).lower()

    score = 0
    query_text = (matched_query or "").lower()

    if any(term in query_text for term in anchor_terms):
        score += 40
    if any(term in query_text for term in topic_terms):
        score += 25
    if metadata and any(term in metadata for term in anchor_terms):
        score += 25
    if metadata and any(term in metadata for term in topic_terms):
        score += 10

    return score


def _build_context_queries(topic, script_text=None, max_queries=6):
    """Build strict topic-anchored queries to prevent unrelated stock footage."""
    queries = []
    base_topic = (topic or "").strip()
    if base_topic:
        queries.append(base_topic)

    category, anchor_terms = _detect_category_anchor(base_topic, script_text)
    full_text = f"{base_topic}. {script_text or ''}".strip().lower()
    words = [w for w in re.findall(r"[a-zA-Z]{4,}", full_text) if w not in STOPWORDS]
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1

    top_keywords = [k for k, _ in sorted(freq.items(), key=lambda item: item[1], reverse=True)[:10]]

    # Always keep category/topic anchors in every expansion query.
    for anchor in anchor_terms:
        if anchor not in queries:
            queries.append(anchor)
        if base_topic:
            anchored_topic = f"{anchor} {base_topic}".strip()
            if anchored_topic not in queries:
                queries.append(anchored_topic)

    for keyword in top_keywords:
        if anchor_terms:
            candidate = f"{anchor_terms[0]} {keyword}".strip()
        else:
            candidate = f"{base_topic} {keyword}".strip()
        if candidate and candidate not in queries:
            queries.append(candidate)

    if category:
        print(f"Detected visual category anchor: {category} -> {anchor_terms}")

    return queries[:max_queries] if queries else [base_topic or "nature"]

def get_visuals(topic, num_visuals=5, target_duration=20, script_text=None):
    """
    Gathers visuals for the video. It tries Pexels first, then falls back to Pixabay.
    Optimized to download only videos matching the target duration to save time.
    """
    print(f"Gathering {num_visuals} visuals for ~{target_duration}s duration...")
    visual_files = []

    # --- API Provider 1: Pexels ---
    pexels_api_key = os.getenv("PEXELS_API_KEY")
    if pexels_api_key:
        print("Trying Pexels for visuals...")
        headers = {"Authorization": pexels_api_key}
        context_queries = _build_context_queries(topic, script_text=script_text, max_queries=8)
        print(f"Using context queries: {context_queries}")
        try:
            videos = []
            seen_ids = set()
            topic_terms = _tokenize(topic)
            _, anchor_terms = _detect_category_anchor(topic, script_text)
            for query in context_queries:
                params = {
                    "query": query,
                    "per_page": max(15, num_visuals * 2),
                    "orientation": "portrait"
                }
                response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=30)
                response.raise_for_status()
                pexels_data = response.json()
                for video in pexels_data.get("videos", []):
                    video_id = video.get("id")
                    if video_id in seen_ids:
                        continue
                    seen_ids.add(video_id)
                    relevance = _video_relevance_score(video, query, topic_terms, anchor_terms)
                    videos.append((relevance, video, query))

            # Deterministic relevance-first ordering to avoid random/off-topic picks.
            videos.sort(key=lambda x: x[0], reverse=True)

            for relevance, video, matched_query in videos:
                if len(visual_files) >= num_visuals:
                    break

                # If we detected an anchor, reject very weak matches.
                if anchor_terms and relevance < 35:
                    continue

                video_files = video.get("video_files", [])
                if not video_files:
                    continue
                
                # Check video duration to avoid downloading long videos
                video_duration = video.get('duration', 0)
                if video_duration > target_duration + 10:  # Skip videos much longer than needed
                    continue
                
                # Filter for optimal portrait resolution (1080x1920 for YouTube Shorts)
                # Avoid 4K to save bandwidth, 1080p is perfect quality for Shorts
                portrait_videos = [f for f in video_files 
                                 if f.get('height', 0) >= 1920 
                                 and f.get('width', 0) >= 1080
                                 and f.get('height', 0) <= 2160]  # Max 2K, avoid 4K
                
                if not portrait_videos:
                    continue

                # Select optimal video (prefer 1080p over 4K for speed)
                best_video = min(portrait_videos, key=lambda x: abs(x.get('height', 0) - 1920))
                video_url = best_video.get("link")

                if video_url:
                    print(
                        f"Downloading Pexels video {video['id']} (score={relevance}, query='{matched_query}', "
                        f"~{video_duration}s, {best_video.get('height')}x{best_video.get('width')})"
                    )
                    
                    # Stream download with chunks for faster processing
                    filename = f"assets/visual_{len(visual_files)}.mp4"
                    try:
                        with requests.get(video_url, stream=True, timeout=30) as video_response:
                            video_response.raise_for_status()
                            total_size = int(video_response.headers.get('content-length', 0))
                            
                            with open(filename, "wb") as f:
                                downloaded = 0
                                for chunk in video_response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                                        downloaded += len(chunk)
                                        # Show progress for large files
                                        if total_size > 1024 * 1024:  # > 1MB
                                            progress = (downloaded / total_size) * 100
                                            print(f"\rProgress: {progress:.1f}%", end="")
                            
                            if total_size > 1024 * 1024:
                                print()  # New line after progress
                            
                        visual_files.append(filename)
                        print(f"[OK] Downloaded {total_size / (1024*1024):.1f} MB")
                    except requests.exceptions.RequestException as e:
                        print(f"\n[ERROR] Download failed: {e}")
                        if os.path.exists(filename):
                            os.remove(filename)
                        continue
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Pexels: {e}. Trying next provider.")
            
    # --- API Provider 2: Pixabay (Fallback) ---
    if len(visual_files) < num_visuals:
        pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        if pixabay_api_key:
            print("Pexels failed or had insufficient results. Trying Pixabay...")
            needed = num_visuals - len(visual_files)
            try:
                topic_terms = _tokenize(topic)
                _, anchor_terms = _detect_category_anchor(topic, script_text)
                query_candidates = _build_context_queries(topic, script_text=script_text, max_queries=4)

                videos = []
                seen_ids = set()
                for query in query_candidates:
                    params = {
                        "key": pixabay_api_key,
                        "q": query,
                        "video_type": "film",
                        "orientation": "vertical",
                        "per_page": max(needed * 2, 10),
                        "safesearch": "true"
                    }
                    response = requests.get("https://pixabay.com/api/videos/", params=params)
                    response.raise_for_status()
                    pixabay_data = response.json()
                    for video in pixabay_data.get("hits", []):
                        video_id = video.get("id")
                        if video_id in seen_ids:
                            continue
                        seen_ids.add(video_id)

                        tags = str(video.get("tags", "")).lower()
                        score = 0
                        ql = query.lower()
                        if any(t in ql for t in anchor_terms):
                            score += 40
                        if any(t in ql for t in topic_terms):
                            score += 20
                        if any(t in tags for t in anchor_terms):
                            score += 30
                        if any(t in tags for t in topic_terms):
                            score += 10
                        videos.append((score, video, query))

                videos.sort(key=lambda x: x[0], reverse=True)

                for score, video, matched_query in videos:
                    if len(visual_files) >= num_visuals:
                        break

                    if anchor_terms and score < 35:
                        continue
                    
                    # Check duration to avoid long videos
                    video_duration = video.get('duration', 0)
                    if video_duration > target_duration + 10:
                        continue
                    
                    # Pixabay: use 'medium' for optimal balance (faster than 'large')
                    video_data = video.get("videos", {})
                    video_url = video_data.get("medium", {}).get("url") or video_data.get("large", {}).get("url")
                    
                    if video_url:
                        print(f"Downloading Pixabay video {video['id']} (score={score}, query='{matched_query}', ~{video_duration}s)")
                        
                        # Stream download with chunks
                        filename = f"assets/visual_{len(visual_files)}.mp4"
                        try:
                            with requests.get(video_url, stream=True, timeout=30) as video_response:
                                video_response.raise_for_status()
                                total_size = int(video_response.headers.get('content-length', 0))
                                
                                with open(filename, "wb") as f:
                                    downloaded = 0
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                            downloaded += len(chunk)
                                            if total_size > 1024 * 1024:
                                                progress = (downloaded / total_size) * 100
                                                print(f"\rProgress: {progress:.1f}%", end="")
                                
                                if total_size > 1024 * 1024:
                                    print()
                                
                            visual_files.append(filename)
                            print(f"[OK] Downloaded {total_size / (1024*1024):.1f} MB")
                        except requests.exceptions.RequestException as e:
                            print(f"\n[ERROR] Download failed: {e}")
                            if os.path.exists(filename):
                                os.remove(filename)
                            continue
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from Pixabay: {e}")

    print(f"Found {len(visual_files)} visuals.")
    return visual_files
