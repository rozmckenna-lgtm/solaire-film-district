#!/usr/bin/env python3
"""Prepare a reviewed staging-only article update. Never modify a published page."""
import argparse
import difflib
import html
import json
import re
from pathlib import Path

ALLOWED = {"does-a-story-have-to-be-fast.html", "realistic-film-budget.html"}

def article_body(fragment):
    m = re.fullmatch(r'\s*<article class="gamma-english-article" lang="en">\s*(.*?)\s*</article>\s*', fragment, re.S)
    if not m:
        raise ValueError("Unexpected or non-English Gamma fragment wrapper")
    return m.group(1).strip()

def prepare(name, existing, fragment):
    if name not in ALLOWED:
        raise ValueError("Article not approved for staged conversion")
    if '<html lang="en">' not in existing or '<script src="automatic-translation.js"' not in existing:
        raise ValueError("Cinematic staging structure or translation loader missing")
    match = re.search(r'(<main\b[^>]*>)(.*?)(</main>)', existing, re.S)
    if not match or existing.count("<main") != 1:
        raise ValueError("Cannot safely locate exactly one article main")
    original = match.group(2)
    new_body = article_body(fragment)
    if len(new_body) < 500 or "<h1>" not in new_body:
        raise ValueError("Missing expected article content")
    # Verify the authenticated source's opening paragraph is present in staging.
    def plain(s):
        return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
    if plain(new_body)[:140] not in plain(original):
        raise ValueError("Source opening does not match staging; refuse replacement")
    updated = existing[:match.start(2)] + new_body + existing[match.end(2):]
    if updated == existing:
        return updated, ""
    # The original pages are minified onto one line; split at structural tags so reviewers\n    # can see individual paragraph/heading changes rather than an unreadable giant line.\n    def readable_lines(markup):\n        return re.sub(r"(?=<(?:h[1-6]|p|hr|spacer|ul|ol|li|blockquote)\\b)", "\\n", markup).strip().splitlines(keepends=True)\n    diff = "".join(difflib.unified_diff(readable_lines(original), readable_lines(new_body), fromfile="staging-existing", tofile="authenticated-gamma", n=2))
    return updated, diff

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--page",required=True)
    ap.add_argument("--fragment",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--diff",required=True)
    args=ap.parse_args()
    page=Path(args.page)
    if page.name not in ALLOWED or page.parent.name != "preview":
        raise SystemExit("Refusing non-preview article or unapproved path")
    out=Path(args.out)
    diff=Path(args.diff)
    if out.exists() or diff.exists() or out.resolve()==page.resolve():
        raise SystemExit("Refusing overwrite")
    result,changes=prepare(page.name,page.read_text(encoding="utf-8"),Path(args.fragment).read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True,exist_ok=True)
    diff.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(result,encoding="utf-8")
    diff.write_text(changes,encoding="utf-8")
    print(json.dumps({"article":page.name,"staged":str(out),"diff":str(diff),"changed":bool(changes)}))
if __name__=="__main__":main()
