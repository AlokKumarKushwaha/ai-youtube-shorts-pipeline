import os
import sys
import pickle
import socket
from pathlib import Path
from typing import List, Dict, Any, Optional

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Force IPv4 resolution to prevent WinError 10060 timeouts on networks with broken IPv6
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(*args, **kwargs):
    res = _orig_getaddrinfo(*args, **kwargs)
    ipv4_res = [r for r in res if r[0] == socket.AF_INET]
    return ipv4_res if ipv4_res else res
socket.getaddrinfo = _ipv4_getaddrinfo



from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import CLIENT_SECRETS_FILE, YOUTUBE_TOKEN_FILE, YOUTUBE_PRIVACY_STATUS

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """Authenticates using client_secret.json and caches the token."""
    creds = None
    if YOUTUBE_TOKEN_FILE.exists():
        with open(YOUTUBE_TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRETS_FILE.exists():
                raise FileNotFoundError(
                    f"'{CLIENT_SECRETS_FILE}' not found! "
                    "To enable automatic YouTube upload:\n"
                    "1. Go to https://console.cloud.google.com/\n"
                    "2. Enable YouTube Data API v3\n"
                    "3. Create OAuth 2.0 Client IDs (Desktop application)\n"
                    "4. Download JSON and rename it to 'client_secret.json' in this folder."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(YOUTUBE_TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
            
    return build("youtube", "v3", credentials=creds)

def upload_short_to_youtube(
    video_path: Path,
    title: str,
    description: str,
    tags: List[str] = None,
    privacy_status: str = YOUTUBE_PRIVACY_STATUS,
    category_id: str = "25"  # 25 = News & Politics, 28 = Science & Tech
) -> Dict[str, Any]:
    """
    Uploads a video to YouTube as a Short.
    Returns details including the YouTube Short URL.
    """
    if tags is None:
        tags = ["shorts", "news", "trending"]
        
    # Ensure title contains #Shorts for YouTube algorithm optimization
    if "#shorts" not in title.lower():
        title = f"{title[:85]} #Shorts"

    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    file_size_mb = os.path.getsize(str(video_path)) / (1024 * 1024)
    print(f"Uploading '{video_path.name}' ({file_size_mb:.1f} MB) to YouTube ({privacy_status})...", flush=True)

    if file_size_mb < 15:
        # Fast direct single-request upload for Shorts
        media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=False)
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )
        response = request.execute()
    else:
        # Resumable multi-chunk for larger files
        media = MediaFileUpload(str(video_path), chunksize=1024 * 1024 * 2, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%", flush=True)



    video_id = response.get("id")
    short_url = f"https://youtube.com/shorts/{video_id}"
    print(f"Upload complete! Video URL: {short_url}")
    
    return {
        "video_id": video_id,
        "url": short_url,
        "title": title,
        "status": privacy_status
    }
