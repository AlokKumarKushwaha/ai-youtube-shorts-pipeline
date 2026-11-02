import asyncio
import json
import sys
from pathlib import Path
import edge_tts
from config import VOICE_NAME, VOICE_RATE

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def generate_speech_async(text: str, output_audio_path: Path, output_subtitles_path: Path = None, voice: str = VOICE_NAME, rate: str = VOICE_RATE):
    """
    Generates voiceover using Edge-TTS.
    Captures SentenceBoundary and WordBoundary timings to create precision subtitles.
    """
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    
    timing_segments = []
    
    with open(output_audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                # offset and duration are in 100-nanoseconds (1e-7 seconds)
                start_sec = chunk["offset"] / 10_000_000
                duration_sec = chunk["duration"] / 10_000_000
                end_sec = start_sec + duration_sec
                sentence_text = chunk.get("text", "").strip()
                
                if not sentence_text:
                    continue
                    
                # If SentenceBoundary, break into sub-chunks of 3-4 words for dynamic Shorts captions
                words = sentence_text.split()
                if len(words) > 4:
                    words_per_group = 3
                    num_groups = (len(words) + words_per_group - 1) // words_per_group
                    group_duration = duration_sec / num_groups
                    
                    for g_idx in range(num_groups):
                        g_words = words[g_idx * words_per_group : (g_idx + 1) * words_per_group]
                        g_start = start_sec + (g_idx * group_duration)
                        g_end = g_start + group_duration
                        timing_segments.append({
                            "start": round(g_start, 3),
                            "end": round(g_end, 3),
                            "text": " ".join(g_words)
                        })
                else:
                    timing_segments.append({
                        "start": round(start_sec, 3),
                        "end": round(end_sec, 3),
                        "text": sentence_text
                    })
                
    if output_subtitles_path and timing_segments:
        with open(output_subtitles_path, "w", encoding="utf-8") as f:
            json.dump(timing_segments, f, ensure_ascii=False, indent=2)
            
    return timing_segments

def generate_voiceover(text: str, output_audio_path: Path, output_subtitles_path: Path = None, voice: str = VOICE_NAME, rate: str = VOICE_RATE):
    """Synchronous wrapper for generate_speech_async."""
    return asyncio.run(generate_speech_async(text, output_audio_path, output_subtitles_path, voice, rate))

if __name__ == "__main__":
    test_text = "क्या आप जानते हैं कि सैमसंग ने भारत में एक नया स्मार्टफोन लॉन्च किया है? इसमें 6000mAh की बड़ी बैटरी दी गई है!"
    out_dir = Path("./test_output")
    out_dir.mkdir(exist_ok=True)
    audio_file = out_dir / "sample_voice.mp3"
    subs_file = out_dir / "sample_subs.json"
    
    print(f"Generating voiceover using {VOICE_NAME}...")
    timings = generate_voiceover(test_text, audio_file, subs_file)
    print(f"Saved audio: {audio_file}")
    print(f"Extracted {len(timings)} subtitle segments:")
    for t in timings:
        print(f"  [{t['start']}s -> {t['end']}s]: {t['text']}")
