import json
import re
from typing import Dict, Any
from config import GEMINI_API_KEY

def build_prompt(news_title: str, news_desc: str) -> str:
    return f"""
You are a viral YouTube Shorts scriptwriter specializing in fast-paced, high-retention Hindi news videos.

Given the following news story:
HEADLINE: {news_title}
SUMMARY: {news_desc}

Create a 35 to 45-second high-energy Hindi Shorts script divided into 4-5 dynamic visual scenes.

REQUIREMENTS:
1. Hook (Scene 1): Immediate curiosity or shocking fact (0-3 sec). Never start with "Namaste" or "Welcome".
2. Story (Scenes 2-4): Clear, simple explanation of what happened, why it matters. Keep sentences punchy.
3. Outro (Last Scene): Fast call to action ("वीडियो को लाइक और सब्सक्राइब जरूर करें!").
4. Language: Natural, conversational Hindi / Hinglish that sounds great when spoken aloud.
5. Image Prompts: In English, photorealistic, cinematic lighting, 9:16 vertical framing, describing what to visualize.

Return ONLY a valid JSON object with the following schema:
{{
  "youtube_title": "Catchy YouTube Title under 60 chars #Shorts #News",
  "youtube_description": "Engaging description with relevant hashtags #Shorts #BreakingNews",
  "tags": ["news", "shorts", "trending", "india"],
  "full_speech": "The complete combined Hindi speech to be spoken by TTS without any pauses or markdown",
  "scenes": [
    {{
      "scene_num": 1,
      "speech_chunk": "Scene 1 spoken Hindi text...",
      "image_prompt": "Cinematic visual description in English for image generation...",
      "overlay_keyword": "2-3 WORDS TO HIGHLIGHT"
    }}
  ]
}}
"""

def generate_script_with_gemini(news_title: str, news_desc: str, api_key: str = GEMINI_API_KEY) -> Dict[str, Any]:
    """Generates an engaging Shorts script using Gemini API."""
    if not api_key:
        print("[Notice] GEMINI_API_KEY is not set. Generating using smart template fallback...")
        return generate_fallback_script(news_title, news_desc)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = build_prompt(news_title, news_desc)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        raw_text = response.text.strip()
        # Clean potential markdown fences ```json ... ```
        clean_json = re.sub(r"^```json\s*", "", raw_text)
        clean_json = re.sub(r"\s*```$", "", clean_json)
        
        data = json.loads(clean_json)
        return data
    except Exception as e:
        print(f"[Warning] Gemini API call failed: {e}. Falling back to template script...")
        return generate_fallback_script(news_title, news_desc)

def generate_fallback_script(news_title: str, news_desc: str) -> Dict[str, Any]:
    """Creates a high-quality script template when no API key is present."""
    clean_title = news_title.split(" - ")[0].strip()
    speech = f"क्या आप जानते हैं? {clean_title}! जी हाँ, हाल ही में आई ताज़ा रिपोर्ट के मुताबिक यह बड़ी खबर सामने आई है। {news_desc[:120]}। ऐसी ही ताज़ा और दिलचस्प जानकारियों के लिए हमारे चैनल को अभी सब्सक्राइब करें!"
    
    return {
        "youtube_title": f"{clean_title[:50]}! #Shorts #News",
        "youtube_description": f"{clean_title}\n\nताज़ा ख़बरों के लिए चैनल सब्सक्राइब करें! #Shorts #News #Trending",
        "tags": ["news", "shorts", "trending", "breakingnews", "india"],
        "full_speech": speech,
        "scenes": [
            {
                "scene_num": 1,
                "speech_chunk": f"क्या आप जानते हैं? {clean_title}!",
                "image_prompt": f"Dramatic breaking news broadcast studio with neon digital holographic displays, concept art: {clean_title}",
                "overlay_keyword": "बड़ी खबर!"
            },
            {
                "scene_num": 2,
                "speech_chunk": f"जी हाँ, हाल ही में आई ताज़ा रिपोर्ट के मुताबिक यह बड़ी खबर सामने आई है।",
                "image_prompt": f"Futuristic technology visual or global news map, 8k realistic: {clean_title}",
                "overlay_keyword": "ताज़ा रिपोर्ट"
            },
            {
                "scene_num": 3,
                "speech_chunk": f"{news_desc[:120] if news_desc else 'इस नए अपडेट से दुनिया भर में काफी चर्चा हो रही है।'}",
                "image_prompt": f"Detailed cinematic close up representing the event: {clean_title}",
                "overlay_keyword": "पूरी सच्चाई"
            },
            {
                "scene_num": 4,
                "speech_chunk": "ऐसी ही ताज़ा और दिलचस्प जानकारियों के लिए हमारे चैनल को अभी सब्सक्राइब करें!",
                "image_prompt": "Sleek YouTube subscription screen with notification bell, modern 3d render, dark aesthetic",
                "overlay_keyword": "सब्सक्राइब करें"
            }
        ]
    }

if __name__ == "__main__":
    sample = generate_fallback_script("ISRO ने लॉन्च किया नया मौसम उपग्रह", "भारतीय अंतरिक्ष अनुसंधान संगठन ने श्रीहरिकोटा से नया उपग्रह सफलता पूर्वक भेजा।")
    print("Sample Script Output:")
    print(json.dumps(sample, ensure_ascii=False, indent=2))
