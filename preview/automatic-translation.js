/* Solaire Film District — automatic browser-language translation (static GitHub Pages).
   Uses the isolated staging Supabase Edge Function endpoint; production is unchanged.
   No language picker, login, or third-party scripts. */
(() => {
  "use strict";
  const API_BASE = "https://titeccsfyanjqmzofjrr.supabase.co/functions/v1/";
  const isProduction = ["solairefilmdistrict.fr", "www.solairefilmdistrict.fr"].includes(location.hostname);
  const API = API_BASE + (isProduction ? "translate-website" : "translate-website-staging");
  const language = (navigator.languages?.[0] || navigator.language || "en").split("-")[0].toLowerCase();
  // Keep the English page visible until a complete translated batch is ready.
  // Swapping the batch synchronously avoids visibly mixing two languages.
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
  async function prepareText(node) {
    if (pending.has(node) || completed.has(node)) return null;
    const source = originals.get(node) || node.textContent;
    if (!source?.trim() || source.length > 800) return null;
    const marked = node.parentElement?.closest("[lang]");
    if (marked && marked !== document.documentElement && marked.lang.split("-")[0].toLowerCase() !== pageLanguage) return null;
    originals.set(node, source); pending.add(node);
    try {
      const value = await translate(source);
      return value ? {node, source, value} : null;
    } finally { pending.delete(node); }
  }
  // Translate visitor-facing attributes as well as visible text.
  // Keep addresses, form field names, URLs, values and user input untouched.
  const attributes = ["placeholder", "aria-label", "title", "alt"];
  const attributeDone = new WeakMap();
  async function prepareAttributes(element) {
    if (element.closest(protectedSelector + ",[hidden]")) return [];
    let seen = attributeDone.get(element);
    if (!seen) { seen = new Set(); attributeDone.set(element, seen); }
    const updates = [];
    for (const attribute of attributes) {
      if (seen.has(attribute) || !element.hasAttribute(attribute)) continue;
      const original = element.getAttribute(attribute);
      if (!original || original.trim().length < 2 || original.length > 800) continue;
      seen.add(attribute);
      const translated = await translate(original);
      if (!translated) seen.delete(attribute);
      else updates.push({element, attribute, original, translated});
    }
    return updates;
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
  let scanning = false, scanAgain = false;
  async function scan() {
    if (scanning) { scanAgain = true; return; }
    scanning = true;
    try {
      const nodes = textNodes().filter(node => !completed.has(node));
      const elements = [...document.querySelectorAll("[placeholder],[aria-label],[title],[alt]")];
      const [texts, attrs] = await Promise.all([
        Promise.all(nodes.map(prepareText)),
        Promise.all(elements.map(prepareAttributes))
      ]);
      // Never show a half-translated page. On any failure retain the English original.
      if (texts.some((item, i) => !item && !completed.has(nodes[i]))) {
        // Attributes were prepared but not displayed. Allow retry with a later batch.
        for (const group of attrs) for (const {element, attribute} of group) {
          attributeDone.get(element)?.delete(attribute);
        }
        return;
      }
      const changes = texts.filter(Boolean);
      // A late DOM update can invalidate a prepared translation batch.
      // Abort the entire batch rather than mixing translated and new English text.
      if (changes.some(({node, source}) => !node.isConnected || node.nodeValue !== source)) {
        for (const group of attrs) for (const {element, attribute} of group) {
          attributeDone.get(element)?.delete(attribute);
        }
        scanAgain = true;
        return;
      }
      // All visible text updates are synchronous, so the browser paints one language.
      for (const {node, value} of changes) {
        node.nodeValue = value;
        completed.add(node);
      }
      for (const group of attrs) for (const {element, attribute, original, translated} of group) {
        if (element.isConnected && element.getAttribute(attribute) === original) element.setAttribute(attribute, translated);
      }
      if (changes.length) {
        document.documentElement.lang = language;
        document.documentElement.dir = ["ar", "he", "fa", "ur"].includes(language) ? "rtl" : "ltr";
      }
    } finally {
      scanning = false;
      if (scanAgain) { scanAgain = false; void scan(); }
    }
  }
  new MutationObserver(() => { void scan(); }).observe(document.documentElement, { childList: true, subtree: true });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => { void scan(); }, { once: true });
  else void scan();
})();
