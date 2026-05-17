import aiohttp
import asyncio

from core.config import API_KEYS

SEM = asyncio.Semaphore(4)

def deduplicate(candidates):
    seen = set()
    final = []
    for c in candidates:
        key = c.get("url")
        if key in seen:
            continue
        seen.add(key)
        final.append(c)
    return final


async def fetch_pexels_video(session, query, limit=12):
    print(f"📡 [SCOUT] Searching Pexels Videos for: '{query}'")
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={limit}"
    headers = {
        "Authorization": API_KEYS["pexels"]
    }
    try:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"⚠️ [SCOUT] Pexels Video API error: {response.status}")
                return []
            data = await response.json()
            final = []
            for v in data.get("videos", []):
                try:
                    best = max(
                        v["video_files"],
                        key=lambda x: x.get("width", 0)
                    )
                    final.append({
                        "type": "video",
                        "source": "pexels",
                        "id": f"pexels_video_{v['id']}",
                        "url": best["link"],
                        "width": best.get("width", 0),
                        "height": best.get("height", 0),
                        "duration": v.get("duration", 0),
                        "title": query,
                        "description": query
                    })
                except:
                    pass
            return final
    except Exception as e:
        print(f"❌ [SCOUT] Pexels Video Fetch failed: {e}")
        return []


async def fetch_pexels_image(session, query, limit=12):
    print(f"📡 [SCOUT] Searching Pexels Images for: '{query}'")
    url = f"https://api.pexels.com/v1/search?query={query}&per_page={limit}"
    headers = {
        "Authorization": API_KEYS["pexels"]
    }
    try:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"⚠️ [SCOUT] Pexels Image API error: {response.status}")
                return []
            data = await response.json()
            final = []
            for p in data.get("photos", []):
                try:
                    final.append({
                        "type": "image",
                        "source": "pexels",
                        "id": f"pexels_image_{p['id']}",
                        "url": p["src"]["large2x"],
                        "width": p["width"],
                        "height": p["height"],
                        "duration": 5,
                        "title": query,
                        "description": query
                    })
                except:
                    pass
            return final
    except Exception as e:
        print(f"❌ [SCOUT] Pexels Image Fetch failed: {e}")
        return []


async def fetch_pixabay_video(session, query, limit=12):
    print(f"📡 [SCOUT] Searching Pixabay Videos for: '{query}'")
    key = API_KEYS["pixabay"]
    url = f"https://pixabay.com/api/videos/?key={key}&q={query}&per_page={limit}"
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"⚠️ [SCOUT] Pixabay Video API error: {response.status}")
                return []
            data = await response.json()
            final = []
            for v in data.get("hits", []):
                try:
                    vid = v["videos"]["large"]
                    final.append({
                        "type": "video",
                        "source": "pixabay",
                        "id": f"pixabay_video_{v['id']}",
                        "url": vid["url"],
                        "width": vid.get("width", 0),
                        "height": vid.get("height", 0),
                        "duration": v.get("duration", 0),
                        "title": query,
                        "description": query
                    })
                except:
                    pass
            return final
    except Exception as e:
        print(f"❌ [SCOUT] Pixabay Video Fetch failed: {e}")
        return []


async def fetch_pixabay_image(session, query, limit=12):
    print(f"📡 [SCOUT] Searching Pixabay Images for: '{query}'")
    key = API_KEYS["pixabay"]
    url = f"https://pixabay.com/api/?key={key}&q={query}&per_page={limit}&image_type=photo"
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"⚠️ [SCOUT] Pixabay Image API error: {response.status}")
                return []
            data = await response.json()
            final = []
            for p in data.get("hits", []):
                try:
                    final.append({
                        "type": "image",
                        "source": "pixabay",
                        "id": f"pixabay_image_{p['id']}",
                        "url": p["largeImageURL"],
                        "width": p["imageWidth"],
                        "height": p["imageHeight"],
                        "duration": 5,
                        "title": query,
                        "description": query
                    })
                except:
                    pass
            return final
    except Exception as e:
        print(f"❌ [SCOUT] Pixabay Image Fetch failed: {e}")
        return []


async def get_all_candidates(scene):
    prefs = scene.get("asset_preferences", {})
    preferred_type = prefs.get("preferred_type", "video")

    # Strict Preference Logic: If video is preferred, we ONLY look for videos.
    allow_video = True if preferred_type == "video" else prefs.get("allow_video", True)
    allow_image = False if preferred_type == "video" else prefs.get("allow_image", True)

    scout = scene.get("scout_config", {})
    keywords = scout.get("keywords", [])
    if not keywords:
        keywords = [scene["text"]]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for query in keywords:
            if allow_video:
                tasks.append(fetch_pexels_video(session, query))
                tasks.append(fetch_pixabay_video(session, query))
            if allow_image:
                tasks.append(fetch_pexels_image(session, query))
                tasks.append(fetch_pixabay_image(session, query))

        results = await asyncio.gather(*tasks)

    final = []
    for r in results:
        final.extend(r)

    final = deduplicate(final)
    print(f"✅ [SCOUT] Candidates Pool: {len(final)} ({'Videos Only' if preferred_type=='video' else 'Mixed'})")
    return final[:40]
