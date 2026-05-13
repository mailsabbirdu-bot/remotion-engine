import google.generativeai as genai
import os
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import GEMINI_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP

class GeminiSummarizer:
    def __init__(self, api_key=None):
        self.local_model = None
        self.local_tokenizer = None
        if not api_key:
            api_key = GEMINI_API_KEY

        print(f"🔑 [SUMMARIZER] Initializing Gemini API with key: {api_key[:10]}...{api_key[-5:]}")

        try:
            genai.configure(api_key=api_key)
            # Efficiently find an available model
            available_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

            # Prioritized preference list
            preferred_models = [
                'gemini-2.0-flash', 'gemini-1.5-flash',
                'gemini-flash-latest', 'gemini-pro-latest', 'gemini-pro'
            ]

            self.model = None
            for model_name in preferred_models:
                if model_name in available_models:
                    self.model = genai.GenerativeModel(model_name)
                    print(f"✅ [SUMMARIZER] Gemini {model_name} Model selected.")
                    break

            if not self.model:
                # We won't setup local LLM here anymore to save time.
                # It will be setup lazily in summarize_text if needed.
                print("⚠️ [SUMMARIZER] Gemini unavailable. Local fallback will be used if needed.")

            if not self.model and not self.local_model:
                # Absolute fallback to first available model
                if available_models:
                    self.model = genai.GenerativeModel(available_models[0])
                    print(f"⚠️ [SUMMARIZER] Using absolute fallback model: {available_models[0]}")
                else:
                    raise Exception("No Gemini models available for this API key.")

        except Exception as e:
            print(f"❌ [SUMMARIZER] Failed to initialize Gemini: {e}")

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

    def _setup_local_llm(self):
        """
        Initialize a very lightweight local LLM optimized for CPU fallback.
        """
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM

            # Qwen2.5-0.5B is extremely capable for its size and fast on CPU
            model_id = "Qwen/Qwen2.5-0.5B-Instruct"
            print(f"📥 [LOCAL LLM] Loading {model_id} for CPU fallback...")

            self.local_tokenizer = AutoTokenizer.from_pretrained(model_id)
            device = "cuda" if torch.cuda.is_available() else "cpu"

            # CPU-friendly loading
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

    def _call_gemini_with_retry(self, prompt, retries=3, initial_delay=5):
        """
        Call Gemini API with exponential backoff to handle 429 errors.
        """
        delay = initial_delay
        for attempt in range(retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                if "429" in str(e) and attempt < retries - 1:
                    print(f"⚠️ Quota exceeded. Retrying in {delay} seconds... (Attempt {attempt+1}/{retries})")
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise e
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
            # Respect Free Tier RPM limits
            if i > 0:
                time.sleep(2)

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
                if self.model:
                    summary = self._call_gemini_with_retry(prompt)
                else:
                    if not self.local_model: self._setup_local_llm()
                    summary = self._summarize_locally(chunk, source_type)
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
                        summaries.append(summary)
                    except:
                        summaries.append(f"Summary failed for chunk {i}")
                else:
                    summaries.append(f"Summary failed for chunk {i}")

        if len(summaries) > 1:
            # Combine summaries if multi-chunk
            final_prompt = f"Combine these summaries into one comprehensive deep analysis:\n\n" + "\n\n".join(summaries)
            try:
                return self._call_gemini_with_retry(final_prompt)
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
            return self._call_gemini_with_retry(prompt)
        except Exception as e:
            print(f"❌ Gemini Error during deep analysis: {e}")
            return "Deep analysis failed."

if __name__ == "__main__":
    # Test (requires API key)
    summarizer = GeminiSummarizer()
    # print(summarizer.summarize_text("Test content here..."))
