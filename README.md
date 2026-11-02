# 🎬 AI Automated YouTube Shorts Generator

A fully automated, end-to-end Python pipeline that detects trending breaking news, crafts viral YouTube Shorts scripts, synthesizes natural neural voiceovers, composes high-definition 9:16 vertical videos with TV newsroom studio visuals & dynamic subtitles, and automatically publishes them directly to your YouTube channel.

---

## ✨ Features

- **🌐 Automated News Ingestion:** Fetches real-time breaking news across multiple categories (Tech, World, Business, Sports, Entertainment) via Google News RSS feeds with smart deduplication.
- **✍️ AI Scriptwriter:** Generates 35–45 second high-retention Shorts scripts with punchy opening hooks and scene-by-scene visual descriptions using Google Gemini.
- **🎙️ Neural Voiceover (Edge-TTS):** High-definition, human-like voice synthesis using Microsoft Edge neural voices (`hi-IN-MadhurNeural` for male, `hi-IN-SwaraNeural` for female) with exact word and sentence boundary timing.
- **📺 TV Newsroom Studio Layout:** Professional 1080x1920 broadcast layout featuring:
  - Studio news desk with anchor persona and microphone.
  - Digital LED video wall screen showcasing authentic, high-resolution topic imagery.
  - Dynamic Breaking News lower-third ticker and channel branding.
- **💬 Auto-Styled Subtitles:** High-contrast, center-aligned dynamic subtitles burned directly into the video stream using FFmpeg.
- **🚀 Hands-Free YouTube Publishing:** Direct, resumable video uploading via YouTube Data API v3 with automated titles, descriptions, and hashtags (`#Shorts`, `#News`, `#Trending`).
- **⏰ 24/7 Autopilot Mode:** Built-in scheduling and loop support to automatically post new videos every few hours without manual intervention.

---

## 📁 Project Structure

```
ai-youtube-shorts-pipeline/
├── config.py             # System configuration, paths, video specs & voice settings
├── news_fetcher.py       # Google News RSS fetcher with deduplication
├── script_generator.py   # Gemini AI script & scene prompt generator
├── voice_generator.py    # Edge-TTS voiceover synthesizer with timestamp tracking
├── visual_generator.py   # Multi-tier HD photo search (Bing / Wikimedia / AI)
├── studio_compositor.py  # TV Newsroom Studio frame compositor
├── video_composer.py     # FFmpeg video assembler & subtitle burner
├── youtube_uploader.py   # YouTube Data API v3 OAuth2 automated uploader
├── setup_youtube.py      # Interactive one-time YouTube OAuth setup wizard
├── main.py               # Main CLI orchestrator
├── Login_YouTube.bat     # 1-Click desktop YouTube login wizard
├── Start_Auto_YouTube.bat# 1-Click 24/7 background autopilot loop
└── requirements.txt      # Python dependencies
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/AlokKumarKushwaha/ai-youtube-shorts-pipeline.git
cd ai-youtube-shorts-pipeline
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate a Short Video

- **Latest Technology News:**
  ```bash
  python main.py --category tech
  ```

- **International / World News:**
  ```bash
  python main.py --category world
  ```

- **Custom Topic (e.g. Space, AI, Sports):**
  ```bash
  python main.py --topic "ISRO Moon Mission"
  ```

- **With Female Anchor & Voice:**
  ```bash
  python main.py --category tech --anchor female --voice hi-IN-SwaraNeural
  ```

- **Generate and Auto-Upload to YouTube:**
  ```bash
  python main.py --category tech --upload
  ```

---

## 🔑 YouTube Auto-Upload Setup (One-Time)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **YouTube Data API v3**.
3. Navigate to **Credentials** > **Create Credentials** > **OAuth Client ID**:
   - Application Type: **Desktop app**
   - Click **Create** and click **Download JSON**.
4. Rename the downloaded file to `client_secret.json` and place it in the project root folder.
5. Run the authentication wizard:
   ```bash
   python setup_youtube.py
   ```
   *Your browser will open asking you to sign in with your YouTube channel account and grant upload permissions. Once authorized, the credentials are permanently cached in `youtube_token.pickle`.*

---

## 🤖 24/7 Autopilot Mode

To continuously generate and post fresh breaking news videos every 4 hours automatically:

- **Windows 1-Click:** Double-click `Start_Auto_YouTube.bat`.
- **PowerShell / Terminal:**
  ```powershell
  while ($true) {
      python main.py --category tech --upload
      Write-Host "Waiting 4 hours for next news cycle..."
      Start-Sleep -Seconds 14400
  }
  ```

---

## ⚙️ Environment Variables (Optional)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API key for advanced scriptwriting | Smart template fallback if unset |
| `TTS_VOICE` | Default Edge-TTS voice model | `hi-IN-MadhurNeural` |
| `YOUTUBE_PRIVACY` | Upload status (`public`, `unlisted`, `private`) | `public` |

---

## 📄 License

This project is licensed under the MIT License - feel free to customize and expand it for your own automated channels.
