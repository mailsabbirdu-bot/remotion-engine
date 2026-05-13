import google.generativeai as genai
import os
from .config import GEMINI_API_KEY

class ScriptWriter:
    def __init__(self, api_key=None):
        if not api_key:
            api_key = GEMINI_API_KEY

        print(f"🔑 [WRITER] Initializing Gemini API with key: {api_key[:10]}...{api_key[-5:]}")

        try:
            genai.configure(api_key=api_key)
            # Try 1.5-pro, fallback to flash or 1.0 versions
            models_to_try = [
                'gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash',
                'gemini-flash-latest', 'gemini-pro-latest', 'gemini-pro'
            ]
            self.model = None

            for model_name in models_to_try:
                try:
                    m = genai.GenerativeModel(model_name)
                    m.generate_content("test")
                    self.model = m
                    print(f"✅ [WRITER] Gemini {model_name} Model loaded successfully.")
                    break
                except Exception:
                    continue

            if not self.model:
                raise Exception("Could not initialize any Gemini model.")

        except Exception as e:
            print(f"❌ [WRITER] Failed to initialize Gemini Writer: {e}")

    def generate_script(self, topic, research_analysis, language="en"):
        """
        Generate a professional YouTube documentary script based on research analysis.
        """
        lang_instruction = "English" if language == "en" else "Bangla"

        prompt = f"""
        You are a master documentary scriptwriter for a top-tier YouTube channel like MagnatesMedia, ColdFusion, or SunnyV2.
        Your task is to write a highly engaging, cinematic, and professional documentary script about: "{topic}" written entirely in {lang_instruction}.

        Use the following Deep Research Analysis as your source material:
        ---
        {research_analysis}
        ---

        SCRIPT REQUIREMENTS:
        1. **The Hook (0:00 - 1:00)**: Start with a gripping opening that grabs attention. Use mystery, high stakes, or a shocking fact.
        2. **The Introduction**: Define the subject and why it matters in the grand scheme of things.
        3. **Story Progression**: Break the script into logical chapters with smooth transitions.
        4. **Pacing & Tone**: Use a "Cinematic Narration Style". Sentences should vary in length. Use dramatic pauses [Pause].
        5. **Emotional Arc**: Build tension, create empathy, and deliver satisfying revelations.
        6. **Conclusion**: A powerful ending that leaves the viewer thinking. A final "parting thought."

        FORMAT:
        - [Visual: Describe what should be on screen (In {lang_instruction})]
        - [Narrator: The actual spoken words (In {lang_instruction})]
        - [Music: Describe the mood of the music - e.g., Orchestral, Dark Ambient, Upbeat Tech]

        Write the FULL script now in {lang_instruction}. Make it at least 2000 words for a deep dive documentary.
        """

        try:
            print(f"✍️ Generating cinematic script for: {topic}...")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Gemini Error during script writing: {e}")
            return f"Failed to generate script for {topic}."

if __name__ == "__main__":
    # Test
    writer = ScriptWriter()
    # print(writer.generate_script("History of OpenAI", "Analysis goes here..."))
