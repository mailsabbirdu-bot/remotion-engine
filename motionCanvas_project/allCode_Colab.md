# 📜 Motion Canvas Code Audit Tool

Run this cell in Google Colab to display the full project structure and core engine code.

```python
import os

# Search for the project directory in common locations
possible_paths = [
    ".",
    "motionCanvas_project",
    "/content/motion-canvas-production/motionCanvas_project",
    "/content/motionCanvas_project"
]

PROJECT_ROOT = None
for p in possible_paths:
    if os.path.exists(os.path.join(p, "package.json")) and os.path.exists(os.path.join(p, "src")):
        PROJECT_ROOT = p
        break

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
    if not PROJECT_ROOT:
        print("❌ Error: Could not find the Motion Canvas project directory.")
        print("Please ensure you have cloned the repository or are in the correct directory.")
        # List current directory to help debug
        print(f"\nCurrent Directory: {os.getcwd()}")
        print("Contents:", os.listdir("."))
        return

    print(f"📂 PROJECT DIRECTORY FOUND: {os.path.abspath(PROJECT_ROOT)}")
    print("="*60)

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Exclude bulky or hidden folders
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'out', 'dist', 'public']]
        level = root.replace(PROJECT_ROOT, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root) or '.'}/")
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
                    content = f.read()
                    print(content if content.strip() else "[Empty File]")
            except Exception as e:
                print(f"Error reading file: {e}")
            print("-" * 60)
        else:
            print(f"\n⚠️ File not found: {rel_path}")

audit_project()
```
