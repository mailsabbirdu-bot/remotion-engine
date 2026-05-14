import google.generativeai as genai
import os
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import GEMINI_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP

class GeminiSummarizer:
    def __init__(self, api_key=None):
        self.local_model = None
        self.local_tokenizer = None
        self.api_key = api_key or GEMINI_API_KEY

        # Track available models for cycling
        self.available_models = []
        self.current_model_index = 0
        self.model = None

        print(f"🔑 [SUMMARIZER] Initializing Gemini API with key: {self.api_key[:10]}...{self.api_key[-5:]}")

        try:
            genai.configure(api_key=self.api_key)
            # Efficiently find an available model
            remote_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    name = m.name.replace('models/', '')
                    # Filter out non-text/experimental models that often fail text tasks
                    if 'tts' not in name.lower() and 'embedding' not in name.lower():
                        remote_models.append(name)

            # Prioritized preference list
            preferred_models = [
                'gemini-2.0-flash', 'gemini-1.5-flash',
                'gemini-flash-latest', 'gemini-pro-latest', 'gemini-1.5-pro'
            ]

            for m in preferred_models:
                if m in remote_models:
                    self.available_models.append(m)

            # Add any other remaining models as last resort
            for m in remote_models:
                if m not in self.available_models:
                    self.available_models.append(m)

            if self.available_models:
                model_name = self.available_models[0]
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ [SUMMARIZER] Gemini {model_name} Model selected.")
            else:
                print("⚠️ [SUMMARIZER] Gemini unavailable. Local fallback will be used if needed.")

        except Exception as e:
            print(f"❌ [SUMMARIZER] Failed to initialize Gemini: {e}")

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

    def _setup_local_llm(self):
        """
        Initialize an ultra-lightweight local LLM optimized for CPU fallback.
        """
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM

            # SmolLM2-360M is tiny (360M params) and extremely fast on CPU
            model_id = "HuggingFaceTB/SmolLM2-360M-Instruct"
            print(f"📥 [LOCAL LLM] Loading {model_id} for ultra-fast CPU fallback...")

            self.local_tokenizer = AutoTokenizer.from_pretrained(model_id)
            device = "cuda" if torch.cuda.is_available() else "cpu"

            # CPU-optimized loading
            load_kwargs = {"device_map": "auto", "torch_dtype": "auto"}
            if device == "cpu":
                load_kwargs["low_cpu_mem_usage"] = True

            self.local_model = AutoModelForCausalLM.from_pretrained(
                model_id,
                **load_kwargs
            )
            print(f"✅ [LOCAL LLM] Loaded successfully on {device}.")
        except Exception as e:
            print(f"❌ [LOCAL LLM] Failed to load: {e}")

    def _summarize_locally(self, text, source_type):
        """
        Summarize using the local LLM.
        """
        if not self.local_model:
            return "Local summarization failed (model not loaded)."

        messages = [
            {"role": "system", "content": f"You are a helpful assistant that summarizes {source_type} content concisely."},
            {"role": "user", "content": f"Extract key facts and insights from this {source_type}:\n\n{text}"}
        ]

        input_text = self.local_tokenizer.apply_chat_template(messages, tokenize=False)
        inputs = self.local_tokenizer(input_text, return_tensors="pt").to(self.local_model.device)

        outputs = self.local_model.generate(**inputs, max_new_tokens=500, temperature=0.2)
        response = self.local_tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Strip the prompt
        return response.split("assistant\n")[-1].strip()

    def _cycle_model(self):
        """
        Switch to the next available Gemini model if the current one is rate-limited.
        """
        if len(self.available_models) > 1:
            self.current_model_index = (self.current_model_index + 1) % len(self.available_models)
            model_name = self.available_models[self.current_model_index]
            print(f"🔄 [QUOTA] Cycling to next model: {model_name}")
            self.model = genai.GenerativeModel(model_name)
            return True
        return False

    def _call_gemini_with_retry(self, prompt, retries=5, initial_delay=2):
        """
        Call Gemini API with exponential backoff and model cycling to handle 429 errors.
        """
        delay = initial_delay
        for attempt in range(retries):
            if not self.model: break

            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    # If we have other models, try cycling first before long wait
                    if attempt % 2 == 0 and self._cycle_model():
                        time.sleep(1) # Short breath
                        continue

                    if attempt < retries - 1:
                        print(f"⚠️ Quota exceeded. Retrying in {delay} seconds... (Attempt {attempt+1}/{retries})")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        # Exhausted retries for this prompt
                        print("🚫 Gemini exhausted for this request.")
                        raise e
                else:
                    raise e

        # If we reach here, either model is None or retries failed
        return None

    def summarize_text(self, text, source_type="article"):
        """
        Summarize a long text using Gemini with chunking if necessary.
        """
        if not text:
            return "No content to summarize."

        chunks = self.text_splitter.split_text(text)
        summaries = []

        for i, chunk in enumerate(chunks):
            # No fixed delay needed anymore as exponential backoff handles it

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
            summary = None
            try:
                if self.model:
                    summary = self._call_gemini_with_retry(prompt)

                if not summary:
                    if not self.local_model: self._setup_local_llm()
                    summary = self._summarize_locally(chunk, source_type)

                if summary:
                    summaries.append(summary)
            except Exception as e:
                print(f"❌ Summarization Error: {e}")
                # Lazy initialization of local LLM
                if not self.local_model:
                    print("🔄 Attempting local LLM fallback...")
                    self._setup_local_llm()

                if self.local_model:
                    print("🔄 Retrying with local LLM...")
                    try:
                        summary = self._summarize_locally(chunk, source_type)
                        if summary: summaries.append(summary)
                    except:
                        pass

        # Filter out any None values that might have slipped through
        summaries = [s for s in summaries if s]

        if len(summaries) > 1:
            # Combine summaries if multi-chunk
            final_prompt = f"Combine these summaries into one comprehensive deep analysis:\n\n" + "\n\n".join(summaries)
            try:
                res = self._call_gemini_with_retry(final_prompt)
                return res if res else "\n\n".join(summaries)
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
            res = self._call_gemini_with_retry(prompt)
            return res if res else "Deep analysis failed."
        except Exception as e:
            print(f"❌ Gemini Error during deep analysis: {e}")
            return "Deep analysis failed."

if __name__ == "__main__":
    # Test (requires API key)
    summarizer = GeminiSummarizer()
    # print(summarizer.summarize_text("Test content here..."))
