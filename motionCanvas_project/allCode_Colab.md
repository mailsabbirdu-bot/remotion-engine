# 📜 Motion Canvas Code Audit Tool

Run this cell in Google Colab to display the full project structure and core engine code for review.

```python
import os

# Assuming we are in the motionCanvas_project directory
PROJECT_ROOT = "."

core_files = [
    "package.json",
    "tsconfig.json",
    "vite.config.ts",
    "motion_canvas.json",
    "guideline.md",
    "render-headless.js",
    "src/index.ts",
    "src/types.ts",
    "src/scenes/main.tsx",
    "src/components/TextLayer.tsx",
    "src/components/Textbox.tsx",
    "src/components/DataVisuals.tsx",
    "src/components/ShapeLayer.tsx",
    "src/components/Callout.tsx",
    "src/components/Counter.tsx"
]

def audit_project():
    print("📂 PROJECT DIRECTORY STRUCTURE")
    print("="*60)
    # Filter out node_modules and hidden files for clarity
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules' and d != 'out']
        level = root.replace(PROJECT_ROOT, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if not f.startswith('.'):
                print(f"{subindent}{f}")

    print("\n" + "="*60)
    print("📄 CORE ENGINE SOURCE CODE")
    print("="*60)

    for rel_path in core_files:
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.exists(full_path):
            print(f"\n[ FILE: {rel_path} ]")
            print("-" * 40)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    print(f.read())
            except Exception as e:
                print(f"Error reading file: {e}")
            print("-" * 60)
        else:
            print(f"\n⚠️ File not found: {rel_path}")

audit_project()
```
