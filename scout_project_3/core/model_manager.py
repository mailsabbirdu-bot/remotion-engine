import os
import torch
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-root"

# Hardware Acceleration Detection
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
torch.set_grad_enabled(False)

print(f"⚙️ [MODELS] Initializing on Device: {DEVICE.upper()}")

# Load Sentence Transformer for Metadata Filtering
SEMANTIC_MODEL = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device=DEVICE
)

# Load CLIP for visual-text alignment ranking
CLIP_MODEL = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(DEVICE)
CLIP_PROCESSOR = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Load BLIP for deep visual auditing (Captions & Negative Filters)
BLIP_MODEL = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(DEVICE)
BLIP_PROCESSOR = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

# Optimize models for inference
if DEVICE == "cuda":
    CLIP_MODEL = CLIP_MODEL.half()
    BLIP_MODEL = BLIP_MODEL.half()

print("✅ MODELS READY")
