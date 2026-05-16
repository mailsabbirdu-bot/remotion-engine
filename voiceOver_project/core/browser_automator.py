import time
import random
import os
import re
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
        Initialize the browser and navigate to Google AI Studio Generate Speech.
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

        print("🌐 [BROWSER] Navigating to Google AI Studio (Generate Speech)...")
        try:
            self.page.goto("https://aistudio.google.com/generate-speech", timeout=60000)

            # Check if login is required
            if "signin" in self.page.url or "accounts.google.com" in self.page.url:
                print("🔑 [BROWSER] Login required!")
                if self.headless:
                    print("❌ ERROR: Cannot login in headless mode. Please run once in non-headless mode to login.")
                else:
                    print("👉 Please log in to your Google account in the browser window.")
                    # Wait for the interface to load after login
                    self.page.wait_for_selector("textarea", timeout=300000)
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

            # Wait for the textarea to be available
            self.page.wait_for_selector("textarea", timeout=30000)
            print("✅ [BROWSER] AI Studio Generate Speech interface loaded.")
            self.initialized = True
        except Exception as e:
            print(f"⚠️ [BROWSER] Could not fully initialize AI Studio: {e}")
            self.initialized = True

    def paste_text(self, text):
        """
        Paste text into the input field.
        """
        if not self.initialized:
            self.start()

        try:
            print(f"💬 [BROWSER] Pasting scene text ({len(text)} chars)...")

            # Selector for the main input field in Generate Speech
            input_selector = "textarea"
            self.page.wait_for_selector(input_selector, timeout=10000)

            # Focus and clear input
            self.page.click(input_selector)
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")

            # Fill the prompt
            self.page.fill(input_selector, text)
            print("✅ [BROWSER] Text pasted successfully.")
            return True
        except Exception as e:
            print(f"❌ [BROWSER] Error during pasting: {e}")
            return False

    def generate_and_download(self, output_path):
        """
        Trigger audio generation and download the file.
        """
        if not self.initialized:
            self.start()

        try:
            print("⏳ [BROWSER] Triggering audio generation...")

            # Common selectors for generate button
            generate_button_selectors = [
                "button:has-text('Generate')",
                "button:has-text('Run')",
                "button[aria-label='Generate speech']",
                ".generate-button"
            ]

            button_found = False
            for selector in generate_button_selectors:
                if self.page.is_visible(selector):
                    print(f"🖱️ [BROWSER] Clicking generate button: {selector}")
                    self.page.click(selector)
                    button_found = True
                    break

            if not button_found:
                print("⚠️ [BROWSER] Generate button not found by common selectors. Trying to find any primary button...")
                # Fallback: try to find a button with 'Generate' in it
                self.page.click("button:visible:has-text('Generate')")

            print("⏳ [BROWSER] Waiting for generation to complete and download to start...")

            # Setup download listener
            with self.page.expect_download(timeout=120000) as download_info:
                # Some sites might need a click on a Download button AFTER generation
                # If generation is automatic download, this will catch it.
                # If not, we might need to find a download button.

                # Check if a download button appears
                download_button_selectors = [
                    "button:has-text('Download')",
                    "a:has-text('Download')",
                    "button[aria-label='Download audio']"
                ]

                # We wait a bit for generation
                time.sleep(5)

                for _ in range(20): # Polling for download button
                    for selector in download_button_selectors:
                        if self.page.is_visible(selector):
                            print(f"🖱️ [BROWSER] Clicking download button: {selector}")
                            self.page.click(selector)
                            break
                    else:
                        time.sleep(2)
                        continue
                    break

            download = download_info.value
            download.save_as(output_path)
            print(f"✅ [BROWSER] Audio downloaded successfully to: {output_path}")
            return True

        except Exception as e:
            print(f"❌ [BROWSER] Error during generation/download: {e}")
            # Screenshot for debugging
            try:
                self.page.screenshot(path="error_debug.png")
                print("📸 [BROWSER] Error screenshot saved to error_debug.png")
            except:
                pass
            return False

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
    # ai.paste_text("This is a test of the emergency broadcast system.")
    # ai.generate_and_download("test.wav")
    ai.close()
