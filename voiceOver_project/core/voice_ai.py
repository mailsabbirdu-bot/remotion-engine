import os
from google import genai
from google.genai import types
import wave
import time
import re

# Use GEMINI_API_KEY from config if available, otherwise environment
try:
    from scriptWriter_project.core.config import GEMINI_API_KEY
except ImportError:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class VoiceAI:
    def __init__(self, api_key=GEMINI_API_KEY):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY not found. Please set it in config.py or as an environment variable.")

        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-3.1-flash-tts-preview"

    def _save_wave(self, filename, pcm, channels=1, rate=24000, sample_width=2):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)

    def generate_speech(self, text, output_path, voice_name="Kore"):
        """
        Generates speech using the Gemini API (TTS).
        """
        print(f"🎙️ [VOICE_AI] Generating speech for text ({len(text)} chars)...")

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name,
                            )
                        )
                    ),
                )
            )

            if not response.candidates or not response.candidates[0].content.parts:
                print("❌ [VOICE_AI] No audio generated in response.")
                return False

            data = response.candidates[0].content.parts[0].inline_data.data
            self._save_wave(output_path, data)
            print(f"✅ [VOICE_AI] Audio saved to: {output_path}")
            return True

        except Exception as e:
            print(f"❌ [VOICE_AI] Error generating speech: {e}")
            return False

if __name__ == "__main__":
    # Quick Test
    import sys
    test_key = GEMINI_API_KEY
    if len(sys.argv) > 1:
        test_key = sys.argv[1]

    try:
        ai = VoiceAI(api_key=test_key)
        ai.generate_speech("Hello, this is a test of the API-based voice generation.", "test_api.wav")
    except Exception as e:
        print(f"Test failed: {e}")
