import os
import json
import asyncio
import re
import main  # Import the whole module to modify its globals

def get_story_text_for_scene(scene):
    audio_path = scene.get("audio_path")
    if not audio_path:
        return ""

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    txt_path = os.path.join(main.AUDIO_DIR, f"{base_name}.txt")

    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except:
            pass

    # Fallback to scene text if story text file is missing or empty
    return scene.get("text", "")

async def redo_scene_loop():
    # Set the render directory to the new location for re-scouting
    main.RENDER_DIR = os.path.join(main.BASE, "audio", "re_scout")
    os.makedirs(main.RENDER_DIR, exist_ok=True)

    print(f"📂 RE-SCOUT RENDER DIR: {main.RENDER_DIR}")

    if not os.path.exists(main.PLAN_PATH):
        print(f"❌ Production plan not found at {main.PLAN_PATH}!")
        return

    # Load Template Plan (from Repo) for better keywords
    template_scenes = []
    if os.path.exists(main.TEMPLATE_PLAN_PATH):
        try:
            with open(main.TEMPLATE_PLAN_PATH, "r", encoding="utf-8") as f:
                template_data = json.load(f)
                template_scenes = template_data.get("scenes", [])
        except:
            pass

    while True:
        with open(main.PLAN_PATH, "r", encoding="utf-8") as f:
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

        # Get template reference if available
        template_ref = template_scenes[scene_idx] if scene_idx < len(template_scenes) else {}

        print("\nOptions for scouting:")
        print("1. More specific (Dense, targeted queries)")
        print("2. More generic (Broad, atmospheric queries)")
        print("Leave blank for default extraction")
        choice = input("Your choice (1/2/blank): ").strip()

        story_text = get_story_text_for_scene(target_scene)
        unique_words = main.get_unique_words(story_text, limit=15)

        # Base keywords from template
        template_keywords = template_ref.get("scout_config", {}).get("keywords", [])
        template_text = template_ref.get("text", "")
        required = template_ref.get("scout_config", {}).get("must_have_required", [])

        if choice == "1":
            print("🔍 Mode: More Specific")
            keywords = []

            # Use hand-crafted template text + requirements
            if template_text:
                keywords.append(template_text)
                if required:
                    keywords.append(f"{template_text} {required[0]}")

            # Denser word combinations from story
            if len(unique_words) >= 8:
                keywords.append(" ".join(unique_words[:5]))
                keywords.append(" ".join(unique_words[5:10]))
                keywords.append(" ".join(unique_words[:8]))

            # Add specificity modifiers
            if required:
                for req in required[:2]:
                    keywords.append(f"highly detailed {req} close up 4k")

            # Include all template keywords if they exist
            keywords.extend(template_keywords)

        elif choice == "2":
            print("🔍 Mode: More Generic")
            keywords = []
            if len(unique_words) >= 2:
                keywords.append(" ".join(unique_words[:2]))

            if required:
                keywords.append(f"cinematic {required[0]} atmosphere")
            else:
                keywords.append("cinematic background scenery")

            # Use broad terms from template
            if template_text:
                words = template_text.split()
                if len(words) >= 2:
                    keywords.append(" ".join(words[:2]))
        else:
            print("🔍 Mode: Default")
            if template_keywords:
                keywords = template_keywords
            elif len(unique_words) >= 3:
                keywords = [" ".join(unique_words[:3]), " ".join(unique_words[3:6])]
            else:
                keywords = [story_text[:50]] if story_text else ["cinematic atmosphere"]

        # Deduplicate and clean
        keywords = list(dict.fromkeys([k.strip() for k in keywords if k and k.strip()]))

        if not keywords:
            keywords = [target_scene.get("text", "cinematic atmosphere")]

        target_scene["scout_config"]["keywords"] = keywords
        print(f"🆕 New Keywords: {keywords}")

        # Save updated plan
        with open(main.PLAN_PATH, "w", encoding="utf-8") as f:
            json.dump(plan_data, f, indent=2, ensure_ascii=False)

        print(f"🚀 Re-processing Scene {scene_idx + 1}...")
        # process_scene uses main.RENDER_DIR for output path
        await main.process_scene(target_scene, scene_idx + 1)

        cont = input("\nDo you want to re-scout another scene? (y/n): ").strip().lower()
        if cont != 'y':
            break

if __name__ == "__main__":
    asyncio.run(redo_scene_loop())
