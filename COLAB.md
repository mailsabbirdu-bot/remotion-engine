# Running on Google Colab

To run this Remotion project on Google Colab, follow these steps:

1. **Mount Google Drive** to access your assets and save the video.
2. **Install Dependencies**: Remotion requires Node.js and some system packages.
3. **Download Fonts**: Ensure the fonts are placed in the `public/fonts` directory of the project.
4. **Render**: Use the Remotion CLI to render the video.

## Colab Code Cell

Copy and paste the following into a Colab code cell:

```python
# 1. Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# 2. Install Node.js (if not already present or needs update)
!curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
!sudo apt-get install -y nodejs

# 3. Navigate to your project directory
# Replace 'path/to/your/remotion-engine' with the actual path in your Drive
%cd /content/drive/MyDrive/remotion-engine

# 4. Install Project Dependencies
!npm install

# 5. Install System Dependencies for Remotion (Chrome, etc.)
!npx remotion browser ensure

# 6. Render the video
# The final video will be saved as 'out/video.mp4' in your project directory
!npx remotion render src/index.ts Main out/video.mp4
```

## Where is the video saved?
The final video will be saved in the `out/` folder relative to the project root:
`/content/drive/MyDrive/remotion-engine/out/video.mp4`

## Optimization Notes
- The engine uses `OffthreadVideo` and is configured for CPU-only rendering.
- If you encounter memory issues, you can add `--concurrency=1` to the render command:
  `!npx remotion render src/index.ts Main out/video.mp4 --concurrency=1`
