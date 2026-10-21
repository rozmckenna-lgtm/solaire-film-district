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
