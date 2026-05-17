import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-root"

os.makedirs("/tmp/runtime-root", exist_ok=True)
