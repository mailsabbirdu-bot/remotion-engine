import google.generativeai as genai
import os
from .config import GEMINI_API_KEY

class ScriptWriter:
    def __init__(self, api_key=None):
        self.api_key = api_key or GEMINI_API_KEY
        self.available_models = []
        self.current_model_index = 0
        self.model = None

        print(f"🔑 [WRITER] Initializing Gemini API with key: {self.api_key[:10]}...{self.api_key[-5:]}")

        try:
            genai.configure(api_key=self.api_key)
            # Efficiently find an available model
            remote_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

            # Prioritized preference list for high quality script writing
            preferred_models = [
                'gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash',
                'gemini-flash-latest', 'gemini-pro-latest', 'gemini-pro'
            ]

            for m in preferred_models:
                if m in remote_models:
                    self.available_models.append(m)

            for m in remote_models:
                if m not in self.available_models:
                    self.available_models.append(m)

            if self.available_models:
                model_name = self.available_models[0]
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ [WRITER] Gemini {model_name} Model selected.")
            else:
                print("⚠️ [WRITER] No Gemini models available.")

        except Exception as e:
            print(f"❌ [WRITER] Failed to initialize Gemini Writer: {e}")

    def _cycle_model(self):
        """
        Switch to the next available Gemini model if the current one is rate-limited.
        """
        if len(self.available_models) > 1:
            self.current_model_index = (self.current_model_index + 1) % len(self.available_models)
            model_name = self.available_models[self.current_model_index]
            print(f"🔄 [QUOTA-WRITER] Cycling to next model: {model_name}")
            self.model = genai.GenerativeModel(model_name)
            return True
        return False

    def _call_gemini_with_retry(self, prompt, retries=5, initial_delay=2):
        """
        Call Gemini API with exponential backoff and model cycling.
        """
        import time
        delay = initial_delay
        for attempt in range(retries):
            if not self.model: break

            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    if attempt % 2 == 0 and self._cycle_model():
                        time.sleep(1)
                        continue

                    if attempt < retries - 1:
                        print(f"⚠️ Quota exceeded. Retrying in {delay} seconds... (Attempt {attempt+1}/{retries})")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise e
                else:
                    raise e
        return None

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
            res = self._call_gemini_with_retry(prompt)
            return res if res else f"Failed to generate script for {topic}."
        except Exception as e:
            print(f"❌ Gemini Error during script writing: {e}")
            return f"Failed to generate script for {topic}."

if __name__ == "__main__":
    # Test
    writer = ScriptWriter()
    # print(writer.generate_script("History of OpenAI", "Analysis goes here..."))
