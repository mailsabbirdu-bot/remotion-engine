# JSON MAKER PROJECT - COLAB SETUP

Run this cell to install dependencies and execute the engine:

```python
# 1. Install System Dependencies
!pip install playwright playwright-stealth
!playwright install chromium
!python3 -m playwright install-deps

# 2. Run the Engine
%cd /content/your-repo-name/jsonMaker_project
!python3 main.py
```
