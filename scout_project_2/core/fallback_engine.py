import asyncio

from core.scout import get_all_candidates
from core.technical_filter import technical_filter

async def get_fallback_candidates(scene):

    fallback = scene.get("fallback_broll", {})

    if not fallback:
        return []

    print("\n⚠️ ACTIVATING FALLBACK B-ROLL ENGINE")

    fake_scene = {
        "text": fallback["keywords"][0],
        "scout_config": {
            "keywords": fallback["keywords"],
            "must_have_required":
                fallback.get("must_have_required", []),

            "must_have_optional":
                fallback.get("must_have_optional", [])
        },
        "negative_prompts":
            fallback.get("negative_prompts", [])
    }

    candidates = await get_all_candidates(
        fake_scene,
        scene["duration"],
        30
    )

    candidates = technical_filter(
        candidates,
        scene["duration"]
    )

    print(
        f"🎬 FALLBACK SURVIVORS: "
        f"{len(candidates)}"
    )

    return candidates[:10]
