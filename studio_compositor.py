import os
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance

from config import VIDEO_WIDTH, VIDEO_HEIGHT, ASSETS_DIR

FONT_PATH = "C:/Windows/Fonts/Nirmala.ttc"
FONT_BOLD_PATH = "C:/Windows/Fonts/NirmalaB.ttf" if os.path.exists("C:/Windows/Fonts/NirmalaB.ttf") else FONT_PATH

def get_fonts():
    try:
        font_header = ImageFont.truetype(FONT_PATH, 32)
        font_live = ImageFont.truetype(FONT_BOLD_PATH, 28)
        font_tag = ImageFont.truetype(FONT_BOLD_PATH, 24)
        font_breaking = ImageFont.truetype(FONT_BOLD_PATH, 34)
        font_headline = ImageFont.truetype(FONT_BOLD_PATH, 36)
        return font_header, font_live, font_tag, font_breaking, font_headline
    except Exception:
        default = ImageFont.load_default()
        return default, default, default, default, default

def render_tv_studio_frame(
    topic_image_path: Optional[Path],
    anchor_image_path: Path,
    headline_text: str,
    output_path: Path,
    is_talking: bool = False,
    channel_name: str = "QUICK NEWS HINDI",
    width: int = VIDEO_WIDTH,
    height: int = VIDEO_HEIGHT
) -> Path:
    """
    Renders a realistic TV Newsroom Studio broadcast frame:
    1. Background Studio Lighting & Set Panels
    2. Studio LED Video Wall showing the exact news topic visual
    3. News Anchor seated at the modern illuminated desk
    4. Speech-reactive animation
    5. Professional TV Lower-Third Breaking News Ticker and Header
    """
    font_header, font_live, font_tag, font_breaking, font_headline = get_fonts()
    
    frame = Image.new("RGB", (width, height), color=(10, 14, 26))
    draw = ImageDraw.Draw(frame)

    # 1. Studio Backdrop (Deep Navy with atmospheric lighting)
    for y in range(height):
        factor = y / height
        r = int(10 + factor * 22)
        g = int(14 + factor * 20)
        b = int(28 + factor * 48)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Studio background architectural grid lines
    for x in range(60, width, 120):
        draw.line([(x, 0), (x, 900)], fill=(22, 36, 65))
    for y in range(80, 850, 100):
        draw.line([(0, y), (width, y)], fill=(18, 30, 55))

    # 2. Studio LED Video Wall Screen (Upper Section: y=160 to y=760)
    sw_x1, sw_y1 = 80, 160
    sw_w, sw_h = 920, 580
    sw_x2, sw_y2 = sw_x1 + sw_w, sw_y1 + sw_h

    # Glowing screen bezel
    draw.rounded_rectangle([sw_x1 - 10, sw_y1 - 10, sw_x2 + 10, sw_y2 + 10], radius=18, fill=(35, 55, 95))
    draw.rounded_rectangle([sw_x1 - 4, sw_y1 - 4, sw_x2 + 4, sw_y2 + 4], radius=14, fill=(16, 24, 42))

    # Embed Topic Photo inside the LED wall
    if topic_image_path and Path(topic_image_path).exists():
        try:
            with Image.open(topic_image_path) as topic_img:
                topic_img = topic_img.convert("RGB")
                fitted_topic = ImageOps.fit(topic_img, (sw_w, sw_h), centering=(0.5, 0.5))
                # Slight studio contrast boost
                enhancer = ImageEnhance.Contrast(fitted_topic)
                fitted_topic = enhancer.enhance(1.1)
                frame.paste(fitted_topic, (sw_x1, sw_y1))
        except Exception:
            pass

    # Video Wall Header Tag ("TOP STORY / बड़ी ख़बर")
    draw.rounded_rectangle([sw_x1 + 24, sw_y1 + 20, sw_x1 + 210, sw_y1 + 64], radius=6, fill=(220, 20, 20))
    draw.text((sw_x1 + 38, sw_y1 + 26), "बड़ी ख़बर", font=font_tag, fill=(255, 255, 255))

    # 3. Top Broadcast Header Bar
    draw.rectangle([0, 0, width, 120], fill=(12, 16, 30))
    # Red LIVE badge
    draw.rounded_rectangle([40, 30, 170, 86], radius=8, fill=(220, 20, 20))
    draw.text((64, 40), "🔴 LIVE", font=font_live, fill=(255, 255, 255))
    # Channel Name & Bulletin
    draw.text((200, 42), f"{channel_name} | स्पेशल रिपोर्ट", font=font_header, fill=(245, 245, 255))
    draw.line([(0, 120), (width, 120)], fill=(0, 210, 255), width=3) # Cyan neon line

    # 4. News Anchor Seated (Center: y=700 to y=1400)
    anchor_w, anchor_h = 750, 700
    if Path(anchor_image_path).exists():
        try:
            with Image.open(anchor_image_path) as anchor_raw:
                anchor_raw = anchor_raw.convert("RGB")
                # When talking, micro-scale (+2%) for dynamic speech presence
                if is_talking:
                    anchor_raw = anchor_raw.resize((int(anchor_raw.width * 1.02), int(anchor_raw.height * 1.02)), Image.Resampling.LANCZOS)

                anchor_cropped = ImageOps.fit(anchor_raw, (anchor_w, anchor_h), centering=(0.5, 0.2))
                ax = (width - anchor_w) // 2
                ay = 720
                frame.paste(anchor_cropped, (ax, ay))
        except Exception as e:
            print(f"Notice: Anchor paste failed: {e}")

    # 5. Illuminated Newsroom Anchor Desk (in front of anchor's lower torso)
    desk_y = 1340
    # Glass / Metallic curved surface
    draw.ellipse([30, desk_y - 60, width - 30, desk_y + 360], fill=(16, 22, 38))
    # Glowing neon studio rim lines (Cyan & Gold)
    draw.arc([30, desk_y - 60, width - 30, desk_y + 360], start=188, end=352, fill=(0, 220, 255), width=8)
    draw.arc([60, desk_y - 45, width - 60, desk_y + 330], start=193, end=347, fill=(255, 215, 0), width=4)

    # Broadcast gooseneck studio microphone
    mx, my = 540, 1260
    draw.line([(mx, my + 80), (mx - 25, my + 30), (mx - 15, my)], fill=(70, 75, 85), width=6)
    draw.ellipse([mx - 26, my - 16, mx - 4, my + 6], fill=(25, 25, 30))

    # 6. Lower-Third Breaking News Ticker (Bottom: y=1680 to y=1920)
    # Upper Red Breaking Banner
    draw.rectangle([0, 1680, width, 1750], fill=(210, 20, 20))
    draw.text((40, 1692), "🔴 BREAKING NEWS | ताज़ा तरीन ख़बरें", font=font_breaking, fill=(255, 255, 255))

    # Lower Navy Headline Container
    draw.rectangle([0, 1750, width, 1920], fill=(10, 16, 28))
    draw.line([(0, 1750), (width, 1750)], fill=(255, 215, 0), width=4) # Gold divider

    # Headline Text (Truncated gracefully if too long)
    clean_h = headline_text.split(" - ")[0].strip()
    if len(clean_h) > 55:
        clean_h = clean_h[:52] + "..."
    draw.text((40, 1780), clean_h, font=font_headline, fill=(255, 255, 255))

    frame.save(output_path, quality=95)
    return output_path

if __name__ == "__main__":
    out_test = Path("assets/studio/test_tv_studio_frame.jpg")
    render_tv_studio_frame(
        topic_image_path=Path("output/short_1793355516/scene_1.jpg"),
        anchor_image_path=Path("assets/anchors/male_anchor.jpg"),
        headline_text="Apple के सबसे सस्ते MacBook पर बंपर डील, कई हजार की सेविंग!",
        output_path=out_test,
        is_talking=True
    )
    print(f"Generated test TV studio frame: {out_test}")
