from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

def search_youtube(topic, max_results=5):
    """
    Search YouTube for relevant videos.
    """
    print(f"\n🎥 [YOUTUBE] Searching for: '{topic}'")
    try:
        videos_search = VideosSearch(topic, limit=max_results)
        results = videos_search.result()

        videos = []
        for i, res in enumerate(results.get('result', []), 1):
            print(f"   🎬 [{i}] Found: {res.get('title')} ({res.get('link')})")
            videos.append({
                "id": res.get("id"),
                "title": res.get("title"),
                "url": res.get("link"),
                "channel": res.get("channel", {}).get("name"),
                "duration": res.get("duration"),
                "viewCount": res.get("viewCount", {}).get("short")
            })
        return videos
    except Exception as e:
        print(f"❌ Error during YouTube search: {e}")
        return []

def get_transcript(video_id):
    """
    Fetch transcript for a given YouTube video ID.
    """
    print(f"      📝 [TRANSCRIPT] Attempting to fetch transcript for {video_id}...")
    try:
        # YouTubeTranscriptApi.get_transcript is a static method, not an instance method.
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([t['text'] for t in transcript_data])
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
