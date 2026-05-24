# 📜 Motion Canvas Code Audit Tool

Run this cell in Google Colab to display the full project structure and core engine code.
**Note:** Ensure you have run the setup cell (from COLAB.md) or cloned the repository first.

```python
import os

# Search for the project directory in common locations
possible_roots = [
    "/content",
    "/content/motion-canvas-production",
    "/content/motion-canvas-repo",
    "."
]

PROJECT_ROOT = None
for root in possible_roots:
    target = os.path.join(root, "motionCanvas_project")
    if os.path.exists(os.path.join(target, "package.json")):
        PROJECT_ROOT = target
        break
    # Check if we are already inside it
    if os.path.exists(os.path.join(root, "package.json")) and "motionCanvas_project" in os.path.abspath(root):
        PROJECT_ROOT = root
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
        print("Please ensure you have run the main Setup/Render cell in COLAB.md first.")
        print(f"\nCurrent Directory: {os.getcwd()}")
        print("Contents of /content:", os.listdir("/content") if os.path.exists("/content") else "N/A")
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
