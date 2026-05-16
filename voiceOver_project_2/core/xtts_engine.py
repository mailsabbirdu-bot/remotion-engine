import os
import torch
import re
from TTS.api import TTS

# Accept Terms of Service programmatically
os.environ["COQUI_TOS_AGREED"] = "1"

class XTTSEngine:
    def __init__(self, use_gpu=None):
        """
        Initializes the XTTS v2 engine.
        :param use_gpu: Boolean, if True forces CUDA. If None, auto-detects.
        """
        print("🔧 [XTTS_ENGINE] Initializing XTTS v2 model...")

        if use_gpu is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = "cuda" if use_gpu else "cpu"

        print(f"🖥️ [XTTS_ENGINE] Using device: {self.device}")

        try:
            # Load the model
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            print("✅ [XTTS_ENGINE] Model loaded successfully.")
        except Exception as e:
            print(f"❌ [XTTS_ENGINE] Error loading model: {e}")
            raise

    def is_bangla(self, text):
        """
        Detects if text contains Bangla characters.
        """
        return bool(re.search(r"[\u0980-\u09ff]", text))

    def generate_speech(self, text, output_path, speaker_wav, language=None):
        """
        Generates speech using XTTS v2.
        :param text: Text to synthesize
        :param output_path: Where to save the .wav file
        :param speaker_wav: Reference audio for voice cloning
        :param language: Language code (e.g., 'en', 'hi'). If None, auto-detects Bangla vs English.
        """
        if not language:
            if self.is_bangla(text):
                # XTTS v2 doesn't officially support 'bn' yet in most stable releases.
                # Hindi ('hi') provides a more natural Indic accent for Bangla text than English.
                language = "hi"
                print(f"🌏 [XTTS_ENGINE] Bangla detected, using 'hi' (Hindi) for Indic accent.")
            else:
                language = "en"
                print(f"🌏 [XTTS_ENGINE] Using 'en' (English).")

        print(f"🎙️ [XTTS_ENGINE] Synthesizing speech (lang={language})...")

        try:
            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=speaker_wav,
                language=language
            )
            return True
        except Exception as e:
            print(f"❌ [XTTS_ENGINE] Synthesis failed: {e}")
            return False
