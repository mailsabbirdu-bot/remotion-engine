# Google Colab Setup for ScriptWriter AI

Run this cell in Google Colab to set up and run the ScriptWriter AI.

```python
# 1. Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# 2. Clone the Repository (or navigate to it)
import os
REPO_URL = "https://github.com/your-repo/scriptWriter_project.git" # Update with actual repo URL
REPO_NAME = "your-repo-name"

if not os.path.exists(REPO_NAME):
    !git clone {REPO_URL}
%cd {REPO_NAME}/scriptWriter_project

# 3. Install Dependencies
!pip install -r requirements.txt

# 4. Set Gemini API Key
import os
from google.colab import userdata
try:
    os.environ["GOOGLE_API_KEY"] = userdata.get('GOOGLE_API_KEY')
except:
    print("⚠️ Please set GOOGLE_API_KEY in Colab Secrets (Left sidebar -> 🔑)")

# 5. Run the Program
!python main.py
```

## How to use:
1. Open Google Colab.
2. Go to **Secrets** (key icon on the left).
3. Add a new secret with the name `GOOGLE_API_KEY` and your Gemini API Key as the value.
4. Paste the code above into a cell and run it.
5. Enter your topic when prompted and hit Enter.
6. The final script will be saved to your Google Drive at `Counterism_Studio_V4/audio/script.txt`.
