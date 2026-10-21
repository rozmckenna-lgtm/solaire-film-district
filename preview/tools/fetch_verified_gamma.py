#!/usr/bin/env python3
"""Fail-closed Gamma source identity preflight; does NOT retrieve article text.

Gamma GET /v1.0/gammas/{id} provides metadata, not an authenticated
read_gamma content export. Do not treat its response as a sync source.
"""
import json
import os
import pathlib
import sys
import urllib.request
import urllib.error

API = "https://public-api.gamma.app/v1.0/gammas/"
EXPECTED = {
    "does-a-story-have-to-be-fast.html": "Does a Story Have to Be Fast to Be Compelling?",
    "realistic-film-budget.html": "How Do You Create a Realistic Film Budget?",
}

def verify(manifest_path):
    key = os.environ.get("GAMMA_API_KEY")
    if not key:
        raise RuntimeError("GAMMA_API_KEY unavailable: no remote request made")
    manifest = json.loads(pathlib.Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("syncEnabled") is not False:
        raise RuntimeError("Refusing metadata preflight while sync is enabled")
    targets = [a for a in manifest["articles"] if a.get("verifiedCanonical")]
    if len(targets) != 2 or {a["localPath"] for a in targets} != set(EXPECTED):
        raise RuntimeError("Expected exactly two verified canonical sources")
    for article in targets:
        identifier = article["gammaId"]
        if not identifier.isalnum():
            raise RuntimeError("Invalid Gamma document identifier")
        req = urllib.request.Request(API + identifier, headers={"X-API-KEY": key, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status != 200:
                raise RuntimeError("Gamma metadata request failed")
            metadata = json.load(response)
        if not isinstance(metadata, dict) or EXPECTED[article["localPath"]].casefold() not in str(metadata.get("title", "")).casefold():
            raise RuntimeError("Gamma metadata title mismatch: " + article["localPath"])
        print("PASS: metadata identity " + article["localPath"])
    print("STOP: metadata only. No article content fetched; no automatic sync or publication.")

if __name__ == "__main__":
    try:
        verify("preview/gamma-english-sources.json")
    except (RuntimeError, urllib.error.URLError, ValueError) as exc:
        print("STOP: " + str(exc), file=sys.stderr)
        sys.exit(1)
