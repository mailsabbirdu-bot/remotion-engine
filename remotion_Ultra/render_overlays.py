import os
import json
import subprocess
import shutil
import re

# --- CONFIGURATION ---
BASE_DRIVE_PATH = "/content/drive/MyDrive/Counterism_Studio_V4"
MASTER_JSON_PATH = os.path.join(BASE_DRIVE_PATH, "master_remotion.json")
ASSET_SOURCE_DRIVE = os.path.join(BASE_DRIVE_PATH, "renders")
OUTPUT_DRIVE_DIR = os.path.join(BASE_DRIVE_PATH, "renders/overlays/remotion")

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(PROJECT_DIR, "public")
LOCAL_MASTER_JSON = os.path.join(PROJECT_DIR, "src/master_remotion.json")

def get_video_frame_count(file_path):
    """Returns accurate frame count using ffprobe."""
    try:
        cmd_dur = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        duration = float(subprocess.check_output(cmd_dur).decode('utf-8').strip())

        cmd_fps = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        fps_raw = subprocess.check_output(cmd_fps).decode('utf-8').strip()
        if '/' in fps_raw:
            num, den = fps_raw.split('/')
            fps = float(num) / float(den)
        else:
            fps = float(fps_raw)

        return int(round(duration * fps))
    except Exception as e:
        print(f"⚠️ Error getting frame count for {file_path}: {e}")
        return None

def run_render():
    # 1. Load Master JSON
    if not os.path.exists(MASTER_JSON_PATH):
        print(f"❌ Master JSON not found at {MASTER_JSON_PATH}")
        return

    with open(MASTER_JSON_PATH, 'r') as f:
        data = json.load(f)

    scenes = data.get('scenes', data.get('Scenes', []))
    fps = data.get('fps', 30)

    # 2. Update durations and prepare assets
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)

    for scene in scenes:
        src = scene.get('src', '')
        if not src: continue

        # Handle naming convention (scene_1.mp4 -> scene_SC_01.mp4 if necessary)
        # But mostly we just need to find the file in ASSET_SOURCE_DRIVE
        asset_path = os.path.join(ASSET_SOURCE_DRIVE, src)

        # Fallback search if exact name not found (e.g. scene_SC_01.mp4 vs scene_1.mp4)
        if not os.path.exists(asset_path):
            match = re.search(r'scene_(\d+)', src)
            if match:
                num = match.group(1).zfill(2)
                alt_src = f"scene_SC_{num}.mp4"
                alt_path = os.path.join(ASSET_SOURCE_DRIVE, alt_src)
                if os.path.exists(alt_path):
                    asset_path = alt_path
                    scene['src'] = alt_src
                    if 'background' in scene:
                        scene['background']['src'] = alt_src

        if os.path.exists(asset_path):
            # Mirror to public for Remotion to see
            shutil.copy2(asset_path, os.path.join(PUBLIC_DIR, os.path.basename(asset_path)))

            # Update duration
            frames = get_video_frame_count(asset_path)
            if frames:
                scene['duration'] = frames
                # Sync text layers
                layers = scene.get('layers', scene.get('Layers', []))
                for layer in layers:
                    if layer.get('type') == 'text':
                        layer['duration'] = frames
        else:
            print(f"⚠️ Warning: Asset {src} not found in {ASSET_SOURCE_DRIVE}")

    # Save updated JSON locally for the render process
    with open(LOCAL_MASTER_JSON, 'w') as f:
        json.dump(data, f, indent=2)

    # 3. Render each scene
    for i, scene in enumerate(scenes):
        scene_id = scene.get('Id', scene.get('id', f'scene_{i+1}'))
        output_file = os.path.join(PROJECT_DIR, f"out/{scene_id}.webm")
        os.makedirs(os.path.join(PROJECT_DIR, "out"), exist_ok=True)

        print(f"🎬 Rendering Scene: {scene_id} ({scene.get('duration')} frames)...")

        # Remotion command for transparent WebM (VP9)
        # --codec=vp9 and --pixel-format=yuva420p are key for alpha channel
        cmd = [
            "npx", "remotion", "render",
            "src/index.ts",
            scene_id,
            output_file,
            "--codec=vp9",
            "--pixel-format=yuva420p",
            "--concurrency=1",
            "--bundle-cache=false"
        ]

        try:
            subprocess.run(cmd, check=True)

            # 4. Copy to Drive
            drive_output = os.path.join(OUTPUT_DRIVE_DIR, f"{scene_id}.webm")
            shutil.copy2(output_file, drive_output)
            print(f"✅ Saved to Drive: {drive_output}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to render scene {scene_id}: {e}")

if __name__ == "__main__":
    run_render()
