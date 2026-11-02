import os
import sys
import pickle
import subprocess
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import CLIENT_SECRETS_FILE, YOUTUBE_TOKEN_FILE

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

def check_or_setup_channel():
    print("\n=======================================================", flush=True)
    print("      YOUTUBE CHANNEL LIVE AUTO-UPLOAD SETUP", flush=True)
    print("=======================================================\n", flush=True)
    
    if not CLIENT_SECRETS_FILE.exists():
        print("❌ 'client_secret.json' file not found!", flush=True)
        return False

    print("✅ 'client_secret.json' found!", flush=True)
    print("[*] Opening Google login in your Chrome browser...", flush=True)
    print("[*] Please select your channel Google account and click Allow.\n", flush=True)
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
        # Use fixed port 8080 and run local server
        creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")
        
        with open(YOUTUBE_TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
            
        print("\n✅ Authentication token saved successfully!", flush=True)
        
        # Verify connection by getting channel details
        youtube = build("youtube", "v3", credentials=creds)
        request = youtube.channels().list(part="snippet,statistics", mine=True)
        response = request.execute()
        
        if "items" in response and len(response["items"]) > 0:
            channel = response["items"][0]
            ch_title = channel["snippet"]["title"]
            subs = channel["statistics"].get("subscriberCount", "0")
            print(f"\n🎉 Successfully connected to YouTube Channel: {ch_title}", flush=True)
            print(f"   Subscribers: {subs}", flush=True)
            return True
        else:
            print("Token saved! Channel is ready for automated uploads.", flush=True)
            return True
            
    except Exception as e:
        print(f"\n❌ Login process error: {e}", flush=True)
        return False

if __name__ == "__main__":
    check_or_setup_channel()
