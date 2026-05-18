import os
import json
import asyncio
import main  # Import main to access paths and engine functions

async def re_scout_loop():
    # Set the render directory specifically for re-scouting as per requirements
    main.RENDER_DIR = os.path.join(main.BASE, "audio", "re_scout")
    os.makedirs(main.RENDER_DIR, exist_ok=True)

    print(f"📂 RE-SCOUT RENDER DIR: {main.RENDER_DIR}")

    if not os.path.exists(main.PLAN_PATH):
        print(f"❌ Production plan not found at {main.PLAN_PATH}!")
        return

    while True:
        # Reload plan data every time in case of updates
        with open(main.PLAN_PATH, "r", encoding="utf-8") as f:
            plan_data = json.load(f)

        scenes = plan_data.get("scenes", [])
        if not scenes:
            print("❌ No scenes found in the production plan.")
            break

        print(f"\n--- 🔄 RE-SCOUT ENGINE (Total Scenes: {len(scenes)}) ---")
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

        # 1. Keywords Editing
        current_keywords = target_scene.get("scout_config", {}).get("keywords", [])
        print(f"\n🔑 Current Keywords: {current_keywords}")
        new_keywords_input = input("Enter new keywords (comma-separated) or press Enter to keep current: ").strip()
        if new_keywords_input:
            target_scene["scout_config"]["keywords"] = [k.strip() for k in new_keywords_input.split(",") if k.strip()]

        # 2. Must Have Editing
        current_must_have = target_scene.get("scout_config", {}).get("must_have_required", [])
        print(f"📌 Current Must Have: {current_must_have}")
        new_must_have_input = input("Enter new 'must have' items (comma-separated) or press Enter to keep current: ").strip()
        if new_must_have_input:
            target_scene["scout_config"]["must_have_required"] = [m.strip() for m in new_must_have_input.split(",") if m.strip()]

        # 3. Negative Prompts Editing
        current_neg = target_scene.get("negative_prompts", [])
        print(f"🚫 Current Negative Prompts: {current_neg}")
        new_neg_input = input("Enter new negative prompts (comma-separated) or press Enter to keep current: ").strip()
        if new_neg_input:
            target_scene["negative_prompts"] = [n.strip() for n in new_neg_input.split(",") if n.strip()]

        # Save updated plan back to BASE (so engine picks it up)
        with open(main.PLAN_PATH, "w", encoding="utf-8") as f:
            json.dump(plan_data, f, indent=2, ensure_ascii=False)

        print(f"\n🚀 Re-scouting Scene {scene_idx + 1} with updated parameters...")
        # process_scene handles downloading, auditing, and rendering (with audio and padding)
        await main.process_scene(target_scene, scene_idx + 1)

        cont = input("\nDo you want to re-scout another scene? (y/n): ").strip().lower()
        if cont != 'y':
            break

if __name__ == "__main__":
    asyncio.run(re_scout_loop())
