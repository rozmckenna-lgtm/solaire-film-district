# Solaire Film District — launch checklist (21 October 2026)

## Launch rule
Do not change OVH DNS until the GitHub Pages website has passed the checks below. Gamma remains the public website.

## Completed
- Main pages: home, PitchUp, creators, decision-makers, Letter of Intent, Creator Centre.
- Five original English articles migrated; legacy French duplicate addresses redirect to originals.
- Automatic browser-language translation script installed on main pages and articles.
- Both public forms configured for Formspree endpoint `xwvkjpaz` and redirect to `thank-you.html`.
- Sitemap and robots.txt present.

## Four Gamma resources to migrate
The connected Gamma reader returns an unrelated PitchUp Package Template for these URLs. All four *correctly named PDF exports* were completed on 21 October 2026, but the export links have not been downloaded to the working environment or committed to GitHub. The links are temporary; re-export if expired.

1. Story Diagnostic — https://gamma.app/docs/STORY-DIAGNOSTIC-um5tnjskgipr3ei — PDF export ID `XTgv7R1LD7mty10v2I8UY`
2. Before You Pitch — https://gamma.app/docs/Before-You-Pitch-9ovpdiqxvtzg6vp — PDF export ID `VoxPiCoJLXuZcBtfHpa1P`
3. PitchUp Readiness Scorecard — https://gamma.app/docs/PitchUp-Readiness-Scorecard-o6kwtxtfpwma1k4 — PDF export ID `erZ9xMEUZVAYyltAKZjHa`
4. Materials for PitchUp Package — https://gamma.app/docs/Materials-for-PitchUp-Package-8dp7yrgjfi526lm — PDF export ID `AgkMWzfo-hXvzRHntJcFC`

Do not substitute invented or incomplete text for these documents. Preserve source content and link native versions from `creator-centre.html`.

## Required verification before cutover
- Confirm GitHub Pages preview loads all navigation, logos, images, and five article pages.
- Confirm translation actually works in a non-English browser, without a language picker or broken bilingual sections. Avoid paid translation tests without approval.
- Confirm a real submission from each Formspree form reaches its destination and confirmation page (requires an approved test).
- Confirm canonical links, sitemap, robots, and responsive mobile navigation.
- Decide whether the four specialist documents must be native before cutover; do not silently drop them.

## OVH cutover — not yet performed
Apex A records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
`www` CNAME: `rozmckenna-lgtm.github.io.`
Remove Gamma A/CNAME records only when ready. Preserve all OVH MX, SPF, DKIM, SRV, NS and verification records. Check any existing OVH root redirect before switching. Do not alter the .com domain.
