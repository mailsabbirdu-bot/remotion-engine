# 🛠️ Master JSON Guideline (V4)

This guide helps AI and Human editors fill the `master_remotion.json` to leverage the full "After Effects" engine.

## 🌟 Root Level Properties
- `width`: Video width (e.g., 1080).
- `height`: Video height (e.g., 1920).
- `fps`: Frames per second (Standard 30).
- `banglaFont`: Filename of the .ttf file for Bangla text (without extension).
- `englishFont`: Filename of the .ttf file for English text (without extension).
- `scenes`: Array of scene objects.

## 🎬 Scene Object
- `id`: Unique identifier.
- `duration`: Length of scene in frames.
- `background`:
    - `type`: "video", "image", "color", "gradient".
    - `src`: Path or value.
    - `audio`: Path to audio file.
    - `zoom`: Zoom factor for Ken Burns (e.g., 1.2).
- `transition`:
    - `type`: "fade", "slide", "wipe".
    - `duration`: frames.
- `layers`: Array of layer objects.

## 💎 Layer Objects

### 1. Text Layer (`type: "text"`)
- `content`: The text to display.
- `style`:
    - `x`, `y`: Position (e.g., "50%").
    - `fontSize`: pixels.
    - `color`: hex/rgba.
    - `fontWeight`, `textShadow`.
- `animationIn`:
    - `type`: "fade-up", "zoom-in", "blur-in".
    - `duration`: frames.
- `animationOut`:
    - `type`: "fade-down", "zoom-out".
- `textbox`:
    - `enabled`: boolean.
    - `type`: "rounded-rect", "rect".
    - `color`: rgba.
- `textAnimation`:
    - `mode`: "word", "character", "sentence", "none".
    - `duration`: how long the kinetic typography takes.

### 2. Image/Video Layer (`type: "image"` or `"video"`)
- `content`: Path to asset.
- `style`: `width`, `height`, `rotate`, `borderRadius`, `zoom`.

### 3. Shape Layer (`type: "shape"`)
- `shape`:
    - `type`: "rect", "circle", "triangle".
    - `width`, `height`, `color`, `stroke`, `strokeWidth`, `borderRadius`.

## 🚀 Pro Tips for AI
1. **Timing**: Ensure `start + duration` of a layer does not exceed scene `duration`.
2. **Transitions**: Transitions overlap scenes. The engine handles the math, just specify the `duration`.
3. **Hierarchy**: Use `zIndex` in `style` to control layer stacks.
