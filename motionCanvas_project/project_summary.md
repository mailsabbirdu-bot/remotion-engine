# 🎬 Motion Canvas JSON-Driven Production Engine

## 📌 Project Overview
This project is a high-end, programmatic video production engine built on **Motion Canvas**, **React**, and **TypeScript**. It is designed to create professional, documentary-style motion graphics (e.g., National Geographic or Vox style) driven entirely by a JSON configuration file.

The engine specifically targets **sequential storytelling**, where scenes are rendered one after another with clean transitions, making it ideal for cinematic documentaries.

---

## 🚀 Core Features

### 1. Sequential Scene Rendering
Unlike standard animation timelines, this engine renders scenes strictly in sequence.
- **No Overlaps**: Each scene completes its transition-out before the next begins.
- **Transitions**: Built-in support for configurable fade transitions at the start and end of every scene.
- **Timing Control**: Scene durations are defined in seconds, allowing precise alignment with narration.

### 2. Premium Component Library
A suite of modular components designed for high-end aesthetics:
- **`Textbox`**: Modern lower-thirds with a dual-line layout (Title | Subtitle), sleek accent lines, and transparent backgrounds.
- **`Callout`**: Animated pointer lines and labels used to highlight specific areas of interest in the background footage.
- **`DataVisuals`**:
    - **Line/Area Graphs**: Animated line drawing with sleek area fills, background grids, and pulsing trackers.
    - **Bar Charts**: Staggered, animated bars with value labels.
- **`Counter`**: High-impact numerical counters for statistics and data-heavy segments.
- **`TextLayer`**: Kinetic typography supporting multi-line text, custom fonts (Bangla/English), and various entry animations (Fade, Slide, Zoom, Typewriter).
- **`ShapeLayer`**: Minimalist geometric accents.

### 3. Headless Rendering Pipeline
A robust pipeline designed for server-side or cloud-based (Google Colab) production:
- **`render-headless.js`**: A Playwright-based bridge that automates a Vite server, navigates to the project, captures frames in high resolution, and signals completion.
- **Frame-to-Video Encoding**: Uses FFmpeg to convert captured PNG sequences into high-quality H.264 MP4 videos (`crf 18`).

---

## 🛠️ Technical Stack
- **Framework**: [Motion Canvas](https://motioncanvas.io/) (2D & Core)
- **Language**: TypeScript / TSX
- **Build Tool**: Vite
- **Automation**: Playwright (Headless Browser)
- **Video Processing**: FFmpeg
- **Runtime**: Node.js (ESM)

---

## 📂 Project Structure
```text
motionCanvas_project/
├── src/
│   ├── components/         # Modular animation components
│   ├── scenes/             # Main rendering logic (main.tsx)
│   ├── types.ts            # JSON Schema and TypeScript interfaces
│   ├── index.ts            # Browser entry point
│   └── motion-canvas.d.ts  # Type declarations for assets
├── public/                 # Static assets (linked from Drive in Colab)
├── motion_canvas.json      # The master manifest (Production Plan)
├── guideline.md            # Detailed instructions for editors
├── COLAB.md                # One-cell render automation script
├── allCode_Colab.md        # Code audit and inspection tool
├── project_summary.md      # This file
├── render-headless.js      # Headless rendering bridge
├── vite.config.ts          # Vite configuration with MC plugin
├── tsconfig.json           # TypeScript configuration for MC JSX
└── package.json            # Dependencies and scripts
```

---

## 📖 How to Use

### 1. Define the Story
Edit `motion_canvas.json` to define your scenes, background assets, and overlay layers. Use the `guideline.md` for specific property values.

### 2. Prepare Assets
Upload your background videos to `Google Drive > Counterism_Studio_V4 > renders`. The engine automatically links these during the Colab run.

### 3. Render on Google Colab
- Open the project on Google Colab.
- Copy the contents of `COLAB.md` into a cell.
- Replace `REPO_URL` with your actual repository link.
- Run the cell. The engine will:
    1. Setup the environment (Node, Playwright, FFmpeg).
    2. Sync your JSON and Assets from Drive.
    3. Render the animation frame-by-frame.
    4. Encode the final video and save it back to `Google Drive > Counterism_Studio_V4 > out`.

---

## 💎 Design Philosophy
- **Ultra-Edged**: Sharp lines, clean typography, and modern color palettes.
- **Sleek & Modern**: Heavy use of easing (`easeOutExpo`, `easeOutCubic`), subtle shadows, and transparency.
- **Error-Free**: Comprehensive TypeScript definitions and fallback mechanisms (e.g., dark backgrounds if video is missing) to ensure a successful render every time.
