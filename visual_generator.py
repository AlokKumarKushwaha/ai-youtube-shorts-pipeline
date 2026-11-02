import urllib.parse
import re
import io
import time
from pathlib import Path
from typing import Optional
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps

from config import VIDEO_WIDTH, VIDEO_HEIGHT

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def clean_query(text: str) -> str:
    """Extracts clean English/alphanumeric keywords from prompts for reliable image search."""
    # Remove special characters and common noise words
    cleaned = re.sub(r"[^\w\s-]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    words = cleaned.split()
    # Limit to top 5-6 key words for high search relevance
    return " ".join(words[:6])

def format_to_vertical_short(img: Image.Image, width: int = VIDEO_WIDTH, height: int = VIDEO_HEIGHT) -> Image.Image:
    """
    Transforms any image (landscape, square, or portrait) into a professional 9:16 Short.
    Uses cinematic blurred background + centered crisp foreground (Industry standard).
    """
    img = img.convert("RGB")
    aspect_target = width / height
    aspect_img = img.width / img.height

    if abs(aspect_img - aspect_target) < 0.1:
        # Already near 9:16, directly fit
        return ImageOps.fit(img, (width, height), centering=(0.5, 0.5))

    # 1. Blurred and slightly dimmed background
    bg = ImageOps.fit(img, (width, height), centering=(0.5, 0.5))
    bg = bg.filter(ImageFilter.GaussianBlur(35))
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.5)

    # 2. Foreground crisp image scaled to width
    fg_w = width
    fg_h = int(width / aspect_img)
    if fg_h > height:
        fg_h = height
        fg_w = int(height * aspect_img)

    fg = img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
    
    # Optional subtle border around foreground
    y_pos = (height - fg_h) // 2
    x_pos = (width - fg_w) // 2
    bg.paste(fg, (x_pos, y_pos))
    return bg

def fetch_from_web_bing(query: str) -> Optional[Image.Image]:
    """Fast, reliable web image search returning real HD photos with zero API key."""
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&form=HDRSC2&first=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        matches = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', r.text)
        for img_url in matches[:4]:
            try:
                res = requests.get(img_url, headers=HEADERS, timeout=7)
                if res.status_code == 200 and len(res.content) > 15000:
                    img = Image.open(io.BytesIO(res.content))
                    if img.width >= 350 and img.height >= 250:
                        return img
            except Exception:
                continue
    except Exception as e:
        print(f"Notice: Bing search error: {e}")
    return None

def fetch_from_wikimedia(query: str) -> Optional[Image.Image]:
    """Fetches high-resolution Creative Commons news/topic photos from Wikimedia."""
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit=3&prop=imageinfo&iiprop=url|mime&format=json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        pages = r.json().get("query", {}).get("pages", {})
        for _, v in pages.items():
            info = v.get("imageinfo", [{}])[0]
            mime = info.get("mime", "")
            if "image/jpeg" in mime or "image/png" in mime:
                img_url = info.get("url")
                res = requests.get(img_url, headers=HEADERS, timeout=8)
                if res.status_code == 200 and len(res.content) > 15000:
                    return Image.open(io.BytesIO(res.content))
    except Exception as e:
        print(f"Notice: Wikimedia search error: {e}")
    return None

def fetch_from_pollinations(prompt: str) -> Optional[Image.Image]:
    """Fetches AI generated image from Pollinations AI (Flux/Sana)."""
    encoded = urllib.parse.quote(prompt[:80])
    url = f"https://image.pollinations.ai/prompt/{encoded}?model=sana&width=512&height=512&nologo=true"
    try:
        res = requests.get(url, headers=HEADERS, timeout=20)
        if res.status_code == 200 and len(res.content) > 15000:
            return Image.open(io.BytesIO(res.content))
    except Exception:
        pass
    return None

def generate_ai_image(prompt: str, output_path: Path, width: int = VIDEO_WIDTH, height: int = VIDEO_HEIGHT, topic_context: str = "") -> bool:
    """
    Robust multi-tier image generator:
    1. Searches real HD web photo for the scene / topic.
    2. Falls back to Wikimedia Commons news archive.
    3. Falls back to Pollinations AI image generation.
    4. Formats cleanly into professional 1080x1920 vertical Short format.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    search_terms = []
    
    # Extract clean search keywords
    if prompt:
        search_terms.append(clean_query(prompt))
    if topic_context:
        search_terms.append(clean_query(topic_context))
        
    search_terms.append("breaking news television studio broadcast")
    
    photo = None
    for term in search_terms:
        if not term:
            continue
        # 1. Try Bing Real Photos
        photo = fetch_from_web_bing(term)
        if photo:
            break
        # 2. Try Wikimedia
        photo = fetch_from_wikimedia(term)
        if photo:
            break

    # 3. Try Pollinations AI if no web photo found
    if not photo:
        print("  -> Fetching AI generated visual...")
        photo = fetch_from_pollinations(prompt)

    # 4. If all failed, generate sleek news graphic card
    if not photo:
        print("  -> Creating graphic news card...")
        photo = Image.new("RGB", (width, height), color=(20, 25, 40))
        draw = ImageDraw.Draw(photo)
        draw.rectangle([(40, 40), (width - 40, height - 40)], outline=(220, 40, 40), width=6)
    
    # Format and save
    vertical_img = format_to_vertical_short(photo, width=width, height=height)
    vertical_img.save(output_path, quality=95)
    return True

if __name__ == "__main__":
    test_out = Path("./test_output/test_real_photo.jpg")
    print("Testing robust photo generation...")
    generate_ai_image("Apple MacBook Pro Touchscreen launch", test_out, topic_context="Apple MacBook")
    print(f"Saved real photo to: {test_out}")
