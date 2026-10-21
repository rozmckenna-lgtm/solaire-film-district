/* Solaire Film District — automatic browser-language translation (static GitHub Pages).
   Production API endpoint is deliberately unset until the secured backend is deployed.
   No language picker, login, or third-party scripts. */
(() => {
  "use strict";
  const API = window.SOLAIRE_TRANSLATION_ENDPOINT;
  const language = (navigator.languages?.[0] || navigator.language || "en").split("-")[0].toLowerCase();
  if (language === "en" || !/^[a-z]{2,3}$/.test(language) || !API) return;
  const protectedSelector = "script,style,noscript,textarea,code,pre,svg,[contenteditable],[translate='no'],[data-no-translate],iframe";
  const originals = new WeakMap(), cache = new Map(), pending = new Set();
  const textNodes = () => {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const nodes = []; let node;
    while ((node = walker.nextNode())) {
      if (!node.parentElement || node.parentElement.closest(protectedSelector)) continue;
      const value = node.textContent;
      if (value.trim().length >= 2 && value.length <= 800) nodes.push(node);
    }
    return nodes;
  };
  async function translate(source) {
    const key = language + ":" + source;
    if (!cache.has(key)) cache.set(key, fetch(API, {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ contentId: "auto", sourceText: source, sourceLanguage: "en", targetLanguage: language })
    }).then(async r => {
      const body = await r.json().catch(() => ({}));
      return r.ok && (body.status === "translated" || body.status === "cached") && typeof body.text === "string" ? body.text : null;
    }).catch(() => null));
    return cache.get(key);
  }
  async function process(node) {
    if (pending.has(node)) return;
    const source = originals.get(node) || node.textContent;
    if (!source?.trim() || source.length > 800) return;
    if (node.parentElement?.closest('[lang]:not([lang="en"])')) return; // Existing French passages must remain French.
    originals.set(node, source); pending.add(node);
    try {
      const value = await translate(source);
      if (value && node.isConnected && (node.textContent === source || node.textContent === value)) node.textContent = value;
    } finally { pending.delete(node); }
  }
  let queued = false;
  function scan() {
    if (queued) return; queued = true;
    queueMicrotask(() => {
      queued = false;
      for (const node of textNodes()) if (!originals.has(node) || node.textContent === originals.get(node)) void process(node);
    });
  }
  new MutationObserver(scan).observe(document.documentElement, { childList: true, subtree: true });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", scan, { once: true });
  else scan();
})();
