/* Solaire Film District — automatic browser-language translation (static GitHub Pages).
   Uses the isolated staging Supabase Edge Function endpoint; production is unchanged.
   No language picker, login, or third-party scripts. */
(() => {
  "use strict";
  const API_BASE = "https://titeccsfyanjqmzofjrr.supabase.co/functions/v1/";
  const isProduction = ["solairefilmdistrict.fr", "www.solairefilmdistrict.fr"].includes(location.hostname);
  const API = API_BASE + (isProduction ? "translate-website" : "translate-website-staging");
  const language = (navigator.languages?.[0] || navigator.language || "en").split("-")[0].toLowerCase();
  // Keep the document language accurate for screen readers once translated content arrives.
  // Do not change it on failed requests, when the visible page remains English.
  let translatedCount = 0;
  function markTranslated() {
    translatedCount++;
    if (translatedCount === 1) {
      document.documentElement.lang = language;
      if (["ar", "he", "fa", "ur"].includes(language)) document.documentElement.dir = "rtl";
    }
  }
  if (!/^[a-z]{2,3}$/.test(language)) return;
  // Staging uses English as the sole canonical source. Never reveal legacy French duplicates.
  const pageLanguage = (document.documentElement.lang || "en").split("-")[0].toLowerCase();
  if (language === pageLanguage) return;
  // On bilingual pages, an already-visible French passage is not English source text.
  // Do not translate it again; only the source-language passages are eligible.
  const protectedSelector = "script,style,noscript,textarea,code,pre,svg,[contenteditable],[translate='no'],[data-no-translate],iframe,.bilingual-fr,.hero-intro-fr";
  const originals = new WeakMap(), cache = new Map(), pending = new Set(), completed = new WeakSet();
  const MAX_CONCURRENT_REQUESTS = 2;
  const queue = []; let active = 0;
  // Decode Google Translate HTML entities as text, never as markup.
  function decodeTranslatedText(value) {
    const named = { amp: "&", quot: '"', apos: "'", lt: "<", gt: ">", nbsp: " " };
    return value.replace(/&(#x[0-9a-f]+|#[0-9]+|amp|quot|apos|lt|gt|nbsp);/gi, (entity, code) => {
      if (code[0] === "#") {
        const numeric = code[1].toLowerCase() === "x" ? parseInt(code.slice(2), 16) : parseInt(code.slice(1), 10);
        return numeric > 0 && numeric <= 0x10ffff && !(numeric >= 0xd800 && numeric <= 0xdfff)
          ? String.fromCodePoint(numeric) : entity;
      }
      return named[code.toLowerCase()] ?? entity;
    });
  }
  const textNodes = () => {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const nodes = []; let node;
    while ((node = walker.nextNode())) {
      if (!node.parentElement || node.parentElement.closest(protectedSelector) || node.parentElement.closest("[hidden]")) continue;
      const value = node.textContent;
      if (value.trim().length >= 2 && value.length <= 800) nodes.push(node);
    }
    return nodes;
  };
  function schedule(job) {
    return new Promise(resolve => {
      queue.push({ job, resolve });
      pump();
    });
  }
  function pump() {
    while (active < MAX_CONCURRENT_REQUESTS && queue.length) {
      const { job, resolve } = queue.shift();
      active++;
      Promise.resolve().then(job).then(resolve, () => resolve(null)).finally(() => { active--; pump(); });
    }
  }
  async function translate(source) {
    const key = pageLanguage + ":" + language + ":" + source;
    if (!cache.has(key)) {
      cache.set(key, schedule(async () => {
        // A stalled translation service must not block both request slots forever.
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 12000);
        try {
          const response = await fetch(API, {
            method: "POST", headers: { "content-type": "application/json" },
            body: JSON.stringify({ contentId: "auto", sourceText: source, sourceLanguage: pageLanguage, targetLanguage: language }),
            signal: controller.signal
          });
          const body = await response.json().catch(() => ({}));
          return response.ok && (body.status === "translated" || body.status === "cached") && typeof body.text === "string" ? decodeTranslatedText(body.text) : null;
        } catch (_) {
          return null; // Leave original English visible and allow a later retry.
        } finally {
          clearTimeout(timeout);
        }
      }));
    }
    const result = await cache.get(key);
    // A transient network/CORS error must not poison the page cache permanently.
    if (!result) cache.delete(key);
    return result;
  }
  async function process(node) {
    if (pending.has(node) || completed.has(node)) return;
    const source = originals.get(node) || node.textContent;
    if (!source?.trim() || source.length > 800) return;
    // Preserve inline passages in a language different from the page source.
    const marked = node.parentElement?.closest("[lang]");
    if (marked && marked !== document.documentElement && marked.lang.split("-")[0].toLowerCase() !== pageLanguage) return;
    if (node.parentElement?.closest(".bilingual, .hero-intro") && node.parentElement?.closest("[hidden]")) return;
    originals.set(node, source); pending.add(node);
    try {
      const value = await translate(source);
      if (value && node.isConnected && node.nodeValue === source) { node.nodeValue = value; markTranslated(); }
      if (value) completed.add(node);
    } finally { pending.delete(node); }
  }
  // Translate visitor-facing attributes as well as visible text.
  // Keep addresses, form field names, URLs, values and user input untouched.
  const attributes = ["placeholder", "aria-label", "title", "alt"];
  const attributeDone = new WeakMap();
  async function processAttributes(element) {
    if (element.closest(protectedSelector + ",[hidden]")) return;
    let seen = attributeDone.get(element);
    if (!seen) { seen = new Set(); attributeDone.set(element, seen); }
    for (const attribute of attributes) {
      if (seen.has(attribute) || !element.hasAttribute(attribute)) continue;
      const original = element.getAttribute(attribute);
      if (!original || original.trim().length < 2 || original.length > 800) continue;
      seen.add(attribute);
      const translated = await translate(original);
      if (!translated) seen.delete(attribute);
      if (translated && element.isConnected && element.getAttribute(attribute) === original)
        element.setAttribute(attribute, translated);
    }
  }
  async function translateDocumentMetadata() {
    const originalTitle = document.title;
    if (originalTitle) {
      const translated = await translate(originalTitle);
      if (translated && document.title === originalTitle) document.title = translated;
    }
    // The document description is shown in browser previews and assistive tools.
    // Do not modify canonical URLs, Open Graph URLs or English source files.
    for (const selector of ['meta[name="description"]', 'meta[property="og:description"]']) {
      const element = document.querySelector(selector);
      const original = element?.getAttribute("content");
      if (!original || original.trim().length < 2 || original.length > 800) continue;
      const translated = await translate(original);
      if (translated && element.isConnected && element.getAttribute("content") === original)
        element.setAttribute("content", translated);
    }
  }
  void translateDocumentMetadata();
  let queued = false;
  function scan() {
    if (queued) return; queued = true;
    queueMicrotask(() => {
      queued = false;
      for (const node of textNodes()) if (!completed.has(node)) void process(node);
      for (const element of document.querySelectorAll("[placeholder],[aria-label],[title],[alt]")) void processAttributes(element);
    });
  }
  new MutationObserver(scan).observe(document.documentElement, { childList: true, subtree: true });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", scan, { once: true });
  else scan();
})();
