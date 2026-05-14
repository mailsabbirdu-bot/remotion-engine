import os

class BrowserScriptWriter:
    def __init__(self, browser_ai):
        self.browser_ai = browser_ai

    def generate_script(self, topic, research_analysis, language="en"):
        """
        Generate a professional YouTube documentary script using browser-based AI.
        """
        lang_instruction = "English" if language == "en" else "Bangla"

        prompt = f"""
        You are a master documentary scriptwriter. Write a highly engaging, cinematic, and professional documentary script about: "{topic}" written entirely in {lang_instruction}.

        Use the following Deep Research Analysis as your source material:
        ---
        {research_analysis}
        ---

        SCRIPT REQUIREMENTS:
        1. **The Hook (0:00 - 1:00)**: Grip the audience immediately.
        2. **The Introduction**: Define the subject and stakes.
        3. **Story Progression**: Break into logical chapters.
        4. **Pacing & Tone**: Cinematic narration, varied sentence length, dramatic pauses [Pause].
        5. **Emotional Arc**: Build tension and empathy.
        6. **Conclusion**: A powerful final thought.

        FORMAT:
        - [Visual: Description (In {lang_instruction})]
        - [Narrator: Spoken words (In {lang_instruction})]
        - [Music: Mood description]

        IMPORTANT: Provide the FULL script now in {lang_instruction}. Make it very detailed and long. Start directly with the script, no conversational intro.
        """

        print(f"✍️ [BROWSER] Generating cinematic script for: {topic}...")
        return self.browser_ai.send_prompt(prompt, wait_time=10)
