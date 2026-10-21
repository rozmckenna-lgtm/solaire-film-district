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
            response = page.goto(BASE + page_name, wait_until="domcontentloaded", timeout=30000)
            assert response and response.status == 200, f"{device} {page_name}: HTTP {response.status if response else 'no response'}"
            page.wait_for_function("document.body.innerText.includes('FR_TEST:')", timeout=30000)
            page.wait_for_function("document.title.startsWith('FR_TEST:')", timeout=30000)
            assert page.locator("script[src=\'automatic-translation.js\']").count() == 1, f"{device} {page_name}: translation script missing or duplicated"
            assert page.locator("img[src=\'../logo-solaire.jpeg\']").evaluate_all("(images) => images.every(img => img.complete && img.naturalWidth > 0)") if page.locator("img[src=\'../logo-solaire.jpeg\']").count() else True, f"{device} {page_name}: Solaire logo not loaded"
            if page_name == "index.html":
                hero = page.locator(".hero")
                assert hero.count() == 1, f"{device}: cinematic globe hero missing"
                page.wait_for_function("getComputedStyle(document.querySelector(\'.hero\')).backgroundImage.includes(\'fd49a2c7f_generated_image.png\')", timeout=15000)
                image = page.request.get("https://media.base44.com/images/public/6ad768462ea55ab133e15a41/fd49a2c7f_generated_image.png", timeout=20000)
                assert image.ok and image.headers.get("content-type", "").startswith("image/"), f"{device}: globe asset unavailable: {image.status}"
            page.screenshot(path=str(OUT / (device + "-" + page_name.replace(".html", ".png"))), full_page=True)
            assert not errors, f"{device} {page_name}: {errors}"
            assert page.locator("html").get_attribute("lang") == "en", "English source language changed"
            assert page.locator("body").evaluate("(el) => el.scrollWidth <= window.innerWidth + 3"), f"{device} horizontal overflow: {page_name}"
            print("PASS", device, page_name)
            page.close()
        context.close()
    browser.close()
