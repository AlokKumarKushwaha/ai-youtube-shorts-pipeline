import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import imageio_ffmpeg
from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS
from studio_compositor import render_tv_studio_frame

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def get_audio_duration(audio_path: Path) -> float:
    """Returns duration of an audio file in seconds using ffmpeg."""
    cmd = [
        FFMPEG_EXE,
        "-i", str(audio_path),
        "-f", "null",
        "-"
    ]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    import re
    match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 30.0

def format_timestamp_srt(seconds: float) -> str:
    """Converts seconds into SRT timestamp format: HH:MM:SS,mmm"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def create_srt_from_timings(segments: List[Dict[str, Any]], srt_path: Path):
    """Writes timing segments directly into standard SRT format."""
    if not segments:
        return
        
    srt_lines = []
    for idx, seg in enumerate(segments, 1):
        start_ts = format_timestamp_srt(seg["start"])
        end_ts = format_timestamp_srt(seg["end"])
        srt_lines.append(f"{idx}\n{start_ts} --> {end_ts}\n{seg['text']}\n")
            
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

def compose_short_video(
    image_paths: List[Path],
    audio_path: Path,
    output_video_path: Path,
    srt_subtitles_path: Path = None,
    anchor_image_path: Optional[Path] = None,
    headline_text: str = "ताज़ा ख़बर | BREAKING NEWS",
    anchor_frames_dir: Optional[Path] = None
) -> Path:
    """
    Assembles a full-fledged TV Newsroom Studio broadcast Short:
    - Permanent professional news anchor seated at the studio desk.
    - Studio digital LED wall showing the exact relevant topic photo for each scene.
    - Breaking News lower-third ticker and channel branding.
    - Synchronized high-visibility yellow subtitles.
    """
    total_duration = get_audio_duration(audio_path)
    num_scenes = len(image_paths)
    if num_scenes == 0:
        raise ValueError("No images provided for video generation.")
        
    duration_per_scene = total_duration / num_scenes
    temp_dir = output_video_path.parent / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Render TV Studio frames for each scene
    studio_scene_files = []
    default_anchor = anchor_image_path if anchor_image_path and Path(anchor_image_path).exists() else Path("assets/anchors/male_anchor.jpg")
    
    for idx, img_path in enumerate(image_paths):
        scene_output = temp_dir / f"tv_studio_scene_{idx}.jpg"
        render_tv_studio_frame(
            topic_image_path=img_path,
            anchor_image_path=default_anchor,
            headline_text=headline_text,
            output_path=scene_output,
            is_talking=True
        )
        studio_scene_files.append(scene_output)

    # 2. Write Concat demuxer script
    concat_file = temp_dir / "input_scenes.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for sc in studio_scene_files:
            abs_p = sc.resolve().as_posix()
            f.write(f"file '{abs_p}'\n")
            f.write(f"duration {duration_per_scene:.3f}\n")
        last_abs = studio_scene_files[-1].resolve().as_posix()
        f.write(f"file '{last_abs}'\n")

    # 3. Subtitles styling: High-contrast yellow text placed between desk and ticker
    sub_style = (
        "FontName=Nirmala UI,"
        "FontSize=22,"
        "Bold=1,"
        "PrimaryColour=&H0000FFFF,"  # Bright Yellow
        "OutlineColour=&H00000000,"  # Black border
        "BorderStyle=1,"
        "Outline=3,"
        "Shadow=2,"
        "Alignment=2,"              # Bottom-Center
        "MarginV=260"               # Position above Breaking News ticker
    )

    inputs = [
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-i", str(audio_path)
    ]
    
    sub_filter = ""
    if srt_subtitles_path and srt_subtitles_path.exists():
        escaped_srt = srt_subtitles_path.resolve().as_posix().replace(":", "\\:")
        sub_filter = f",subtitles='{escaped_srt}':force_style='{sub_style}'"

    vf_chain = f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}{sub_filter}"

    cmd = [
        FFMPEG_EXE, "-y",
        *inputs,
        "-vf", vf_chain,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", f"{total_duration:.3f}",
        "-r", str(FPS),
        str(output_video_path)
    ]

    print("Executing TV News Studio FFmpeg render...", flush=True)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Notice: Subtitle pass warning, falling back without subtitle filter: {res.stderr[:200]}", flush=True)
        cmd_fallback = [
            FFMPEG_EXE, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(audio_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
            "-t", f"{total_duration:.3f}", "-r", str(FPS),
            str(output_video_path)
        ]
        subprocess.run(cmd_fallback, check=True)

    return output_video_path
