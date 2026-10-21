/* Solaire Film District — automatic browser-language translation (static GitHub Pages).
   Uses the secured production Supabase Edge Function endpoint.
   No language picker, login, or third-party scripts. */
(() => {
  "use strict";
  const API = "https://titeccsfyanjqmzofjrr.supabase.co/functions/v1/translate-website";
  const language = (navigator.languages?.[0] || navigator.language || "en").split("-")[0].toLowerCase();
  if (language === "en" || !/^[a-z]{2,3}$/.test(language)) return;
  const protectedSelector = "script,style,noscript,textarea,code,pre,svg,[contenteditable],[translate='no'],[data-no-translate],iframe";
  const originals = new WeakMap(), cache = new Map(), pending = new Set(), completed = new WeakSet();
  const MAX_UNIQUE_REQUESTS = 24; // Limit requests; server budget remains authoritative.
  const MAX_SOURCE_CHARACTERS = 2500; // Conservative per-page ceiling (backend reserves 3x).
  const MAX_CONCURRENT_REQUESTS = 2;
  const queue = []; let active = 0, scheduledCharacters = 0;
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
    const key = language + ":" + source;
    if (!cache.has(key)) {
      if (cache.size >= MAX_UNIQUE_REQUESTS || scheduledCharacters + [...source].length > MAX_SOURCE_CHARACTERS) return null;
      scheduledCharacters += [...source].length;
      cache.set(key, schedule(() => fetch(API, {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ contentId: "auto", sourceText: source, sourceLanguage: "en", targetLanguage: language })
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
    if (node.parentElement?.closest('[lang]:not([lang="en"]), [lang="fr"]')) return; // Existing French passages must remain French.
    originals.set(node, source); pending.add(node);
    try {
      const value = await translate(source);
      if (value && node.isConnected && node.textContent === source) node.textContent = value;
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
