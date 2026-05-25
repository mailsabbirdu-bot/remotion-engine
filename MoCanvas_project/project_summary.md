# MoCanvas Project Summary

## What it does
MoCanvas is a JSON-driven overlay engine built with **Motion Canvas**. It takes a structured JSON manifest (`master_motion.json`) and renders each scene into a separate, transparent `.webm` video. These videos are designed to be used as high-quality overlays for video production.

## How it works
1. **JSON Driven**: The entire animation sequence, including timing, content, and styling, is defined in a single JSON file.
2. **Motion Canvas Power**: Uses the Motion Canvas framework for programmatic, ultra-smooth, "edged" animations.
3. **Headless Capture**: A custom Playwright-based script (`render-headless.js`) runs a headless browser, captures each frame of the animation as a PNG, and then uses **FFmpeg** to encode them into transparent WebM files.
4. **Colab Ready**: Designed to run entirely in Google Colab with a single cell, syncing assets from Google Drive and exporting the final renders back to Drive.
5. **Modern Aesthetics**: Built-in components for sleek textboxes, data visualizations, and animated text with various entrance effects.

## Output Path
Renders are saved to: `Counterism_Studio_V4/renders/overlays/motion_canvas` on Google Drive.
