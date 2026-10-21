from pathlib import Path
from playwright.sync_api import sync_playwright
import json

PAGES = ["index.html", "creators.html", "decision-makers.html", "pitchup.html", "loi.html", "creator-centre.html", "distracted-audience.html", "does-a-story-have-to-be-fast.html", "john-malkovich.html", "realistic-film-budget.html", "screenplay-baby.html", "thank-you.html"]
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
            page.route("**/functions/v1/translate-website-staging", mock_translation)
            response = page.goto(BASE + page_name, wait_until="domcontentloaded", timeout=30000)
            assert response and response.status == 200, f"{device} {page_name}: HTTP {response.status if response else 'no response'}"
            page.wait_for_function("document.body.innerText.includes('FR_TEST:')", timeout=30000)
            page.wait_for_function("document.title.startsWith('FR_TEST:')", timeout=30000)
            if page_name == "index.html":
                page.wait_for_function("document.querySelector('meta[name=description]')?.content.startsWith('FR_TEST:')", timeout=30000)
                print("PASS", device, "translated-description-metadata", flush=True)
            assert page.locator("script[src=\'automatic-translation.js\']").count() == 1, f"{device} {page_name}: translation script missing or duplicated"
            assert page.locator("img[src=\'../logo-solaire.jpeg\']").evaluate_all("(images) => images.every(img => img.complete && img.naturalWidth > 0)") if page.locator("img[src=\'../logo-solaire.jpeg\']").count() else True, f"{device} {page_name}: Solaire logo not loaded"
            if page_name == "loi.html":
                redirect = page.locator('form[action="https://formspree.io/f/xwvkjpaz"] input[name="_next"]').input_value()
                assert redirect == BASE + "thank-you.html", f"{device}: LOI confirmation redirect wrong: {redirect}"
                print("PASS", device, "LOI-same-origin-confirmation-redirect", flush=True)
            if page_name == "index.html":
                hero = page.locator(".hero")
                assert hero.count() == 1, f"{device}: cinematic globe hero missing"
                css_url = BASE + "cinematic.css"
                css_response = page.request.get(css_url, timeout=15000)
                css_text = css_response.text()
                assert css_response.ok and "fd49a2c7f_generated_image.png" in css_text, f"{device}: cinematic stylesheet missing globe URL"
                # Reference-parity design intentionally paints the illuminated globe on BODY
                # so it continues behind the project cards; the hero overlays gradients.
                computed = page.locator("body").evaluate("(el) => getComputedStyle(el).backgroundImage")
                assert "fd49a2c7f_generated_image.png" in computed, f"{device}: globe missing from page background: {computed}"
                # Verify five downloadable guides actually resolve, not merely that links exist.
                pdf_links = page.locator('a[href$=".pdf"]').evaluate_all("(els) => [...new Set(els.map(a => a.href))]")
                assert len(pdf_links) == 5, f"{device}: expected 5 PDFs, found {len(pdf_links)}"
                for pdf_url in pdf_links:
                    pdf = page.request.get(pdf_url, timeout=15000)
                    assert pdf.ok and pdf.body().startswith(b"%PDF-"), f"{device}: invalid PDF {pdf_url} ({pdf.status})"
                print("PASS", device, "five-PDF-content-signatures", flush=True)
                # Verify every local HTML navigation target resolves.
                internal_links = page.locator('a[href]').evaluate_all("""(els) => [...new Set(els.map(a => a.href).filter(u => u.startsWith(location.origin) && /\\.html(?:#.*)?$/.test(u)))]""")
                for target in internal_links:
                    nav = page.request.get(target.split("#")[0], timeout=15000)
                    assert nav.ok, f"{device}: broken local navigation {target} ({nav.status})"
                print("PASS", device, "internal-navigation-targets", len(internal_links), flush=True)
                image = page.request.get("https://media.base44.com/images/public/6ad768462ea55ab133e15a41/fd49a2c7f_generated_image.png", timeout=20000)
                assert image.ok and image.headers.get("content-type", "").startswith("image/"), f"{device}: globe asset unavailable: {image.status}"
            page.screenshot(path=str(OUT / (device + "-" + page_name.replace(".html", ".png"))), full_page=True)
            assert not errors, f"{device} {page_name}: {errors}"
            assert page.locator("html").get_attribute("lang") == "fr", "Translated page must declare visitor language for screen readers"
            assert page.locator("body").evaluate("(el) => el.scrollWidth <= window.innerWidth + 3"), f"{device} horizontal overflow: {page_name}"
            print("PASS", device, page_name)
            page.close()
        context.close()
    # Verify actual form-submit handling without sending a real Letter of Intent.
    for outcome in ("failure", "success"):
        context = browser.new_context(viewport={"width": 390, "height": 844}, locale="en-GB")
        page = context.new_page()
        requests = []
        def formspree_mock(route):
            requests.append(route.request.method)
            route.fulfill(status=200 if outcome == "success" else 422,
                          content_type="application/json",
                          headers={"access-control-allow-origin": "*"},
                          body='{"ok":true}' if outcome == "success" else '{"error":"test rejection"}')
        page.route("https://formspree.io/f/xwvkjpaz", formspree_mock)
        page.goto(BASE + "loi.html", wait_until="domcontentloaded")
        page.locator("#org-name").fill("Solaire Test Organisation")
        page.locator("#contact-name").fill("Solaire Test")
        page.locator("#contact-email").fill("test@example.invalid")
        page.locator('button[type="submit"]').click()
        if outcome == "success":
            page.wait_for_url(BASE + "thank-you.html", timeout=10000)
        else:
            page.locator("#loi-form-status").get_by_text("could not be submitted", exact=False).wait_for(timeout=10000)
            assert page.url.endswith("/loi.html"), "Failed submission must not show confirmation"
            assert page.locator('button[type="submit"]').is_enabled(), "Failed submission must permit retry"
        assert requests == ["POST"], "Form submission must send one POST only"
        print("PASS loi-mocked-submit-" + outcome, flush=True)
        context.close()
    # Real browser behaviour with a mocked provider: an Arabic visitor must
    # retain readable English/LTR when translation fails, and switch to
    # Arabic/RTL only when a translated text node actually appears.
    for outcome in ("failure", "success"):
        context = browser.new_context(locale="ar-SA", viewport={"width": 390, "height": 844})
        page = context.new_page()
        page.on("pageerror", lambda e: (_ for _ in ()).throw(AssertionError(str(e))))
        def arabic_response(route):
            if outcome == "failure":
                route.fulfill(status=503, content_type="application/json", body='{"error":"unavailable"}')
            else:
                payload = route.request.post_data_json or {}
                route.fulfill(status=200, content_type="application/json",
                              body=json.dumps({"status":"translated","text":"AR_TEST: " + payload.get("sourceText", "")}))
        page.route("**/functions/v1/translate-website-staging", arabic_response)
        page.goto(BASE + "thank-you.html", wait_until="domcontentloaded")
        if outcome == "success":
            page.wait_for_function("document.body.innerText.includes('AR_TEST:')", timeout=30000)
            assert page.locator("html").get_attribute("lang") == "ar"
            assert page.locator("html").get_attribute("dir") == "rtl"
        else:
            page.wait_for_timeout(2000)
            assert page.locator("html").get_attribute("lang") == "en"
            assert page.locator("html").get_attribute("dir") != "rtl"
            assert "AR_TEST:" not in page.locator("body").inner_text()
        print("PASS arabic-translation-" + outcome + "-direction", flush=True)
        context.close()
    browser.close()
