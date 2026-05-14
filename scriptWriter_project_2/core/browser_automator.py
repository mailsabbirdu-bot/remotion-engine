import time
import random
from playwright.sync_api import sync_playwright

class BrowserAI:
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.initialized = False

    def start(self):
        """
        Initialize the browser and navigate to Gemini.
        """
        if self.initialized:
            return

        print("🌐 [BROWSER] Starting headless browser...")
        self.playwright = sync_playwright().start()
        # Using a persistent context to potentially keep cookies/session if needed
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        self.page = self.context.new_page()

        print("🌐 [BROWSER] Navigating to Gemini (gemini.google.com)...")
        self.page.goto("https://gemini.google.com/app")

        # Wait for the chat input to be available - this also acts as a check for being logged in
        try:
            self.page.wait_for_selector("div[contenteditable='true']", timeout=30000)
            print("✅ [BROWSER] Gemini interface loaded.")
            self.initialized = True
        except Exception:
            print("⚠️ [BROWSER] Could not find Gemini input. You might need to be logged in.")
            # In a real scenario, we might need to handle login or wait for user
            self.initialized = True # Proceeding anyway, hoping for the best or manual intervention in non-headless

    def send_prompt(self, prompt, wait_time=15):
        """
        Send a prompt to Gemini and extract the response.
        """
        if not self.initialized:
            self.start()

        try:
            print(f"💬 [BROWSER] Sending prompt ({len(prompt)} chars)...")

            # Clear previous if necessary (optional)
            # Find input area
            input_selector = "div[contenteditable='true']"
            self.page.fill(input_selector, prompt)

            # Press Enter or click send
            self.page.keyboard.press("Enter")

            print(f"⏳ [BROWSER] Waiting for AI response (~{wait_time}s)...")
            time.sleep(wait_time)

            # Extract the last response
            # Note: Selectors might change as Google updates the UI
            responses = self.page.query_selector_all(".model-response-text")
            if responses:
                last_response = responses[-1].inner_text()
                print(f"✅ [BROWSER] Received response ({len(last_response)} chars).")
                return last_response
            else:
                # Fallback selector if the above fails
                responses = self.page.query_selector_all("message-content")
                if responses:
                    last_response = responses[-1].inner_text()
                    return last_response

            print("⚠️ [BROWSER] Could not extract response text.")
            return None
        except Exception as e:
            print(f"❌ [BROWSER] Error during automation: {e}")
            return None

    def close(self):
        if self.playwright:
            self.browser.close()
            self.playwright.stop()
            self.initialized = False

if __name__ == "__main__":
    # Test
    ai = BrowserAI(headless=False)
    ai.start()
    res = ai.send_prompt("Hello, who are you?")
    print(f"Response: {res}")
    ai.close()
