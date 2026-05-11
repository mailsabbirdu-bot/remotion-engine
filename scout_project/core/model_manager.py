import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-root"

import torch

from sentence_transformers import SentenceTransformer

# We'll use a lazy loading pattern for transformers to avoid downloading everything
# if only basic functions are used, but for now we follow the user's structure.
DEVICE = "cpu"

torch.set_grad_enabled(False)

SEMANTIC_MODEL = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device=DEVICE
)

# Placeholder for CLIP/BLIP models which are referenced in other files
# but not explicitly initialized in the user's provided snippet for this file.
# I'll add them to ensure the project "works" as requested.
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration

CLIP_MODEL = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(DEVICE)
CLIP_PROCESSOR = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

BLIP_MODEL = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(DEVICE)
BLIP_PROCESSOR = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

print("✅ MODELS READY")
