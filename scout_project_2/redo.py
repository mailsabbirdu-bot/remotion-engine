import os
import json
import asyncio
import re
from main import (
    PLAN_PATH,
    AUDIO_DIR,
    get_unique_words,
    process_scene,
    BASE
)

def get_story_text_for_scene(scene):
    audio_path = scene.get("audio_path")
    if not audio_path:
        return ""

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    txt_path = os.path.join(AUDIO_DIR, f"{base_name}.txt")

    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            pass
    return ""

async def redo_scene_loop():
    if not os.path.exists(PLAN_PATH):
        print(f"❌ Production plan not found at {PLAN_PATH}!")
        return

    while True:
        with open(PLAN_PATH, "r", encoding="utf-8") as f:
            plan_data = json.load(f)

        scenes = plan_data.get("scenes", [])
        if not scenes:
            print("❌ No scenes found in the production plan.")
            break

        print(f"\n--- RE-SCOUT ENGINE (Total Scenes: {len(scenes)}) ---")
        scene_num_input = input("Enter the scene number you want to re-scout (or 'q' to quit): ").strip()

        if scene_num_input.lower() == 'q':
            break

        try:
            scene_idx = int(scene_num_input) - 1
            if scene_idx < 0 or scene_idx >= len(scenes):
                print(f"❌ Invalid scene number. Please enter 1-{len(scenes)}.")
                continue
        except ValueError:
            print("❌ Please enter a valid number.")
            continue

        target_scene = scenes[scene_idx]
        print(f"🎬 Selected Scene {scene_idx + 1}: {target_scene['scene_id']}")

        print("\nOptions for scouting:")
        print("1. More specific (Dense queries)")
        print("2. More generic (Broad query)")
        print("Leave blank for default extraction")
        choice = input("Your choice (1/2/blank): ").strip()

        story_text = get_story_text_for_scene(target_scene)
        unique_words = get_unique_words(story_text, limit=15)

        if choice == "1":
            print("🔍 Mode: More Specific")
            if len(unique_words) >= 6:
                keywords = [
                    " ".join(unique_words[:4]),
                    " ".join(unique_words[4:8]),
                    " ".join(unique_words[8:12]),
                    " ".join(unique_words[:6])
                ]
            else:
                keywords = [story_text[:60]]
        elif choice == "2":
            print("🔍 Mode: More Generic")
            if len(unique_words) >= 2:
                keywords = [" ".join(unique_words[:2])]
            else:
                keywords = ["cinematic " + (unique_words[0] if unique_words else "scenery")]
        else:
            print("🔍 Mode: Default")
            if len(unique_words) >= 3:
                keywords = [" ".join(unique_words[:3]), " ".join(unique_words[3:6])]
            else:
                keywords = [story_text[:50]] if story_text else ["cinematic atmosphere"]

        target_scene["scout_config"]["keywords"] = keywords
        print(f"🆕 New Keywords: {keywords}")

        # Save updated plan
        with open(PLAN_PATH, "w", encoding="utf-8") as f:
            json.dump(plan_data, f, indent=2, ensure_ascii=False)

        print(f"🚀 Re-processing Scene {scene_idx + 1}...")
        await process_scene(target_scene, scene_idx + 1)

        cont = input("\nDo you want to re-scout another scene? (y/n): ").strip().lower()
        if cont != 'y':
            break

if __name__ == "__main__":
    asyncio.run(redo_scene_loop())
