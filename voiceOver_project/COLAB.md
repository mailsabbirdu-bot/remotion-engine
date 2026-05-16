# VoiceOver Project - Colab Setup

Run the following cell to setup and run the voice generation engine.

```python
# @title 🎙️ RUN VOICEOVER ENGINE
import os

# 1. Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# 2. Setup Project
%cd /content
!git clone https://github.com/your-repo/path.git # Note: Replace with actual repo if needed, or skip if already present
%cd /content/voiceOver_project

# 3. Install Dependencies
!pip install -r requirements.txt
!playwright install chromium
!python3 -m playwright install-deps

# 4. Run Engine
# First time? Run with headless=False to login
# !python3 main.py --headless=False

# Regular run
!python3 main.py
```

## ⚠️ IMPORTANT: First Run & Login
Since Google AI Studio requires a login, you must perform the first run in **non-headless mode** (if possible on local) or use a `gemini_session` folder that already has the login cookie.

In Colab, you might need to use a tool like `localtunnel` or `ngrok` to see the browser if you need to login manually, or upload your local `gemini_session` folder to Drive and link it.

### How to use your local login in Colab:
1. Run the project locally with `headless=False`.
2. Login to your Google account.
3. Zip the `gemini_session` folder.
4. Upload `gemini_session.zip` to your Google Drive.
5. In Colab, unzip it to the project folder before running `main.py`.
