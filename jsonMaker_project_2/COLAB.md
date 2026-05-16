# JSON Maker V2 - Colab Execution

Run the following cell to install dependencies and execute the JSON generation engine.

```python
# 1. Install Dependencies
!pip install playwright playwright-stealth
!playwright install chromium
!python3 -m playwright install-deps

# 2. Run the Engine
%cd /content/your-repo-name/jsonMaker_project_2
!python3 main.py
```

*Note: Ensure your Google Drive is mounted at `/content/drive`.*
