import os
import pickle
import time
import random
import httplib2
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

def generate_engaging_title_long(topic):
    """
    Generates engaging, professional titles for long-form YouTube content.
    """
    title_templates = [
        # Educational & Informative
        f"The Complete Guide to {topic} - Everything You Need to Know",
        f"Understanding {topic}: A Deep Dive",
        f"{topic} Explained: The Full Story",
        f"Everything About {topic} (Comprehensive Guide)",
        f"The Ultimate {topic} Breakdown",
        f"{topic}: The Complete Analysis",
        
        # Scientific & Academic
        f"The Science Behind {topic}",
        f"How {topic} Actually Works (Detailed Explanation)",
        f"{topic}: The Facts and Research",
        f"The Truth About {topic} - Scientific Perspective",
        f"Exploring {topic}: A Scientific Approach",
        
        # Documentary Style
        f"The Fascinating World of {topic}",
        f"Inside {topic}: What You Need to Know",
        f"{topic}: An In-Depth Investigation",
        f"The Real Story of {topic}",
        f"Discovering {topic}: A Journey",
        
        # Professional & Authoritative
        f"{topic}: Expert Analysis and Insights",
        f"Mastering {topic} - Complete Tutorial",
        f"The Definitive Guide to {topic}",
        f"Professional Perspective on {topic}",
        f"{topic}: Advanced Understanding",
    ]
    
    return random.choice(title_templates)

def generate_tags_long(topic):
    """
    Generates relevant tags for long-form video discovery.
    """
    base_tags = [
        topic.lower(),
        "educational",
        "informative",
        "tutorial",
        "guide",
        "explained",
        "science",
        "facts",
        "learning",
        "knowledge",
        "documentary",
        "in-depth",
        "analysis",
        "comprehensive"
    ]
    
    # Add topic-specific variations
    words = topic.lower().split()
    for word in words:
        if len(word) > 3:
            base_tags.append(word)
    
    return base_tags[:15]  # YouTube allows up to 500 characters

def _clean_description(text: str, max_length: int = 4900) -> str:
    """Sanitize and clamp description to be valid for YouTube.

    - Remove problematic control characters
    - Ensure overall length stays safely under the 5000-char limit
    """
    if not text:
        return ""
    # Keep printable ASCII plus basic whitespace
    cleaned = ''.join(
        ch if 32 <= ord(ch) <= 126 or ch in "\n\r\t" else ' '
        for ch in text
    )
    cleaned = cleaned.strip()
    if len(cleaned) > max_length:
        cleaned = cleaned[: max_length - 3] + '...'
    return cleaned


def upload_long_video(video_file, topic, description):
    """
    Uploads a long-form video to YouTube with appropriate settings.
    """
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    creds = None
    if os.path.exists('token.pickle'):
        try:
            import sys, types
            if 'google.auth._regional_access_boundary_utils' not in sys.modules:
                mod = types.ModuleType('google.auth._regional_access_boundary_utils')
                setattr(mod, '__getattr__', lambda name: type(name, (), {'__init__': lambda self, *a, **kw: None}))
                sys.modules['google.auth._regional_access_boundary_utils'] = mod
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            print(f"⚠️  Could not load existing token.pickle ({e}). Re-authenticating...")
            creds = None
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    title = generate_engaging_title_long(topic)
    tags = generate_tags_long(topic)

    # For long-form videos, avoid dumping the full script into the
    # description. Use a short, clean template based only on the topic.
    base_description = f"In this video, we explore {topic} in a clear and engaging way, breaking it down into simple, practical insights."
    safe_description = _clean_description(base_description, max_length=800)

    # Final description shown on YouTube
    full_description = f"{safe_description}\n\n"
    full_description += "🔔 Subscribe for more educational content!\n"
    full_description += "👍 Like if you found this helpful!\n"
    full_description += "💬 Comment your thoughts below!\n\n"
    full_description += "#education #learning #knowledge #tutorial #explained"
    
    request_body = {
        'snippet': {
            'title': title,
            'description': full_description,
            'tags': tags,
            'categoryId': '27'  # Education category
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    # High-speed upload without small chunk bottleneck
    CHUNK_SIZE = -1
    MAX_RETRIES = 10

    media = MediaFileUpload(
        video_file,
        chunksize=CHUNK_SIZE,
        resumable=True,
        mimetype='video/mp4',
    )
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    )
    
    print("Starting long-form video upload...")
    file_size_mb = os.path.getsize(video_file) / (1024 * 1024)
    print(f"📦 File size: {file_size_mb:.1f} MB (high-speed upload stream)")

    response = None
    retry = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")
            retry = 0  # Reset retry counter on success
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                retry += 1
                if retry > MAX_RETRIES:
                    print(f"❌ Upload failed after {MAX_RETRIES} retries.")
                    raise
                wait = min(2 ** retry + random.random(), 60)
                print(f"⚠️  Server error ({e.resp.status}), retrying in {wait:.1f}s... (attempt {retry}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                raise
        except (httplib2.HttpLib2Error, IOError, OSError) as e:
            retry += 1
            if retry > MAX_RETRIES:
                print(f"❌ Upload failed after {MAX_RETRIES} retries due to network error.")
                raise
            wait = min(2 ** retry + random.random(), 60)
            print(f"⚠️  Network error ({type(e).__name__}), retrying in {wait:.1f}s... (attempt {retry}/{MAX_RETRIES})")
            time.sleep(wait)
    
    print(f"Upload complete! Video ID: {response['id']}")
    return response['id']
