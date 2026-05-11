import os
import torch
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-root"
os.makedirs("/tmp/runtime-root", exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
torch.set_grad_enabled(False)

print(f"🧠 LOADING MODELS ON {DEVICE.upper()}...")

# Semantic matching
SEMANTIC_MODEL = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device=DEVICE
)

# Vision matching (CLIP)
CLIP_MODEL = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(DEVICE)
CLIP_PROCESSOR = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Captioning (BLIP)
BLIP_MODEL = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(DEVICE)
BLIP_PROCESSOR = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

print("✅ MODELS READY")
