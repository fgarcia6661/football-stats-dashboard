from playwright.sync_api import sync_playwright
import time

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://futfrede.streamlit.app/", wait_until="networkidle", timeout=60000)
        # Wait a bit more for Streamlit to render data
        time.sleep(15)

        # Get all text
        text = page.locator("body").inner_text()
        print("PAGE TEXT:")
        print(text)

        # Also let's click the other modules to see if they crash
        page.screenshot(path="screenshot_main.png")

        browser.close()

if __name__ == "__main__":
    test_app()
