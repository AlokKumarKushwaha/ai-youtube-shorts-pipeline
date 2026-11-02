import math
import struct
import wave
import subprocess
import urllib.parse
import re
import io
from pathlib import Path
from typing import Tuple, Optional
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance
import imageio_ffmpeg
from config import ASSETS_DIR

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
ANCHOR_DIR = ASSETS_DIR / "anchors"
ANCHOR_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def download_real_anchor_portrait(gender: str = "male") -> Path:
    """
    Downloads a high-definition real portrait of an Indian news anchor
    using web search if not already present.
    """
    anchor_file = ANCHOR_DIR / f"{gender}_anchor.jpg"
    if anchor_file.exists() and anchor_file.stat().st_size > 20000:
        return anchor_file

    queries = [
        f"Indian {gender} TV news anchor formal suit studio portrait",
        f"Indian {gender} news broadcast journalist portrait studio",
        f"Indian {gender} corporate formal portrait"
    ]
    
    for q in queries:
        url = f"https://www.bing.com/images/search?q={urllib.parse.quote(q)}&form=HDRSC2&first=1"
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            matches = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', r.text)
            for m in matches[:5]:
                try:
                    res = requests.get(m, headers=HEADERS, timeout=8)
                    if res.status_code == 200 and len(res.content) > 20000:
                        img = Image.open(io.BytesIO(res.content)).convert("RGB")
                        if img.width >= 350 and img.height >= 350:
                            img.save(anchor_file, quality=95)
                            print(f"[+] Downloaded real {gender} anchor portrait: {img.size}")
                            return anchor_file
                except Exception:
                    continue
        except Exception as e:
            print(f"Notice: Web search for anchor portrait failed: {e}")

    # Fallback to AI generation
    try:
        poll_url = f"https://image.pollinations.ai/prompt/Indian%20{gender}%20news%20anchor%20portrait?model=sana&width=512&height=512&nologo=true"
        r = requests.get(poll_url, headers=HEADERS, timeout=15)
        if r.status_code == 200 and len(r.content) > 15000:
            with open(anchor_file, "wb") as f:
                f.write(r.content)
            return anchor_file
    except Exception:
        pass

    return anchor_file

# Backward compatibility alias
generate_default_anchor_portrait = download_real_anchor_portrait

def extract_audio_amplitudes(audio_path: Path, fps: int = 30) -> list:

    """
    Computes RMS audio amplitude per video frame to synchronize avatar reactive speech.
    """
    temp_wav = audio_path.parent / "temp_audio.wav"
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", str(audio_path),
        "-ac", "1",
        "-ar", "16000",
        "-f", "wav",
        str(temp_wav)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    with wave.open(str(temp_wav), "rb") as wf:
        n_frames = wf.getnframes()
        raw_data = wf.readframes(n_frames)
        framerate = wf.getframerate()
        
    temp_wav.unlink(missing_ok=True)
    
    samples = struct.unpack(f"<{n_frames}h", raw_data)
    samples_per_frame = int(framerate / fps)
    
    amplitudes = []
    for i in range(0, len(samples), samples_per_frame):
        chunk = samples[i : i + samples_per_frame]
        if not chunk:
            break
        rms = math.sqrt(sum(s * s for s in chunk) / len(chunk))
        amplitudes.append(rms)
        
    max_amp = max(amplitudes) if amplitudes and max(amplitudes) > 0 else 1
    return [round(a / max_amp, 3) for a in amplitudes]

def create_circular_avatar(img_path: Path, size: int = 360, is_talking: bool = False) -> Image.Image:
    """
    Creates a broadcast news circular avatar badge with glowing live border.
    When talking, applies subtle energetic scale and high-intensity broadcast outline.
    """
    with Image.open(img_path) as orig_img:
        orig_img = orig_img.convert("RGBA")
        
        # Center on face (upper 30%)
        cropped = ImageOps.fit(orig_img, (size, size), centering=(0.5, 0.25))
        
        # Render canvas
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        
        # Create circular mask
        mask = Image.new("L", (size, size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((6, 6, size - 6, size - 6), fill=255)
        
        # News broadcast border (Vibrant Red/Gold when talking, Clean Red when idle)
        border_color = (255, 30, 30, 255) if not is_talking else (255, 215, 0, 255)
        border_width = 7 if not is_talking else 9
        
        # Composite masked face
        face_circle = Image.composite(cropped, Image.new("RGBA", (size, size), (0, 0, 0, 0)), mask)
        canvas.paste(face_circle, (0, 0), face_circle)
        
        # Draw broadcast ring
        draw_border = ImageDraw.Draw(canvas)
        draw_border.ellipse((3, 3, size - 3, size - 3), outline=border_color, width=border_width)
        
        # 'LIVE' badge indicator on bottom of avatar
        badge_w, badge_h = 70, 24
        bx = (size - badge_w) // 2
        by = size - badge_h - 4
        draw_border.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=6, fill=(220, 20, 20, 255))
        
        return canvas

def generate_talking_anchor_frames(
    anchor_image_path: Path,
    audio_path: Path,
    output_dir: Path,
    fps: int = 30,
    avatar_size: int = 360
) -> Tuple[Path, int]:
    """
    Generates video frames of the talking anchor badge synchronized to speech volume.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    amplitudes = extract_audio_amplitudes(audio_path, fps=fps)
    
    avatar_idle = create_circular_avatar(anchor_image_path, size=avatar_size, is_talking=False)
    avatar_active = create_circular_avatar(anchor_image_path, size=avatar_size, is_talking=True)
    
    threshold = 0.20
    frame_dir = output_dir / "anchor_frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    
    for idx, amp in enumerate(amplitudes):
        frame_file = frame_dir / f"frame_{idx:05d}.png"
        # Alternate talking state when speaking
        if amp > threshold and (idx % 3 != 0):
            avatar_active.save(frame_file)
        else:
            avatar_idle.save(frame_file)
            
    return frame_dir, len(amplitudes)

if __name__ == "__main__":
    p = download_real_anchor_portrait("male")
    print(f"Verified anchor portrait at: {p}")
