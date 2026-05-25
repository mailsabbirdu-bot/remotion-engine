# MoCanvas JSON Guideline

🌟 **Engine Principles**
- **Sequential Flow:** Scenes play one after another. No overlaps.
- **Timing:** Use `duration` (seconds) to control how long a scene stays visible.
- **Coordinates:** (0,0) is the exact center of the screen. 1920x1080 resolution is standard.

🎬 **Scene Object**
- `id`: Unique name (string).
- `duration`: Visible length in seconds (number).
- `background`: (Optional)
  - `type`: "video", "image", "color".
  - `src`: Path or color code.

💎 **Storyteller Layers**

### 1. Text Layer (type: "text")
- `content`: Supports multi-line Bengali/English text.
- `style`: `fontSize`, `fontWeight`, `color`, `shadowBlur`, `x`, `y`.
- `animationIn`: "fade", "slide-up", "zoom", "typewriter".

### 2. Textbox Layer (type: "textbox")
- Sleek accent-lined boxes for locations or facts.
- `content`: Use `|` to separate title and subtitle (e.g., "Title | Subtitle").
- `style`: `width`, `height`, `fill` (bg color), `stroke` (accent line color), `fontSize`.
- `animationIn`: "slide-right", "fade", etc.

### 3. Data Visuals (type: "graph" or "chart")
- `data`: Array of numbers (for bar charts) or `[x,y]` pairs (for graphs).
- `style`: `fill` or `stroke`, `x`, `y`.

### 4. Callout Layer (type: "image" with id: "callout_...")
- Points to a specific spot in the background.
- `content`: The label text.
- `style`: `x`, `y` (the destination of the line), `color`.

---

**Note on Fonts:** Default fonts support Bangla and English. Custom fonts can be linked via style properties.
