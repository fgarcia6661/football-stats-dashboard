from playwright.sync_api import sync_playwright
import time

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://futfrede.streamlit.app/", wait_until="networkidle", timeout=60000)
        time.sleep(15)

        # Click Generar Radar
        page.locator("button:has-text('Generar Radar')").click()
        time.sleep(10)

        page.screenshot(path="screenshot_main.png")

        browser.close()

if __name__ == "__main__":
    test_app()
