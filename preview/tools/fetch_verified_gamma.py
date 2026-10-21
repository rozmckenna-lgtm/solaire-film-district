#!/usr/bin/env python3
"""Retrieve verified English Gamma documents for guarded staging conversion.

No site changes; requires GAMMA_API_KEY in the environment. Never log the key.
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

API = "https://public-api.gamma.app/v1.0/gammas/"
ALLOW = {"does-a-story-have-to-be-fast.html", "realistic-film-budget.html"}

def retrieve(manifest_path, output):
    key = os.environ.get("GAMMA_API_KEY")
    if not key:
        raise RuntimeError("GAMMA_API_KEY unavailable: no remote fetch attempted")
    manifest = json.loads(pathlib.Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("syncEnabled") is not False:
        raise RuntimeError("Refusing fetch: staging review manifest must stay disabled")
    targets = [x for x in manifest["articles"] if x.get("verifiedCanonical") and x["localPath"] in ALLOW]
    if len(targets) != 2:
        raise RuntimeError("Expected exactly two verified English source mappings")
    output = pathlib.Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for entry in targets:
        identifier = entry["gammaId"]
        if not identifier.isalnum() or (output / (identifier + ".txt")).exists():
            raise RuntimeError("Unsafe identifier or refusing overwrite")
        request = urllib.request.Request(API + identifier, headers={"X-API-KEY": key, "Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status != 200:
                raise RuntimeError("Gamma did not return HTTP 200")
            data = json.load(response)
        # The converter accepts the Gamma authenticated document text, not arbitrary JSON.
        # Refuse unknown API shapes rather than fabricate an export.
        if not isinstance(data, dict) or not isinstance(data.get("content"), str):
            raise RuntimeError("Gamma response content shape not verified; no files published")
        if entry["localPath"] == "does-a-story-have-to-be-fast.html" and "Does a Story Have to Be Fast to Be Compelling?" not in data["content"]:
            raise RuntimeError("English article identity mismatch")
        if entry["localPath"] == "realistic-film-budget.html" and "How Do You Create a Realistic Film Budget?" not in data["content"]:
            raise RuntimeError("English article identity mismatch")
        (output / (identifier + ".txt")).write_text(data["content"], encoding="utf-8")
        print("Authenticated English Gamma content retrieved for " + entry["localPath"])

if __name__ == "__main__":
    try:
        retrieve("preview/gamma-english-sources.json", sys.argv[1] if len(sys.argv) > 1 else "/tmp/solaire-gamma-fresh")
    except (RuntimeError, urllib.error.URLError, ValueError) as exc:
        print("STOP: " + str(exc), file=sys.stderr)
        sys.exit(1)
