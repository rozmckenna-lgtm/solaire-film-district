/* Solaire Film District — automatic browser-language translation (static GitHub Pages).
   Uses the secured production Supabase Edge Function endpoint.
   No language picker, login, or third-party scripts. */
(() => {
  "use strict";
  const API = "https://titeccsfyanjqmzofjrr.supabase.co/functions/v1/translate-website";
  const language = (navigator.languages?.[0] || navigator.language || "en").split("-")[0].toLowerCase();
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
      cache.set(key, schedule(() => fetch(API, {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ contentId: "auto", sourceText: source, sourceLanguage: pageLanguage, targetLanguage: language })
    }).then(async r => {
      const body = await r.json().catch(() => ({}));
      return r.ok && (body.status === "translated" || body.status === "cached") && typeof body.text === "string" ? body.text : null;
    }).catch(() => null)));
    }
    return cache.get(key);
  }
  async function process(node) {
    if (pending.has(node) || completed.has(node)) return;
    const source = originals.get(node) || node.textContent;
    if (!source?.trim() || source.length > 800) return;
    // Preserve inline passages in a language different from the page source.
    const marked = node.parentElement?.closest("[lang]");
    if (marked && marked.lang.split("-")[0].toLowerCase() !== pageLanguage) return;
    if (node.parentElement?.closest(".bilingual, .hero-intro") && node.parentElement?.closest("[hidden]")) return;
    originals.set(node, source); pending.add(node);
    try {
      const value = await translate(source);
      if (value && node.isConnected && node.nodeValue === source) node.nodeValue = value;
      completed.add(node);
    } finally { pending.delete(node); }
  }
  let queued = false;
  function scan() {
    if (queued) return; queued = true;
    queueMicrotask(() => {
      queued = false;
      for (const node of textNodes()) if (!completed.has(node)) void process(node);
    });
  }
  new MutationObserver(scan).observe(document.documentElement, { childList: true, subtree: true });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", scan, { once: true });
  else scan();
})();
