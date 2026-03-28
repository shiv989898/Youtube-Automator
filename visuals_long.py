import os
import requests
import re


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than", "this", "that", "these", "those",
    "with", "from", "into", "about", "over", "under", "between", "during", "while", "where", "when",
    "what", "why", "how", "who", "whom", "which", "your", "you", "are", "for", "to", "of", "in",
    "on", "at", "by", "is", "was", "were", "be", "been", "being", "it", "its", "as", "we", "our",
    "they", "their", "them", "he", "she", "his", "her", "will", "would", "can", "could", "should",
    "today", "video", "long", "form", "host", "like", "comment", "subscribe", "watch"
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
        primary_anchor = CATEGORY_PRIMARY_TERMS.get(best_category, best_category)
        ordered_hits = [primary_anchor] + [h for h in sorted(best_hits) if h != primary_anchor]
        return best_category, ordered_hits[:4]

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


def _build_context_queries(topic, script_text=None, max_queries=10):
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

    top_keywords = [k for k, _ in sorted(freq.items(), key=lambda item: item[1], reverse=True)[:12]]

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


def get_visuals(topic, num_visuals: int = 8, target_duration: int = 180, script_text=None):
    """Gather horizontal (16:9) 1080p-friendly visuals for long-form videos.

    Prefers landscape clips (width >= height) from Pexels/Pixabay and avoids
    the portrait settings used by shorts.
    Optimized to download only videos matching the target duration to save time and bandwidth.
    """
    per_clip_duration = target_duration // num_visuals if num_visuals > 0 else 30
    print(f"Gathering {num_visuals} horizontal visuals (~{per_clip_duration}s each, total ~{target_duration}s)...")
    visual_files = []

    # --- API Provider 1: Pexels (landscape) ---
    pexels_api_key = os.getenv("PEXELS_API_KEY")
    if pexels_api_key:
        print("Trying Pexels (landscape) for visuals...")
        headers = {"Authorization": pexels_api_key}
        context_queries = _build_context_queries(topic, script_text=script_text, max_queries=10)
        print(f"Using context queries: {context_queries}")
        try:
            videos = []
            seen_ids = set()
            topic_terms = _tokenize(topic)
            _, anchor_terms = _detect_category_anchor(topic, script_text)
            for query in context_queries:
                params = {
                    "query": query,
                    "per_page": max(15, num_visuals * 3),
                    "orientation": "landscape",  # key change vs shorts
                }
                response = requests.get(
                    "https://api.pexels.com/videos/search",
                    headers=headers,
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
                pexels_data = response.json()
                for video in pexels_data.get("videos", []):
                    video_id = video.get("id")
                    if video_id in seen_ids:
                        continue
                    seen_ids.add(video_id)
                    relevance = _video_relevance_score(video, query, topic_terms, anchor_terms)
                    videos.append((relevance, video, query))

            videos.sort(key=lambda x: x[0], reverse=True)

            for relevance, video, matched_query in videos:
                if len(visual_files) >= num_visuals:
                    break

                if anchor_terms and relevance < 35:
                    continue

                # Check video duration to avoid downloading unnecessarily long videos
                video_duration = video.get('duration', 0)
                # Skip videos that are way too long (more than 2x per-clip duration + 20s buffer)
                max_acceptable = (per_clip_duration * 2) + 20
                if video_duration > max_acceptable:
                    continue
                
                # Skip videos that are too short (less than half the per-clip duration)
                min_acceptable = max(5, per_clip_duration // 2)
                if video_duration < min_acceptable:
                    continue

                video_files = video.get("video_files", [])
                if not video_files:
                    continue

                # Prefer landscape, 1080p (avoid 4K to save bandwidth)
                # Prioritize 1920x1080 over higher resolutions
                candidates = [
                    f
                    for f in video_files
                    if f.get("width", 0) >= f.get("height", 0)
                    and f.get("width", 0) >= 1280
                    and f.get("width", 0) <= 2560  # Avoid 4K
                ]
                if not candidates:
                    continue

                # Select video closest to 1080p (1920x1080)
                best = min(
                    candidates,
                    key=lambda x: abs(x.get("width", 0) - 1920) + abs(x.get("height", 0) - 1080),
                )
                video_url = best.get("link")
                if not video_url:
                    continue

                print(
                    f"Downloading video {len(visual_files)+1}/{num_visuals} from Pexels: {video['id']} "
                    f"(score={relevance}, query='{matched_query}', ~{video_duration}s, {best.get('width')}x{best.get('height')})"
                )
                filename = f"long_visual_{len(visual_files)}.mp4"
                
                # Stream download with progress bar
                try:
                    with requests.get(video_url, stream=True, timeout=60) as video_response:
                        video_response.raise_for_status()
                        total_size = int(video_response.headers.get('content-length', 0))
                        downloaded = 0
                        
                        with open(filename, "wb") as f:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    if total_size > 0:
                                        progress = int((downloaded / total_size) * 100)
                                        bar_length = 30
                                        filled = int((progress / 100) * bar_length)
                                        bar = "█" * filled + "░" * (bar_length - filled)
                                        print(f"\r  [{bar}] {progress}% ({downloaded//(1024*1024):.1f}/{total_size//(1024*1024):.1f} MB)", end="", flush=True)
                        print()  # New line after download
                    visual_files.append(filename)
                except Exception as e:
                    print(f"\n  ❌ Download failed: {e}")
                    if os.path.exists(filename):
                        os.remove(filename)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Pexels (landscape): {e}. Trying next provider.")

    # --- API Provider 2: Pixabay (landscape fallback) ---
    if len(visual_files) < num_visuals:
        pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        if pixabay_api_key:
            print("Pexels had insufficient landscape results. Trying Pixabay...")
            needed = num_visuals - len(visual_files)
            try:
                topic_terms = _tokenize(topic)
                _, anchor_terms = _detect_category_anchor(topic, script_text)
                query_candidates = _build_context_queries(topic, script_text=script_text, max_queries=5)

                videos = []
                seen_ids = set()
                for query in query_candidates:
                    params = {
                        "key": pixabay_api_key,
                        "q": query,
                        "video_type": "film",
                        "orientation": "horizontal",
                        "per_page": max(needed * 3, 10),
                        "safesearch": "true",
                    }
                    response = requests.get(
                        "https://pixabay.com/api/videos/", params=params, timeout=30
                    )
                    response.raise_for_status()
                    pixabay_data = response.json()
                    for video in pixabay_data.get("hits", []):
                        video_id = video.get("id")
                        if video_id in seen_ids:
                            continue
                        seen_ids.add(video_id)

                        tags = str(video.get("tags", "")).lower()
                        ql = query.lower()
                        score = 0
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
                    
                    # Check duration to avoid downloading long videos
                    video_duration = video.get('duration', 0)
                    max_acceptable = (per_clip_duration * 2) + 20
                    min_acceptable = max(5, per_clip_duration // 2)
                    
                    if video_duration > max_acceptable or video_duration < min_acceptable:
                        continue

                    video_url = (
                        video.get("videos", {})
                        .get("large", {})
                        .get("url")
                    )
                    if not video_url:
                        continue

                    print(
                        f"Downloading horizontal video from Pixabay: {video['id']} "
                        f"(score={score}, query='{matched_query}')"
                    )
                    video_response = requests.get(video_url, timeout=60)
                    video_response.raise_for_status()
                    filename = f"long_visual_{len(visual_files)}.mp4"
                    with open(filename, "wb") as f:
                        f.write(video_response.content)
                    visual_files.append(filename)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching from Pixabay (horizontal): {e}")

    print(f"Found {len(visual_files)} horizontal visuals.")
    return visual_files
