import os
import json
import subprocess
import shutil
import re

# --- CONFIGURATION ---
BASE_DRIVE_PATH = "/content/drive/MyDrive/Counterism_Studio_V4"
# The engine will always render according to the remotion_ultra_gdrive.json from the google drive
MASTER_JSON_PATH = os.path.join(BASE_DRIVE_PATH, "remotion_ultra_gdrive.json")
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

def check_transparency(file_path):
    """Verifies if the video has an alpha channel using ffprobe."""
    try:
        # Check pixel format
        cmd_pix = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=pix_fmt', '-of', 'csv=p=0', file_path
        ]
        pix_fmt = subprocess.check_output(cmd_pix).decode('utf-8').strip()

        # Check for alpha_mode tag (common in VP9 WebM)
        cmd_tag = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream_tags=alpha_mode', '-of', 'csv=p=0', file_path
        ]
        alpha_mode = subprocess.check_output(cmd_tag).decode('utf-8').strip()

        # WebM with VP9 often reports yuv420p but has a separate alpha plane signaled by alpha_mode: 1
        has_alpha = 'yuva' in pix_fmt or 'alpha' in pix_fmt or alpha_mode == '1'

        return has_alpha, f"{pix_fmt} (alpha_mode={alpha_mode})"
    except Exception as e:
        print(f"⚠️ Error checking transparency for {file_path}: {e}")
        return False, "unknown"

def run_ffprobe_detailed(file_path):
    """Prints detailed stream info for diagnostic purposes."""
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', file_path]
        output = subprocess.check_output(cmd).decode('utf-8')
        print(f"🔍 DEBUG: ffprobe details for {os.path.basename(file_path)}:")
        print(output)
    except:
        pass

def run_render():
    # 1. Load Master JSON
    if not os.path.exists(MASTER_JSON_PATH):
        print(f"❌ Master JSON not found at {MASTER_JSON_PATH}")
        print(f"📝 ACTION REQUIRED: Please copy 'remotion_ultra.json' from this project to your Google Drive as 'remotion_ultra_gdrive.json'")

        # Fallback to local if drive one missing (for first setup)
        fallback = os.path.join(PROJECT_DIR, "remotion_ultra.json")
        if os.path.exists(fallback):
            print(f"ℹ️ Attempting local fallback for initial run: {fallback}")
            with open(fallback, 'r') as f:
                data = json.load(f)
        else:
            print("❌ No local manifest found. Rendering aborted.")
            return
    else:
        print(f"✅ Using Google Drive manifest: {MASTER_JSON_PATH}")
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

        asset_path = os.path.join(ASSET_SOURCE_DRIVE, src)

        # Fallback search
        if not os.path.exists(asset_path):
            match = re.search(r'scene_(\d+)', src)
            if match:
                num = match.group(1).zfill(2)
                alt_src = f"scene_SC_{num}.mp4"
                alt_path = os.path.join(ASSET_SOURCE_DRIVE, alt_src)
                if os.path.exists(alt_path):
                    asset_path = alt_path
                    scene['src'] = alt_src

        if os.path.exists(asset_path):
            shutil.copy2(asset_path, os.path.join(PUBLIC_DIR, os.path.basename(asset_path)))

            frames = get_video_frame_count(asset_path)
            if frames:
                scene['duration'] = frames
                # Ensure background object exists for the engine but is empty or points to src
                if 'background' not in scene:
                    scene['background'] = {'type': 'video', 'src': scene['src']}

                # Sync text layers
                layers = scene.get('layers', scene.get('Layers', []))
                for layer in layers:
                    if layer.get('type') == 'text':
                        layer['duration'] = frames
        else:
            print(f"⚠️ Warning: Asset {src} not found in {ASSET_SOURCE_DRIVE}")
            if 'duration' not in scene:
                scene['duration'] = 150 # Default fallback

    # Save updated JSON locally for the render process
    with open(LOCAL_MASTER_JSON, 'w') as f:
        json.dump(data, f, indent=2)

    # 3. Render each scene
    for i, scene in enumerate(scenes):
        raw_id = scene.get('Id', scene.get('id', f'scene-{i+1}'))
        scene_id = raw_id.replace('_', '-')
        output_file = os.path.join(PROJECT_DIR, f"out/{scene_id}.webm")
        os.makedirs(os.path.join(PROJECT_DIR, "out"), exist_ok=True)

        print(f"🎬 Rendering Scene: {scene_id} ({scene.get('duration')} frames)...")

        cmd = [
            "npx", "remotion", "render",
            "src/index.ts",
            scene_id,
            output_file,
            "--codec=vp9",
            "--pixel-format=yuva420p",
            "--image-format=png",
            "--concurrency=1",
            "--bundle-cache=false"
        ]

        try:
            subprocess.run(cmd, check=True)

            # 4. Verify Transparency
            has_alpha, pix_fmt = check_transparency(output_file)
            if has_alpha:
                print(f"✨ TRANSPARENCY VERIFIED: {scene_id} has alpha channel ({pix_fmt})")
            else:
                print(f"❌ TRANSPARENCY FAILED: {scene_id} is OPAQUE ({pix_fmt})")
                run_ffprobe_detailed(output_file)

            # 5. Copy to Drive
            drive_output = os.path.join(OUTPUT_DRIVE_DIR, f"{scene_id}.webm")
            shutil.copy2(output_file, drive_output)
            print(f"✅ Saved to Drive: {drive_output}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to render scene {scene_id}: {e}")

if __name__ == "__main__":
    run_render()
    print("\n" + "="*80)
    print("🏁 RENDER SEQUENCE COMPLETE")
    print("="*80)
    print("💡 NOTE ON TRANSPARENCY:")
    print("   WebM (VP9) files use a special 'alpha_mode' to signal transparency.")
    print("   If your video player shows a black background, try importing the file into")
    print("   Adobe Premiere, DaVinci Resolve, or After Effects to verify the alpha channel.")
    print("="*80 + "\n")
