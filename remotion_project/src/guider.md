# Master JSON Guider

This file describes the fields in `master_remotion.json`.

## Root Fields
- `width`: (Number) Video width in pixels.
- `height`: (Number) Video height in pixels.
- `fps`: (Number) Frames per second.
- `banglaFont`: (String) Name of the Bangla font (e.g., "Sohid Osman Hadi").
- `englishFont`: (String) Name of the English font (e.g., "Audiowide").
- `scenes`: (Array) List of scene objects.

## Scene Object
- `id`: (String) Unique identifier for the scene.
- `duration`: (Number) Duration of the scene in frames.
- `background`: (Object)
  - `type`: "video", "image", or "color".
  - `src`: URL, path to the asset, or hex color code.
    - **Colab Tip**: If using files from Google Drive, use the path starting with `/content/drive/MyDrive/...`
  - `audio`: (Optional) URL or path to the background audio.
- `transition`: (Optional Object)
  - `type`: Transition type (e.g., "fade").
  - `duration`: Duration of the transition in frames.
- `layers`: (Array) List of layer objects.

## Layer Object
- `id`: (String) Unique identifier for the layer.
- `type`: "text", "image", or "video".
- `content`: Text content or URL/path to asset.
- `start`: (Number) Start frame relative to the scene start.
- `duration`: (Number) Duration in frames.
- `style`: (Object) CSS-like properties.
  - `fontSize`: (Number)
  - `color`: (String) Hex or RGB.
  - `x`: (Number) Center X position in pixels (e.g., 540 for center of 1080).
  - `y`: (Number) Center Y position in pixels.
- `animationIn`: (Optional Object)
  - `type`: "fade-up", "fade-in".
  - `duration`: (Number) frames.
  - `easing`: (Optional String) e.g., "cubic-bezier(0.33, 1, 0.68, 1)" or "ease-out".
- `animationOut`: (Optional Object)
  - `type`: "fade-down", "fade-out".
  - `duration`: (Number) frames.
  - `easing`: (Optional String).
- `keyframes`: (Optional Array)
  - `frame`: (Number) Frame relative to layer start.
  - `scale`: (Number)
  - `opacity`: (Number)
  - `easing`: (Optional String).
- `textbox`: (Optional Object)
  - `enabled`: (Boolean)
  - `type`: "rounded-rect", "rect", "none".
  - `padding`: (Number)
  - `fill`: (String) Background color of the box (e.g., "rgba(0,0,0,0.5)").

## Presets
### Animations
- `fade-up`: Fades in and slides up.
- `fade-in`: Simple fade in.
- `fade-down`: Fades out and slides down.
- `fade-out`: Simple fade out.

### Easings
- `cubic-bezier(x1, y1, x2, y2)`: Custom Bezier curves supported.
- `ease-in`, `ease-out`, `ease-in-out`, `linear`.

### Transitions
- `fade`: Crossfade between scenes.

### Textbox Shapes
- `rounded-rect`: Rectangular box with rounded corners.
- `rect`: Sharp cornered box.
- `none`: No background box.
