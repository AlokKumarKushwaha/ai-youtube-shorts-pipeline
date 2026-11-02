import argparse
import sys
import time
from pathlib import Path

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import OUTPUT_DIR, VOICE_NAME, YOUTUBE_PRIVACY_STATUS
from news_fetcher import fetch_latest_news, mark_as_processed
from script_generator import generate_script_with_gemini
from voice_generator import generate_voiceover
from visual_generator import generate_ai_image
from video_composer import compose_short_video, create_srt_from_timings
from anchor_generator import generate_default_anchor_portrait, generate_talking_anchor_frames

def run_pipeline(
    category_or_topic: str = "tech",
    is_custom_query: bool = False,
    auto_upload: bool = False,
    voice: str = VOICE_NAME,
    anchor_type: str = "male"
):
    timestamp = int(time.time())
    run_dir = OUTPUT_DIR / f"short_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n=======================================================", flush=True)
    print("     AI AUTOMATED YOUTUBE SHORTS PIPELINE", flush=True)
    print("=======================================================\n", flush=True)
    
    # STEP 1: Fetch News
    print(f"[*] Step 1: Fetching latest news for '{category_or_topic}'...", flush=True)
    news_items = fetch_latest_news(category_or_topic, limit=1, skip_processed=not is_custom_query)
    
    if not news_items:
        print("[!] No new stories found. Trying fallback top headlines...", flush=True)
        news_items = fetch_latest_news("top", limit=1, skip_processed=False)
        
    if not news_items:
        print("[X] Failed to fetch news. Please check your internet connection.", flush=True)
        return None
        
    selected_news = news_items[0]
    print(f"[+] Selected Story: {selected_news['title']}", flush=True)
    print(f"[+] Published: {selected_news['published']}", flush=True)
    
    # STEP 2: Generate Script
    print("\n[*] Step 2: Generating engaging Hindi Shorts script with AI...", flush=True)
    script_data = generate_script_with_gemini(selected_news['title'], selected_news['description'])
    
    title = script_data.get("youtube_title", selected_news['title'])
    description = script_data.get("youtube_description", "")
    tags = script_data.get("tags", ["shorts", "news"])
    full_speech = script_data.get("full_speech", "")
    scenes = script_data.get("scenes", [])
    
    print(f"[+] Title: {title}", flush=True)
    print(f"[+] Number of scenes: {len(scenes)}", flush=True)
    print(f"[+] Speech Preview: {full_speech[:120]}...", flush=True)
    
    # STEP 3: Voiceover Generation
    print(f"\n[*] Step 3: Generating natural voiceover ({voice})...", flush=True)
    audio_path = run_dir / "voiceover.mp3"
    subs_timing_path = run_dir / "word_timings.json"
    srt_path = run_dir / "subtitles.srt"
    
    word_timings = generate_voiceover(full_speech, audio_path, subs_timing_path, voice=voice)
    create_srt_from_timings(word_timings, srt_path)
    print(f"[+] Audio generated: {audio_path.name}", flush=True)
    print(f"[+] Dynamic subtitles created: {srt_path.name}", flush=True)
    
    # STEP 4: Visuals Generation
    print("\n[*] Step 4: Generating 9:16 vertical AI visual scenes...", flush=True)
    image_paths = []
    for s in scenes:
        scene_idx = s.get("scene_num", len(image_paths) + 1)
        prompt = s.get("image_prompt", selected_news['title'])
        img_file = run_dir / f"scene_{scene_idx}.jpg"
        
        print(f"    -> Rendering Scene {scene_idx}: '{prompt[:60]}...'", flush=True)
        generate_ai_image(prompt, img_file, topic_context=selected_news['title'])
        image_paths.append(img_file)

        
    portrait_path = generate_default_anchor_portrait(gender=anchor_type) if anchor_type in ("male", "female") else None

    # STEP 6: Video Assembly (TV Newsroom Studio)
    print("\n[*] Step 6: Assembling TV News Studio video with FFmpeg...", flush=True)
    final_video_path = run_dir / f"final_short_{timestamp}.mp4"
    compose_short_video(
        image_paths=image_paths,
        audio_path=audio_path,
        output_video_path=final_video_path,
        srt_subtitles_path=srt_path,
        anchor_image_path=portrait_path,
        headline_text=selected_news['title']
    )
    print(f"\n[SUCCESS] Final YouTube Short Created at:\n=> {final_video_path}", flush=True)

    
    # Mark story as processed
    mark_as_processed(selected_news["id"])
    
    # STEP 7: Optional YouTube Upload
    if auto_upload:
        print("\n[*] Step 7: Initiating YouTube Upload...", flush=True)
        try:
            from youtube_uploader import upload_short_to_youtube
            res = upload_short_to_youtube(
                video_path=final_video_path,
                title=title,
                description=description,
                tags=tags,
                privacy_status=YOUTUBE_PRIVACY_STATUS
            )
            print(f"[🎉] Published to YouTube: {res['url']}", flush=True)
        except Exception as e:
            print(f"[!] YouTube upload failed or client_secret.json missing: {e}", flush=True)
            print("    Run 'python setup_youtube.py' to link your channel.", flush=True)
            
    return final_video_path

def main():
    parser = argparse.ArgumentParser(description="Automated AI YouTube Shorts Pipeline")
    parser.add_argument("--category", type=str, default="tech", choices=["top", "tech", "world", "science", "sports", "entertainment"], help="News category")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic or search query")
    parser.add_argument("--upload", action="store_true", help="Auto upload to YouTube")
    parser.add_argument("--voice", type=str, default=VOICE_NAME, help="Edge-TTS voice name")
    parser.add_argument("--anchor", type=str, default="male", choices=["male", "female", "none"], help="Add AI Talking News Anchor (male/female/none)")
    
    args = parser.parse_args()
    
    target = args.topic if args.topic else args.category
    is_custom = bool(args.topic)
    
    run_pipeline(
        category_or_topic=target,
        is_custom_query=is_custom,
        auto_upload=args.upload,
        voice=args.voice,
        anchor_type=args.anchor
    )

if __name__ == "__main__":
    main()
