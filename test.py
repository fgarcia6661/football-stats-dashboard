from playwright.sync_api import sync_playwright
import time

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://futfrede.streamlit.app/", wait_until="networkidle", timeout=90000)
        time.sleep(15)
        page.screenshot(path="screenshot_main.png")

        # Streamlit renders inside an iframe - find it
        try:
            frame = None
            for f in page.frames:
                try:
                    btns = f.query_selector_all("button")
                    for b in btns:
                        if "Generar Radar" in (b.inner_text() or ""):
                            frame = f
                            break
                except Exception:
                    pass
                if frame:
                    break

            if frame:
                btn = frame.locator("button:has-text('Generar Radar')")
                btn.click()
                print("Button clicked!")
            else:
                # Fallback: click by text anywhere
                page.get_by_text("Generar Radar").first.click()
                print("Fallback click!")

            time.sleep(12)
            page.screenshot(path="screenshot_radar.png")
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="screenshot_error.png")

        browser.close()

if __name__ == "__main__":
    test_app()
