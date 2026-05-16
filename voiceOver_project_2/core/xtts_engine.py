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
            print(f"✅ [XTTS_ENGINE] Model loaded successfully. Supported languages: {self.tts.languages}")
        except Exception as e:
            print(f"❌ [XTTS_ENGINE] Error loading model: {e}")
            raise

    def bangla_to_devanagari(self, text):
        """
        Transliterates Bangla script to Devanagari (Hindi) script.
        This allows the Hindi model to read Bangla text with a much more natural Indic accent.
        Bangla Unicode: U+0980 to U+09FF
        Devanagari Unicode: U+0900 to U+097F
        Offset: 0x80 (0980 - 0900)
        """
        transliterated = ""
        for char in text:
            code = ord(char)
            # If char is in Bangla range
            if 0x0980 <= code <= 0x09FF:
                # Map to Devanagari range
                # Note: Not all characters map 1:1, but for TTS prosody, this is very effective
                transliterated += chr(code - 0x80)
            else:
                transliterated += char
        return transliterated

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
        :param language: Language code. If None, auto-detects.
        """
        # Detection and Transliteration
        if self.is_bangla(text):
            if language is None:
                language = "hi"

            # Transliterate for Hindi model if using 'hi'
            if language == "hi":
                original_text = text
                text = self.bangla_to_devanagari(text)
                print(f"🌏 [XTTS_ENGINE] Bangla text transliterated to Devanagari for natural Indic accent.")
        else:
            if language is None:
                language = "en"

        print(f"🎙️ [XTTS_ENGINE] Synthesizing speech (lang={language})...")

        try:
            # Ensure speaker_wav exists
            if not os.path.exists(speaker_wav):
                print(f"⚠️ [XTTS_ENGINE] Reference audio {speaker_wav} not found! Synthesis might fail.")

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
