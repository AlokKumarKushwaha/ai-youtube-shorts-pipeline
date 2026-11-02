import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
FONTS_DIR = ASSETS_DIR / "fonts"

# Ensure essential directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# API Keys (Loaded from environment or fallback)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Video Specs (9:16 vertical for YouTube Shorts / Instagram Reels)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# Voiceover Configuration (Edge-TTS)
# Options: "hi-IN-MadhurNeural" (Male), "hi-IN-SwaraNeural" (Female)
VOICE_NAME = os.getenv("TTS_VOICE", "hi-IN-MadhurNeural")
VOICE_RATE = "+5%"  # Slightly faster for fast-paced shorts

# YouTube Upload Config
CLIENT_SECRETS_FILE = BASE_DIR / "client_secret.json"
YOUTUBE_TOKEN_FILE = BASE_DIR / "youtube_token.pickle"
YOUTUBE_PRIVACY_STATUS = os.getenv("YOUTUBE_PRIVACY", "public")  # "public", "unlisted", "private"

