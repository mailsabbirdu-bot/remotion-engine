from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

def search_youtube(topic, max_results=5):
    """
    Search YouTube for relevant videos using yt-dlp.
    """
    print(f"\n🎥 [YOUTUBE] Searching for: '{topic}'")
    try:
        ydl_opts = {'quiet': True, 'extract_flat': True, 'no_warnings': True}
        videos = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ytsearch: prefix allows searching YouTube
            search_results = ydl.extract_info(f"ytsearch{max_results}:{topic}", download=False)

            for i, res in enumerate(search_results.get('entries', []), 1):
                title = res.get('title')
                video_id = res.get('id')
                url = res.get('url') or f"https://www.youtube.com/watch?v={video_id}"

                print(f"   🎬 [{i}] Found: {title} ({url})")
                videos.append({
                    "id": video_id,
                    "title": title,
                    "url": url,
                    "channel": res.get("uploader"),
                    "duration": res.get("duration_string"),
                    "viewCount": res.get("view_count")
                })
        return videos
    except Exception as e:
        print(f"❌ Error during YouTube search: {e}")
        return []

def get_transcript(video_id):
    """
    Fetch transcript for a given YouTube video ID.
    Supports both v0.6.x (static get_transcript) and v1.x (instance fetch)
    """
    print(f"      📝 [TRANSCRIPT] Attempting to fetch transcript for {video_id}...")
    try:
        # Try v1.x style (instance fetch)
        try:
            api = YouTubeTranscriptApi()
            transcript_data = api.fetch(video_id)
        except (TypeError, AttributeError):
            # Fallback to v0.6.x style (static get_transcript)
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)

        # Handle both list of dicts (v0.6) and list of dataclasses (v1.x)
        processed_texts = []
        for snippet in transcript_data:
            if isinstance(snippet, dict):
                processed_texts.append(snippet.get('text', ''))
            else:
                # Handle dataclass/object (v1.x)
                processed_texts.append(getattr(snippet, 'text', ''))

        transcript_text = " ".join(processed_texts)
        print(f"         ✅ Success: {len(transcript_text)} characters.")
        return transcript_text
    except Exception as e:
        print(f"         ⚠️ No transcript available: {e}")
        return None

def get_video_metadata(url):
    """
    Extract detailed metadata using yt-dlp.
    """
    ydl_opts = {'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "description": info.get("description"),
                "view_count": info.get("view_count"),
                "upload_date": info.get("upload_date"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail")
            }
    except Exception as e:
        print(f"⚠️ Error extracting metadata for {url}: {e}")
        return {}

def process_youtube_research(topic, max_results=5):
    """
    Combine search, metadata, and transcript extraction.
    """
    videos = search_youtube(topic, max_results=max_results)
    detailed_videos = []

    print(f"\n📊 [YOUTUBE] Processing {len(videos)} videos for transcripts and metadata...")
    for v in videos:
        print(f"   🔎 Analyzing: {v['title'][:50]}...")
        transcript = get_transcript(v['id'])
        metadata = get_video_metadata(v['url'])

        detailed_videos.append({
            "basic": v,
            "metadata": metadata,
            "transcript": transcript
        })

    return detailed_videos

if __name__ == "__main__":
    # Test
    res = process_youtube_research("History of OpenAI", max_results=2)
    for r in res:
        print(f"- {r['basic']['title']} | Transcript length: {len(r['transcript']) if r['transcript'] else 'None'}")
