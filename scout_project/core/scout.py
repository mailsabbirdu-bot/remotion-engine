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


async def fetch_pexels_video(session, query, limit=8):

    url = f"https://api.pexels.com/videos/search?query={query}&per_page={limit}"

    headers = {
        "Authorization": API_KEYS["pexels"]
    }

    try:

        async with session.get(url, headers=headers) as response:

            if response.status != 200:
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

    except:
        return []


async def fetch_pexels_image(session, query, limit=8):

    url = f"https://api.pexels.com/v1/search?query={query}&per_page={limit}"

    headers = {
        "Authorization": API_KEYS["pexels"]
    }

    try:

        async with session.get(url, headers=headers) as response:

            if response.status != 200:
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

    except:
        return []


async def fetch_pixabay_video(session, query, limit=8):

    key = API_KEYS["pixabay"]

    url = f"https://pixabay.com/api/videos/?key={key}&q={query}&per_page={limit}"

    try:

        async with session.get(url) as response:

            if response.status != 200:
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

    except:
        return []


async def get_all_candidates(scene):

    prefs = scene.get("asset_preferences", {})

    allow_video = prefs.get("allow_video", True)

    allow_image = prefs.get("allow_image", True)

    scout = scene.get("scout_config", {})

    keywords = scout.get("keywords", [])

    query = keywords[0] if keywords else scene["text"]

    async with aiohttp.ClientSession() as session:

        tasks = []

        if allow_video:

            tasks.append(
                fetch_pexels_video(session, query)
            )

            tasks.append(
                fetch_pixabay_video(session, query)
            )

        if allow_image:

            tasks.append(
                fetch_pexels_image(session, query)
            )

        results = await asyncio.gather(*tasks)

    final = []

    for r in results:
        final.extend(r)

    final = deduplicate(final)

    print(f"✅ MIXED ASSETS: {len(final)}")

    return final[:20]
