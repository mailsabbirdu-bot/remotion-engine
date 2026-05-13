import google.generativeai as genai
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import GEMINI_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP

class GeminiSummarizer:
    def __init__(self, api_key=None):
        if not api_key:
            api_key = GEMINI_API_KEY

        print(f"🔑 [SUMMARIZER] Initializing Gemini API with key: {api_key[:10]}...{api_key[-5:]}")

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ [SUMMARIZER] Gemini Flash Model loaded successfully.")
        except Exception as e:
            print(f"❌ [SUMMARIZER] Failed to initialize Gemini: {e}")

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

    def summarize_text(self, text, source_type="article"):
        """
        Summarize a long text using Gemini with chunking if necessary.
        """
        if not text:
            return "No content to summarize."

        chunks = self.text_splitter.split_text(text)
        summaries = []

        for i, chunk in enumerate(chunks):
            prompt = f"""
            Analyze and summarize the following {source_type} content.
            Extract:
            1. Key insights and facts
            2. Important events and dates
            3. Controversies or hidden patterns
            4. Emotional highlights or dramatic turning points

            Content:
            {chunk}
            """
            try:
                response = self.model.generate_content(prompt)
                summaries.append(response.text)
            except Exception as e:
                print(f"❌ Gemini Error during summarization: {e}")
                summaries.append(f"Summary failed for chunk {i}")

        if len(summaries) > 1:
            # Combine summaries if multi-chunk
            final_prompt = f"Combine these summaries into one comprehensive deep analysis:\n\n" + "\n\n".join(summaries)
            try:
                final_response = self.model.generate_content(final_prompt)
                return final_response.text
            except:
                return "\n\n".join(summaries)

        return summaries[0] if summaries else "Summary failed."

    def deep_combined_analysis(self, summaries_list, language="en"):
        """
        Perform a deep cross-source analysis on a list of summaries.
        """
        lang_instruction = "English" if language == "en" else "Bangla"

        combined_text = "\n\n--- SOURCE ---\n\n".join(summaries_list)
        prompt = f"""
        You are a world-class documentary researcher. Below are several summaries of articles and video transcripts regarding a specific topic.
        Your task is to synthesize all this information into a Deep Analysis Report written entirely in {lang_instruction}.

        Requirements:
        1. Identify the core narrative and main "story arc" of this topic.
        2. Detect any contradictions or differing perspectives between sources.
        3. Highlight the most cinematic and emotional elements that would work well in a YouTube documentary.
        4. Organize key events chronologically if applicable.
        5. Extract compelling hooks or "mind-blowing" facts.

        Source Material:
        {combined_text}

        Deep Analysis Report (In {lang_instruction}):
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Gemini Error during deep analysis: {e}")
            return "Deep analysis failed."

if __name__ == "__main__":
    # Test (requires API key)
    summarizer = GeminiSummarizer()
    # print(summarizer.summarize_text("Test content here..."))
