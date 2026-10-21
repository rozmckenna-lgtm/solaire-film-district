// Supabase Edge Function: translate-website
// Deploy with JWT verification OFF (public website); keep credentials ONLY in Edge secrets.
// Required secrets: SOLAIRE_GOOGLE_TRANSLATION_API_KEY, SOLAIRE_TRANSLATION_SUPABASE_SECRET.
// Calls existing RPCs read_translation_cache, reserve_translation_budget, write_translation_cache.
const PROJECT = "titeccsfyanjqmzofjrr";
const ORIGIN = "https://solairefilmdistrict.fr";
const HEADERS = { "access-control-allow-origin": ORIGIN, "access-control-allow-methods": "POST,OPTIONS", "access-control-allow-headers": "content-type", "vary": "Origin", "cache-control": "no-store" };
function respond(body: unknown, status = 200) { return new Response(JSON.stringify(body), { status, headers: { ...HEADERS, "content-type": "application/json" } }); }
async function rpc(secret: string, name: string, data: Record<string, unknown>) {
  const res = await fetch("https://" + PROJECT + ".supabase.co/rest/v1/rpc/" + name, {
    method: "POST", headers: { apikey: secret, "content-type": "application/json" },
    body: JSON.stringify(data), signal: AbortSignal.timeout(7000)
  });
  if (!res.ok) throw Error("rpc-" + res.status);
  return res.json();
}
Deno.serve(async req => {
  const origin = req.headers.get("origin");
  if (origin !== ORIGIN) return respond({ status: "unavailable" }, 403);
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: HEADERS });
  if (req.method !== "POST") return respond({ status: "unavailable" }, 405);
  let body: Record<string, unknown>;
  try { body = await req.json(); } catch { return respond({ status: "unavailable" }, 400); }
  const { contentId, sourceText, sourceLanguage, targetLanguage } = body;
  if (contentId !== "auto" || sourceLanguage !== "en" || typeof sourceText !== "string" ||
      sourceText.trim().length < 2 || [...sourceText].length > 800 ||
      typeof targetLanguage !== "string" || !/^[a-z]{2,3}$/.test(targetLanguage))
    return respond({ status: "unavailable" }, 400);
  const secret = Deno.env.get("SOLAIRE_TRANSLATION_SUPABASE_SECRET");
  const google = Deno.env.get("SOLAIRE_GOOGLE_TRANSLATION_API_KEY");
  if (!secret || !google) return respond({ status: "unavailable", reason: "credentials-missing" }, 503);
  try {
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(sourceText))))
      .map(x => x.toString(16).padStart(2, "0")).join("");
    const cacheKey = "auto:en:" + targetLanguage + ":general-v3:" + digest;
    const cached = await rpc(secret, "read_translation_cache", { p_cache_key: cacheKey });
    if (typeof cached === "string") return respond({ status: "cached", text: cached });
    const today = new Date().toISOString().slice(0, 10);
    const allowed = await rpc(secret, "reserve_translation_budget", {
      p_day: "day:" + today, p_month: "month:" + today.slice(0, 7), p_chars: [...sourceText].length * 3
    });
    if (allowed !== true && allowed?.allowed !== true) return respond({ status: "unavailable", reason: "budget-limit" }, 503);
    const result = await fetch("https://translation.googleapis.com/language/translate/v2", {
      method: "POST", headers: { "content-type": "application/json", "x-goog-api-key": google },
      body: JSON.stringify({ q: sourceText, source: "en", target: targetLanguage, format: "text" }),
      signal: AbortSignal.timeout(7000)
    });
    if (!result.ok) return respond({ status: "unavailable", reason: "provider-error" }, 503);
    const translated = (await result.json())?.data?.translations?.[0]?.translatedText;
    if (typeof translated !== "string" || !translated.trim()) return respond({ status: "unavailable" }, 503);
    await rpc(secret, "write_translation_cache", {
      p_cache_key: cacheKey, p_translated_text: translated, p_article_slug: "auto",
      p_source_digest: digest, p_target_language: targetLanguage
    });
    return respond({ status: "translated", text: translated });
  } catch { return respond({ status: "unavailable", reason: "backend-unavailable" }, 503); }
});
