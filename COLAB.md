# Running on Google Colab

To run this Remotion project on Google Colab, follow these steps. **Note: It is highly recommended to run the project from `/content` (Colab local disk) rather than directly from Google Drive to avoid permission and speed issues.**

## Colab Code Cell

Copy and paste the following into a Colab code cell:

```python
# 1. Mount Google Drive
from google.colab import drive
import os
import shutil

drive.mount('/content/drive')

# 2. Setup Project in /content (Faster & avoids Drive sync issues)
PROJECT_PATH_DRIVE = "/content/drive/MyDrive/remotion-engine" # Change this to your project path
PROJECT_PATH_LOCAL = "/content/remotion-engine"

if os.path.exists(PROJECT_PATH_LOCAL):
    shutil.rmtree(PROJECT_PATH_LOCAL)

# Copy from Drive to Local (excluding node_modules if it exists)
!mkdir -p {PROJECT_PATH_LOCAL}
!cp -r {PROJECT_PATH_DRIVE}/* {PROJECT_PATH_LOCAL}
# If node_modules exists in Drive, it might be better to re-install locally
if os.path.exists(f"{PROJECT_PATH_LOCAL}/node_modules"):
    shutil.rmtree(f"{PROJECT_PATH_LOCAL}/node_modules")

%cd {PROJECT_PATH_LOCAL}

# 3. Install Node.js
!curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
!sudo apt-get install -y nodejs

# 4. Install Project Dependencies
!npm install

# 5. Install System Dependencies for Remotion (Chrome, etc.)
!npx remotion browser ensure

# 6. Render the video
# The final video will be saved in the /content/remotion-engine/out folder
!npx remotion render src/index.ts Main out/video.mp4

# 7. Copy the result back to Google Drive
OUTPUT_DRIVE = os.path.join(PROJECT_PATH_DRIVE, "out")
os.makedirs(OUTPUT_DRIVE, exist_ok=True)
shutil.copy("/content/remotion-engine/out/video.mp4", os.path.join(OUTPUT_DRIVE, "video.mp4"))

print(f"✅ Video successfully rendered and saved to: {OUTPUT_DRIVE}/video.mp4")
```

## Where is the video saved?
The video is first rendered to `/content/remotion-engine/out/video.mp4` and then automatically copied back to your Google Drive folder under `out/video.mp4`.

## Troubleshooting
- **ENOENT (File not found)**: Make sure `PROJECT_PATH_DRIVE` in the code cell matches the actual folder name in your Google Drive.
- **Permission denied**: Ensure you granted Colab access to your Google Drive when prompted.
- **Out of memory**: If the render fails, try adding `--concurrency=1` to the render command.
