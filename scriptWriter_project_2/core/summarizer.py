import os
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import CHUNK_SIZE, CHUNK_OVERLAP

class BrowserSummarizer:
    def __init__(self, browser_ai):
        self.browser_ai = browser_ai
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

    def summarize_text(self, text, source_type="article", language="en"):
        """
        Summarize long text by sending it in chunks to the browser-based AI.
        """
        if not text:
            return "No content to summarize."

        lang_instruction = "English" if language == "en" else "Bengali (Bangla / বাংলা)"

        chunks = self.text_splitter.split_text(text)
        summaries = []

        for i, chunk in enumerate(chunks):
            print(f"   ✍️ [BROWSER] Processing chunk {i+1}/{len(chunks)}...")
            prompt = f"""
            Task: Summarize the following {source_type} content concisely.
            Target Language: {lang_instruction}

            CRITICAL INSTRUCTIONS:
            1. Your entire response MUST be written in {lang_instruction}.
            2. DO NOT use English. Translate everything to {lang_instruction}.
            3. Provide ONLY the raw summary text.
            4. Do not include introductory phrases like "Here is a summary".

            Content:
            {chunk}
            """
            summary = self.browser_ai.send_prompt(prompt)
            if summary:
                summaries.append(summary)
            else:
                summaries.append(f"(Summary failed for chunk {i})")

            # Brief pause between chunks
            time.sleep(2)

        if len(summaries) > 1:
            print("   ✍️ [BROWSER] Combining multiple summaries...")
            final_prompt = f"Combine these summaries into one comprehensive analysis in {lang_instruction}. MANDATORY: YOUR ENTIRE RESPONSE MUST BE IN {lang_instruction}. DO NOT USE ENGLISH. Provide only the combined summary text:\n\n" + "\n\n".join(summaries)
            return self.browser_ai.send_prompt(final_prompt)

        return summaries[0] if summaries else "Summary failed."

    def deep_combined_analysis(self, summaries_list, language="en"):
        """
        Perform deep cross-source analysis using browser-based AI.
        """
        lang_instruction = "English" if language == "en" else "Bengali (Bangla / বাংলা)"
        combined_text = "\n\n--- SOURCE ---\n\n".join(summaries_list)

        # Split combined text if it's too long for a single prompt
        text_chunks = self.text_splitter.split_text(combined_text)

        if len(text_chunks) > 1:
            print(f"   🧠 [BROWSER] Analysis material too large, processing in {len(text_chunks)} chunks...")
            partial_analyses = []
            for i, chunk in enumerate(text_chunks):
                prompt = f"Analyze this part of the research material ({i+1}/{len(text_chunks)}) in {lang_instruction}. YOUR ENTIRE RESPONSE MUST BE IN {lang_instruction}. NO ENGLISH:\n\n{chunk}"
                partial_analyses.append(self.browser_ai.send_prompt(prompt))

            combined_text = "\n\n".join([p for p in partial_analyses if p])

        prompt = f"""
        You are a world-class documentary researcher. Synthesize all the provided research information into a Deep Analysis Report.

        CRITICAL REQUIREMENT: The entire report MUST be written entirely in {lang_instruction}.
        NO ENGLISH ALLOWED. Translate all findings into {lang_instruction}.

        Requirements:
        1. Identify the core narrative and main "story arc".
        2. Detect contradictions or differing perspectives.
        3. Highlight cinematic and emotional elements.
        4. Organize key events chronologically.
        5. Extract compelling hooks.

        IMPORTANT: Start directly with the report in {lang_instruction}. Do not include any conversational intro or English text.

        Source Material:
        {combined_text}

        Deep Analysis Report (In {lang_instruction}):
        """
        return self.browser_ai.send_prompt(prompt, wait_time=10)
