import time
import random
import os
from playwright.sync_api import sync_playwright
try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

class BrowserAI:
    def __init__(self, headless=True, session_path="gemini_session"):
        self.headless = headless
        self.session_path = session_path
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

        print("🌐 [BROWSER] Starting browser...")
        self.playwright = sync_playwright().start()

        # Use persistent context to save login state
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.session_path,
            headless=self.headless,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )

        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

        if stealth_sync:
            stealth_sync(self.page)

        print("🌐 [BROWSER] Navigating to Gemini (gemini.google.com)...")
        try:
            self.page.goto("https://gemini.google.com/app", timeout=60000)

            # Check if login is required
            if "signin" in self.page.url or self.page.is_visible("a[href*='accounts.google.com']"):
                print("🔑 [BROWSER] Login required!")
                if self.headless:
                    print("❌ ERROR: Cannot login in headless mode. Please run once in non-headless mode to login.")
                    # We continue but it will likely fail
                else:
                    print("👉 Please log in to your Google account in the browser window.")
                    # Wait for the user to login and reach the app
                    self.page.wait_for_selector("div[contenteditable='true']", timeout=300000)
                    print("✅ [BROWSER] Login successful.")

            # Basic cookie/consent handling if it appears
            try:
                consent_selectors = ["button:has-text('I agree')", "button:has-text('Accept all')", "button:has-text('Accept')"]
                for selector in consent_selectors:
                    if self.page.is_visible(selector, timeout=2000):
                        self.page.click(selector)
                        break
            except:
                pass

            # Wait for the chat input to be available
            self.page.wait_for_selector("div[contenteditable='true']", timeout=30000)
            print("✅ [BROWSER] Gemini interface loaded.")
            self.initialized = True
        except Exception as e:
            print(f"⚠️ [BROWSER] Could not fully initialize Gemini: {e}")
            self.initialized = True # Proceed anyway

    def is_logged_in(self):
        """Checks if the user is logged in and the chat interface is ready."""
        try:
            return self.page.is_visible("div[contenteditable='true']", timeout=5000)
        except:
            return False

    def new_chat(self):
        """Starts a fresh conversation to avoid UI lag."""
        try:
            print("🆕 [BROWSER] Starting new chat...")
            new_chat_selectors = ["a[href='/app']", "button:has-text('New chat')", "[data-test-id='new-chat-button']"]
            for s in new_chat_selectors:
                if self.page.is_visible(s, timeout=2000):
                    self.page.click(s)
                    time.sleep(2)
                    return True
            self.page.goto("https://gemini.google.com/app", timeout=30000)
            time.sleep(3)
            return True
        except:
            return False

    def send_prompt(self, prompt, wait_time=5, timeout=180):
        """
        Send a prompt to Gemini and extract the response with dynamic waiting.
        """
        if not self.initialized:
            self.start()

        try:
            # Handle potential overlays
            try:
                for selector in ["button:has-text('Got it')", "button:has-text('Dismiss')", "button:has-text('Close')"]:
                    if self.page.is_visible(selector, timeout=1000):
                        self.page.click(selector)
            except: pass

            print(f"💬 [BROWSER] Sending prompt ({len(prompt)} chars)...")

            input_selector = "div[contenteditable='true']"
            self.page.wait_for_selector(input_selector, timeout=15000)

            # Focus and clear input
            self.page.click(input_selector)
            time.sleep(0.5)
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")

            # Fill the prompt
            self.page.fill(input_selector, prompt)
            time.sleep(0.5)

            # Press Send button
            send_button_selectors = [
                "button[aria-label='Send message']",
                "button:has(mat-icon[fonticon='send'])",
                ".send-button-container button"
            ]

            sent = False
            for selector in send_button_selectors:
                try:
                    if self.page.is_visible(selector, timeout=3000):
                        self.page.click(selector)
                        sent = True
                        break
                except: continue

            if not sent:
                print("⌨️ [BROWSER] Button click failed, using Enter key...")
                self.page.keyboard.press("Enter")

            print(f"⏳ [BROWSER] Waiting for AI response (up to {timeout}s)...")

            # Generation indicators
            stop_button_selector = "button[aria-label='Stop generating']"
            send_button_selector = "button[aria-label='Send message']"

            # 1. Wait for stop button to appear (indicates generation started)
            try:
                self.page.wait_for_selector(stop_button_selector, state="visible", timeout=10000)
            except:
                pass

            # 2. Wait for stop button to disappear (indicates generation finished)
            try:
                self.page.wait_for_selector(stop_button_selector, state="hidden", timeout=timeout*1000)
            except:
                print("⚠️ [BROWSER] Timeout waiting for 'Stop generating' to disappear.")

            # 3. Wait for send button to be enabled (final confirmation)
            try:
                self.page.wait_for_selector(f"{send_button_selector}:not([disabled])", state="visible", timeout=15000)
            except:
                print("⚠️ [BROWSER] Send button did not re-enable in time.")

            # Brief pause for DOM to settle
            time.sleep(wait_time)

            # Extraction selectors
            extract_selectors = [
                "message-content",
                ".model-response-text",
                ".markdown",
                "div[data-message-author-role='assistant']"
            ]

            for selector in extract_selectors:
                responses = self.page.query_selector_all(selector)
                if responses:
                    last_response = responses[-1].inner_text()
                    if last_response and len(last_response.strip()) > 10:
                        print(f"✅ [BROWSER] Received response ({len(last_response)} chars).")
                        return last_response

            print("⚠️ [BROWSER] Could not extract response text. Selectors might be outdated.")
            return None
        except Exception as e:
            print(f"❌ [BROWSER] Error during automation: {e}")
            return None

    def close(self):
        if self.playwright:
            try:
                self.context.close()
                self.playwright.stop()
            except:
                pass
            self.initialized = False

if __name__ == "__main__":
    # Test
    ai = BrowserAI(headless=False)
    ai.start()
    res = ai.send_prompt("Hello, who are you?")
    print(f"Response: {res}")
    ai.close()
