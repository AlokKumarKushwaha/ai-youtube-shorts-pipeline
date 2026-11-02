# 🎬 AI Automated YouTube Shorts Generator

यह एक पूर्णतः स्वचालित (Fully Automated) Python पाइपलाइन है जो ताज़ा खबरों (Breaking News) को डिटेक्ट करके बिना किसी इंसानी दखल के आकर्षक हिंदी YouTube Shorts वीडियो (.mp4) तैयार करती है।

---

## ⚡ मुख्य विशेषताएँ (Features)

1. **ताज़ा ख़बरें (Latest News Ingestion):** Google News RSS से बिना किसी API Key के रियल-टाइम हिंदी व ट्रेंडिंग खबरें निकालना।
2. **AI स्क्रिप्ट राइटर (Shorts Scriptwriting):** Google Gemini के ज़रिए 35-45 सेकंड की हाई-रिटेंशन हिंदी स्क्रिप्ट, कैची हूक और सीन-वाइज़ विज़ुअल प्रॉम्प्ट्स।
3. **नेचुरल वॉइसओवर (Edge-TTS):** Microsoft Edge की हाई-डेफिनिशन प्राकृतिक भारतीय आवाज़ें (`hi-IN-MadhurNeural` - पुरुष / `hi-IN-SwaraNeural` - महिला) बिल्कुल मुफ्त।
4. **9:16 AI विज़ुअल्स (Pollinations AI):** हर सीन के लिए 1080x1920 वर्टिकल AI इमेजेज़।
5. **मोशन और सबटाइटल्स (FFmpeg):** केन-बर्न्स ज़ूम इफ़ेक्ट (हल्का मोशन) और स्क्रीन पर बोल्ड, हाई-विज़िबिलिटी हिंदी सबटाइटल्स।
6. **YouTube Auto-Upload:** YouTube Data API v3 के ज़रिए डायरेक्ट शेड्यूल या प्राइवेट/पब्लिक अपलोड।

---

## 🚀 Quick Start (कैसे चलाएं)

### 1. डायरेक्टरी में जाएँ:
```powershell
cd C:\Users\v9919\.gemini\antigravity\scratch\ai_shorts_pipeline
```

### 2. कोई भी शॉर्ट्स वीडियो जनरेट करें:

* **Tech कैटेगरी की ताज़ा खबर पर वीडियो बनाएँ:**
  ```powershell
  python main.py --category tech
  ```

* **World News (अंतर्राष्ट्रीय खबर) पर बनाएँ:**
  ```powershell
  python main.py --category world
  ```

* **किसी खास टॉपिक पर बनाएँ (जैसे ISRO, AI, क्रिकेट, आदि):**
  ```powershell
  python main.py --topic "ISRO Space Mission"
  ```

* **महिला आवाज़ (Female Voice) के साथ बनाएँ:**
  ```powershell
  python main.py --category tech --voice hi-IN-SwaraNeural
  ```

* **सीधे YouTube पर अपलोड करें:**
  ```powershell
  python main.py --category tech --upload
  ```

---

## 🔑 Configuration & API Keys (वैकल्पिक / Optional)

1. **Gemini API Key (बेहतरीन स्क्रिप्ट के लिए):**
   * अगर आप Gemini से खुद कस्टमाइज्ड स्क्रिप्ट चाहते हैं, तो Windows PowerShell में अपना की सेट करें:
     ```powershell
     $env:GEMINI_API_KEY="your_gemini_api_key_here"
     ```
   * *नोट:* यदि आप API Key नहीं डालते हैं, तो भी सिस्टम में लगा **स्मार्ट टेम्पलेट जनरेटर** काम करेगा और वीडियो तैयार कर देगा!

2. **YouTube Auto-Upload (`client_secret.json`):**
   * [Google Cloud Console](https://console.cloud.google.com/) में जाएँ।
   * **YouTube Data API v3** सक्षम (Enable) करें।
   * **OAuth 2.0 Client ID** (Desktop Application) बनाएँ और JSON डाउनलोड करें।
   * उस फ़ाइल का नाम `client_secret.json` रखकर इसी फ़ोल्डर में डाल दें।

---

## ⏰ रोज़ाना ऑटोमेशन (Daily Hands-Free Automation)

आप Windows Task Scheduler या एक लूप स्क्रिप्ट के ज़रिए इसे हर 4 घंटे में ऑटोमैटिक रन कर सकते हैं:

```powershell
# auto_runner.ps1
while ($true) {
    python main.py --category tech
    Write-Host "Waiting 4 hours for next news cycle..."
    Start-Sleep -Seconds 14400
}
```
