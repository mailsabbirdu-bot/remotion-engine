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
    def __init__(self, headless=True, session_path=None):
        self.headless = headless
        # Use Drive-based session by default in Colab if path not provided
        if session_path is None:
            if os.path.exists("/content/drive/MyDrive"):
                self.session_path = "/content/drive/MyDrive/Counterism_Studio_V4/voiceover_session"
            else:
                self.session_path = "voiceover_session"
        else:
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

        print(f"🌐 [BROWSER] Starting browser with session at: {self.session_path}")
        self.playwright = sync_playwright().start()

        # Ensure session directory exists
        os.makedirs(self.session_path, exist_ok=True)

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
            self.page.goto("https://aistudio.google.com/generate-speech", timeout=90000)

            # Check if login is required
            if "signin" in self.page.url or "accounts.google.com" in self.page.url:
                print("\n" + "!"*50)
                print("🔑 [BROWSER] LOGIN REQUIRED!")
                print("Since you are a novice, follow these steps exactly:")
                print("1. The script will try to wait for you.")
                print("2. If you are in Colab and this is headless, IT WILL FAIL.")
                print("3. Solution: You must ensure the 'voiceover_session' folder in your Drive has valid login data.")
                print("!"*50 + "\n")

                if self.headless:
                    print("❌ ERROR: Cannot login in headless mode.")
                    # We'll try to wait anyway in case the user has a way to interact

                print("👉 Waiting for you to log in or for the interface to appear...")
                try:
                    self.page.wait_for_selector("textarea", timeout=300000)
                    print("✅ [BROWSER] Interface detected! Proceeding...")
                except:
                    print("❌ [BROWSER] Timeout waiting for login/interface.")
                    raise Exception("Login required but not completed.")

            # Basic cookie/consent handling if it appears
            try:
                consent_selectors = ["button:has-text('I agree')", "button:has-text('Accept all')", "button:has-text('Accept')"]
                for selector in consent_selectors:
                    if self.page.is_visible(selector, timeout=5000):
                        self.page.click(selector)
                        break
            except:
                pass

            # Wait for the textarea to be available
            self.page.wait_for_selector("textarea", timeout=60000)
            print("✅ [BROWSER] AI Studio Generate Speech interface loaded.")
            self.initialized = True
        except Exception as e:
            print(f"⚠️ [BROWSER] Initialization failed: {e}")
            # Save screenshot for ultra debugging
            try:
                self.page.screenshot(path="init_error.png")
                print("📸 Screenshot saved to init_error.png")
            except:
                pass
            raise

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
            self.page.wait_for_selector(input_selector, timeout=15000)

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
                try:
                    self.page.click("button:visible:has-text('Generate')")
                    button_found = True
                except:
                    pass

            if not button_found:
                print("❌ [BROWSER] Generate button NOT found.")
                return False

            print("⏳ [BROWSER] Waiting for download to start (checking for Download button or auto-download)...")

            # Setup download listener
            try:
                with self.page.expect_download(timeout=120000) as download_info:
                    # Check if a download button appears
                    download_button_selectors = [
                        "button:has-text('Download')",
                        "a:has-text('Download')",
                        "button[aria-label='Download audio']",
                        ".download-button"
                    ]

                    # Polling for download button or auto-trigger
                    for _ in range(30):
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
                print(f"⚠️ [BROWSER] Download failed or timed out: {e}")
                return False

        except Exception as e:
            print(f"❌ [BROWSER] Error during generation/download: {e}")
            return False

    def close(self):
        if self.playwright:
            try:
                self.context.close()
                self.playwright.stop()
            except:
                pass
            self.initialized = False
