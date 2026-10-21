from pathlib import Path
from playwright.sync_api import sync_playwright
import json

PAGES = ["index.html", "creators.html", "decision-makers.html", "pitchup.html", "loi.html", "creator-centre.html", "distracted-audience.html", "does-a-story-have-to-be-fast.html", "john-malkovich.html", "realistic-film-budget.html", "screenplay-baby.html"]
BASE = "http://127.0.0.1:8765/preview/"
OUT = Path("browser-evidence")
OUT.mkdir(exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    for device, viewport in [("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 390, "height": 844})]:
        context = browser.new_context(viewport=viewport, locale="fr-FR", device_scale_factor=1)
        for page_name in PAGES:
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            def mock_translation(route):
                payload = route.request.post_data_json or {}
                text = payload.get("sourceText", "")
                route.fulfill(status=200, content_type="application/json", headers={"access-control-allow-origin": "*"}, body=json.dumps({"status":"translated","text":"FR_TEST: " + text}))
            page.route("**/functions/v1/translate-website", mock_translation)
            page.goto(BASE + page_name, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_function("document.body.innerText.includes('FR_TEST:')", timeout=30000)
            page.screenshot(path=str(OUT / (device + "-" + page_name.replace(".html", ".png"))), full_page=True)
            assert not errors, f"{device} {page_name}: {errors}"
            assert page.locator("html").get_attribute("lang") == "en", "English source language changed"
            assert page.locator("body").evaluate("(el) => el.scrollWidth <= window.innerWidth + 3"), f"{device} horizontal overflow: {page_name}"
            print("PASS", device, page_name)
            page.close()
        context.close()
    browser.close()
