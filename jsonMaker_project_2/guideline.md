# JSON Maker Project 2 - Guidelines

This project automates the filling of `master_remotion.json` and `production_plan.json` based on cinematic storytelling metadata.

## Mapping Rules

### 1. Master Remotion (`master_remotion.json`)
*   **Scenes**:
    *   `id`: Sequentially numbered as `scene_1`, `scene_2`, etc.
    *   `duration`: Calculated in frames (30 FPS) based on audio duration + 1.0s buffer.
    *   **Background**:
        *   `src`: Set as `scene_1.mp4`, `scene_2.mp4` to match processed B-roll.
    *   **Transition**:
        *   `type`: Extracted from `jsonPrep.txt` (e.g., `fade`).
        *   `duration`: Standardized to 15 frames unless specified.
    *   **Layers**:
        *   Contains full overlay configuration (Text, Animation, Textbox).
        *   `content`: Derived from the `Text` field in `jsonPrep.txt`.
        *   `textbox`: `enabled` is set to `false` if `jsonPrep.txt` specifies `none`.

### 2. Production Plan (`production_plan.json`)
*   **Scene ID**: `scene_1`, `scene_2`, etc.
*   **Text**: Cinematic prompt for the Scout search engine.
*   **Negative Prompts**: Standard set includes `low quality`, `blurry`, `text`, `watermark`, `people`.
*   **Asset Preferences**: Defaults to `video` as the preferred type.
*   **Audio Path**: Fixed pattern `/content/drive/MyDrive/Counterism_Studio_V4/audio/SC_XX.wav`.
*   **Scout Config**:
    *   `keywords`: High-quality search terms for Pexels/Pixabay.
    *   `must_have_required`: Core subjects that must appear in the footage.
*   **Empty Fields**:
    *   `duration` and `audio_duration` are explicitly left empty (`""`).
*   **Fixed Fields**:
    *   `audio_start_in_scene`: Always set to `0.5`.

## Input Files (`Counterism_Studio_V4/audio/`)
*   `jsonPrep.txt`: Main metadata file with visual directions.
*   `story.txt`: Narrative text for context.
