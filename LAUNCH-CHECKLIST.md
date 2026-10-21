# Solaire Film District — launch checklist (21 October 2026)

## Launch rule
Do not change OVH DNS until the GitHub Pages website has passed the checks below. Gamma remains the public website.

## Completed
- Main pages: home, PitchUp, creators, decision-makers, Letter of Intent, Creator Centre.
- Five original English articles migrated; legacy French duplicate addresses redirect to originals.
- Automatic browser-language translation script installed on main pages and articles.
- Both public forms configured for Formspree endpoint `xwvkjpaz` and redirect to `thank-you.html`.
- Sitemap and robots.txt present.

## Creator Centre PDF migration status
Four original specialist documents were exported from Gamma. GitHub commit history confirms these original PDFs are uploaded and linked from `creator-centre.html`:

- Story Diagnostic — `STORY-DIAGNOSTIC-4.pdf` (commit `8180fa7`)
- PitchUp Readiness Scorecard — `PitchUp-Readiness-Scorecard-4.pdf` (commit `63a7675`)
- Materials Preparation Guide — `Materials-for-PitchUp-Package-6.pdf` (commit `6f830ee`)
- Additional Film Finance guide — `FILM-FINANCE-5.pdf` (commit `beb9b31`)

**Still missing from GitHub:** `Before-You-Pitch-6.pdf`. Its Creator Centre link still points to Gamma. The original PDF is available from the user-uploaded files; it must be uploaded through GitHub's browser interface (the connected GitHub text-file tools cannot upload PDF bytes). Once committed, update the link in `creator-centre.html`.

## Required verification before cutover
- Confirm GitHub Pages preview loads all navigation, logos, images, and five article pages.
- Confirm translation actually works in a non-English browser, without a language picker or broken bilingual sections. Avoid paid translation tests without approval.
- Confirm a real submission from each Formspree form reaches its destination and confirmation page (requires an approved test).
- Confirm canonical links, sitemap, robots, and responsive mobile navigation.
- Upload Before You Pitch PDF and replace its remaining Gamma link; confirm all five PDF links work.

## OVH cutover — not yet performed
Apex A records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
`www` CNAME: `rozmckenna-lgtm.github.io.`
Remove Gamma A/CNAME records only when ready. Preserve all OVH MX, SPF, DKIM, SRV, NS and verification records. Check any existing OVH root redirect before switching. Do not alter the .com domain.
