import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import random

def generate_engaging_title(topic):
    """
    Generates engaging, click-worthy titles with variety.
    Includes #Shorts for YouTube Shorts feed recognition.
    """
    title_templates = [
        # Shock & Awe
        f"🤯 {topic} Will BLOW Your Mind! #Shorts",
        f"😱 You Won't BELIEVE This About {topic}! #Shorts",
        f"⚠️ The Shocking Truth About {topic} #Shorts",
        f"🚨 WARNING: This {topic} Fact Is INSANE! #Shorts",
        f"😳 {topic}: This Will Leave You SPEECHLESS #Shorts",
        f"🤭 The {topic} Secret They're Hiding #Shorts",
        f"💀 {topic}: The Truth Is DISTURBING #Shorts",
        
        # Truth & Reality
        f"🔥 The TRUTH About {topic} #Shorts",
        f"⚡ {topic}: What They DON'T Tell You! #Shorts",
        f"💯 {topic}: What Everyone Gets WRONG #Shorts",
        f"🎯 The REAL Story Behind {topic} #Shorts",
        f"✅ {topic}: Facts vs Fiction #Shorts",
        f"🔍 The Truth Behind {topic} EXPOSED #Shorts",
        f"📢 Nobody Tells You THIS About {topic} #Shorts",
        
        # Quick & Educational
        f"💥 {topic} Explained in 30 Seconds #Shorts",
        f"⚡ {topic} in 60 Seconds #Shorts",
        f"🎯 Everything You Need to Know About {topic} #Shorts",
        f"🎬 The Ultimate {topic} Breakdown #Shorts",
        f"🧠 {topic} - The Science Explained #Shorts",
        f"📚 {topic}: The Complete Guide #Shorts",
        f"⏱️ {topic} Explained FAST #Shorts",
        
        # Superlatives & Extremes
        f"🚀 The INSANE Reality of {topic} #Shorts",
        f"🔥 This Will Change How You See {topic} #Shorts",
        f"⭐ Why {topic} Is More Important Than You Think #Shorts",
        f"💎 The MOST Important Thing About {topic} #Shorts",
        f"🏆 {topic}: The ULTIMATE Truth #Shorts",
        f"👑 The #1 Thing About {topic} Nobody Knows #Shorts",
        f"🎯 The ONLY {topic} Video You Need #Shorts",
        
        # Mystery & Intrigue
        f"✨ {topic}: The Hidden Secret #Shorts",
        f"🔐 The {topic} Mystery SOLVED #Shorts",
        f"🤫 The {topic} Secret Scientists Know #Shorts",
        f"🎭 What They Won't Tell You About {topic} #Shorts",
        f"🗝️ Unlocking the Secrets of {topic} #Shorts",
        f"👀 You've Never Seen {topic} Like THIS #Shorts",
        f"🌌 The Dark Side of {topic} #Shorts",
        
        # Questions & Curiosity
        f"❓ What If {topic} Is Actually... #Shorts",
        f"🤔 Why Does {topic} Even Exist? #Shorts",
        f"💭 Ever Wonder About {topic}? #Shorts",
        f"🧐 How Does {topic} Really Work? #Shorts",
        f"⁉️ Is {topic} Real or Fake? #Shorts",
        f"🎯 Can {topic} Actually Happen? #Shorts",
        
        # Viral & Trending
        f"🌟 {topic} - Mind Blowing Facts! #Shorts",
        f"🔥 {topic} Is Going VIRAL For This Reason #Shorts",
        f"📈 Why Everyone Is Talking About {topic} #Shorts",
        f"💫 {topic}: The Viral Sensation Explained #Shorts",
        f"🎪 This {topic} Fact Broke the Internet #Shorts",
        f"🌍 {topic}: Why It's Trending Worldwide #Shorts",
        
        # Personal & Relatable
        f"😮 I Didn't Know This About {topic}! #Shorts",
        f"🙀 {topic} Changed My Perspective Forever #Shorts",
        f"💡 This {topic} Fact Blew My Mind #Shorts",
        f"🎓 What I Learned About {topic} Today #Shorts",
        
        # Challenges & Comparisons
        f"⚔️ {topic} vs Reality: You Decide #Shorts",
        f"🥊 The Battle of {topic} #Shorts",
        f"📊 {topic}: Before vs After #Shorts",
        f"🎭 Myths About {topic} BUSTED #Shorts"
    ]
    return random.choice(title_templates)

def generate_hashtags(topic):
    """
    Generates relevant hashtags for better discoverability.
    """
    # Base hashtags for YouTube Shorts
    base_tags = ["shorts", "viral", "trending", "fyp", "educational", "facts", "mindblowing"]
    
    # Topic-specific tags
    topic_words = topic.lower().replace("the ", "").replace("a ", "").split()
    topic_tags = [word for word in topic_words if len(word) > 3]
    
    # Combine and format
    all_tags = base_tags + topic_tags[:3]
    hashtags = " ".join([f"#{tag}" for tag in all_tags])
    
    return hashtags

def generate_rich_description(topic, script_preview):
    """
    Creates engaging descriptions with emojis and calls-to-action.
    """
    emojis = ["🔥", "⚡", "✨", "🌟", "💡", "🚀", "🎯", "💯"]
    emoji = random.choice(emojis)
    
    # Get first 100 characters of script as preview
    preview = script_preview[:100] + "..." if len(script_preview) > 100 else script_preview
    
    description = f"""{emoji} Discover the fascinating world of {topic}!

{preview}

🎬 Welcome to AI-powered educational content that makes learning fun and engaging!

📌 What's in this video:
• Quick facts about {topic}
• Mind-blowing insights
• Easy-to-understand explanations

💬 Let us know what you think in the comments!
👍 Like if you learned something new
🔔 Subscribe for more amazing content
📤 Share with someone who needs to see this!

⚡ New videos posted regularly - stay tuned!

#Shorts {generate_hashtags(topic)}

---
🤖 Created with AI-powered automation
🎥 Professional stock footage
🎵 Copyright-free music
"""
    return description

def upload_to_youtube(video_file, topic, script_text):
    """
    Uploads a video to YouTube with engaging metadata.
    """
    # Generate engaging metadata
    title = generate_engaging_title(topic)
    description = generate_rich_description(topic, script_text)
    
    # Generate tags for better discoverability
    topic_words = topic.lower().replace("the ", "").replace("a ", "").split()
    tags = ["shorts", "viral", "trending", "educational", "facts", topic] + topic_words[:3]
    
    CLIENT_SECRET_FILE = 'client_secret.json'
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    youtube = build(API_NAME, API_VERSION, credentials=credentials)

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '28' # Science & Technology
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print(f"📺 Video uploaded successfully!")
    print(f"📌 Title: {title}")
    print(f"🏷️ Tags: {', '.join(tags[:5])}")
    return response.get('id')
