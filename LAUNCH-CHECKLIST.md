# Solaire Film District — launch checklist (21 October 2026)

## Launch rule
Do not change OVH DNS until the GitHub Pages website has passed the checks below. Gamma remains the public website.

## Completed
- Main pages: home, PitchUp, creators, decision-makers, Letter of Intent, Creator Centre.
- Five original English articles migrated; legacy French duplicate addresses redirect to originals.
- Automatic browser-language translation script installed on main pages and articles.
- Both public forms configured for Formspree endpoint `xwvkjpaz` and redirect to `thank-you.html`.
- Sitemap and robots.txt present.

## Creator Centre PDFs — completed
All five PDFs are committed to GitHub and linked directly from `creator-centre.html`:
- Story Diagnostic — `STORY-DIAGNOSTIC-4.pdf`
- Before You Pitch — `Before-You-Pitch-6.pdf` (commit `76c4663`)
- PitchUp Readiness Scorecard — `PitchUp-Readiness-Scorecard-4.pdf`
- Materials Preparation Guide — `Materials-for-PitchUp-Package-6.pdf`
- Film Finance — `FILM-FINANCE-5.pdf`

## Required verification before cutover
- Confirm GitHub Pages preview loads all navigation, logos, images, and five article pages.
- Confirm translation actually works in a non-English browser, without a language picker or broken bilingual sections. Avoid paid translation tests without approval.
- Confirm a real submission from each Formspree form reaches its destination and confirmation page (requires an approved test).
- Confirm canonical links, sitemap, robots, and responsive mobile navigation.
- Confirm all five PDF links open from the GitHub Pages preview (uploads and HTML links verified in repository).

## OVH cutover — not yet performed
Apex A records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
`www` CNAME: `rozmckenna-lgtm.github.io.`
Remove Gamma A/CNAME records only when ready. Preserve all OVH MX, SPF, DKIM, SRV, NS and verification records. Check any existing OVH root redirect before switching. Do not alter the .com domain.

## Standing content and translation rule (21 October 2026)
- Keep exactly one maintained English original for each website page, article and document. Other languages are presented through automatic browser-language translation, not separately maintained French copies.
- Do not create French duplicates or spend further time deleting legacy French article addresses. The existing `*-fr.html` files are small redirects to English originals, not duplicate content; retain them to protect old links.
- Do not initiate a separate French-content cleanup task. Continue the website completion critical path. PDF translation requires separate functionality and must not be assumed to work from webpage translation.

## Gamma source reconciliation — 21 October 2026
- Authenticated Gamma reads of three previously proposed article IDs (`1iez2py11pb8yrl`, `jb54fepsfow64in`, `5zupllwsm8jzxw5`) returned the unrelated document **COMMENT FINANCER MON FILM ?**. These IDs are blocked in `preview/gamma-english-sources.json`; never use them for article updates.
- Two other source records have matching English titles. Automatic Gamma sync remains disabled pending verified canonical sources and authenticated scheduled retrieval. No original website articles were changed.
- Next: locate the correct three original English Gamma documents, then implement a guarded update process with validation and rollback before enabling automation.

## English Gamma discovery — 21 October 2026
- Gamma full-text search identified all five English article documents, including three with multiple English editions. The earlier read_gamma mismatch must not be interpreted as evidence that those English articles are French.
- Source registry corrected in commit `a1eec8746b820b609f79108609c8af79cf24ed13`. Automatic sync remains disabled until canonical editions, scheduled authentication and safe updates are confirmed.
- Five converter safety tests executed locally and passed. This does not verify end-to-end sync.

## Cinematic preview static integration audit — 21 October 2026
- Inspected all five HTML files in `preview/` against current repository root and preview directories. Every relative `href` and `src` reference in those five files resolves to a repository entry; this is source-level verification only, not HTTP or browser testing.
- All four interior preview pages have no `lang="fr"` blocks or the sampled French duplicate markers. Industry-access form English-only label correction remains committed.
- Both preview forms retain the existing Formspree endpoint. Neither form has been submitted in a browser; no delivery claim is made.
- Attempted to open the GitHub Pages cinematic preview in a web reader; it was inaccessible there. Live rendering, image availability, desktop/mobile overflow, and translation are still unverified. Next critical task is accessible rendered staging preview and browser acceptance tests.
- Preserve rejected root homepage, live DNS and email. Do not resume Gamma automation ahead of preview functionality verification.

## Gamma authenticated read mismatch confirmed across editions — 21 October 2026
- Re-tested `read_gamma` for the three latest matching English originals: `1iez2py11pb8yrl`, `jb54fepsfow64in`, `5zupllwsm8jzxw5`. All returned the unrelated `COMMENT FINANCER MON FILM ?` content despite Gamma full-text search identifying the requested English documents.
- Tested alternate older English editions `cy8firr58fbaolp`, `t9iiyx88ybm1ae3`, `g78aa2lk8b6ip4v`; all returned unrelated `Catalogue de projets` content. Repeating `read_gamma` or switching editions is not a valid workaround.
- Verified one different English Gamma original `g_8sm4qycom0rpyuc` reads with the correct title. This indicates the issue is selective, not proof that all Gamma content is inaccessible.
- Automatic updates must remain disabled; no source content has been overwritten. Next action is to find a reliable authenticated retrieval route that returns document-specific content before building unattended sync.
