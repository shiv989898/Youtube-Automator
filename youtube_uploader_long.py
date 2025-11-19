import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import random

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

def upload_long_video(video_file, topic, description):
    """
    Uploads a long-form video to YouTube with appropriate settings.
    """
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
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
    
    # Enhanced description for long-form content
    full_description = f"{description}\n\n"
    full_description += f"In this video, we explore {topic} in detail, covering all the important aspects and providing you with comprehensive information.\n\n"
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
    
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype='video/mp4')
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    )
    
    print("Starting long-form video upload...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    
    print(f"Upload complete! Video ID: {response['id']}")
    return response['id']
