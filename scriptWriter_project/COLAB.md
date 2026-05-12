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

# 4. Run the Program
!python main.py
```

## How to use:
1. Open Google Colab.
2. Paste the code above into a cell and run it.
3. Enter your topic when prompted and hit Enter.
4. The final script will be saved to your Google Drive at `Counterism_Studio_V4/audio/script.txt`.
