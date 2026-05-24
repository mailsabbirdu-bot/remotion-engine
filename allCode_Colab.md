# 📜 Project Code Audit

Run this cell to display the file structure and the content of all core engine files.

```python
import os

PROJECT_DIR = "motionCanvas_project"

files_to_show = [
    "package.json",
    "tsconfig.json",
    "vite.config.ts",
    "motion_canvas.json",
    "guideline.md",
    "render-headless.js",
    "src/index.ts",
    "src/types.ts",
    "src/motion-canvas.d.ts",
    "src/scenes/main.tsx",
    "src/components/TextLayer.tsx",
    "src/components/Textbox.tsx",
    "src/components/DataVisuals.tsx",
    "src/components/ShapeLayer.tsx",
    "src/components/Callout.tsx",
    "src/components/Counter.tsx"
]

def show_code():
    print(f"📂 Project Structure: {PROJECT_DIR}")
    print("="*50)
    !find {PROJECT_DIR} -maxdepth 3 -not -path '*/.*' -not -path '*/node_modules*'

    print("\n" + "="*50)
    print("📄 CORE ENGINE CODE")
    print("="*50)

    for rel_path in files_to_show:
        full_path = os.path.join(PROJECT_DIR, rel_path)
        if os.path.exists(full_path):
            print(f"\n--- {rel_path} ---")
            with open(full_path, 'r') as f:
                print(f.read())
            print("-" * 40)
        else:
            print(f"\n⚠️ Missing file: {rel_path}")

show_code()
```
