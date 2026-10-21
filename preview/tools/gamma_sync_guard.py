#!/usr/bin/env python3
"""Fail-closed Gamma source validation. Dry-run only: never changes website HTML."""
import argparse
import json
import re
from pathlib import Path
from convert_gamma_article import convert

EXPECTED = {
    "does-a-story-have-to-be-fast.html": "Does a Story Have to Be Fast to Be Compelling?",
    "realistic-film-budget.html": "How Do You Create a Realistic Film Budget? | Solaire PitchUp Creator Centre",
}

def validate(manifest, source_dir, output_dir):
    if manifest.get("syncEnabled") is not False:
        raise ValueError("Dry-run guard requires syncEnabled=false")
    source_dir, output_dir = Path(source_dir), Path(output_dir)
    results = []
    for entry in manifest["articles"]:
        name = entry["localPath"]
        if name not in EXPECTED or not entry.get("verifiedCanonical"):
            results.append({"article": name, "status": "SKIPPED_UNVERIFIED"})
            continue
        if not re.fullmatch(r"[a-z0-9-]+\.html", name):
            raise ValueError("Unsafe article path")
        source = source_dir / (entry["gammaId"] + ".txt")
        if not source.is_file():
            results.append({"article": name, "status": "MISSING_AUTHENTICATED_EXPORT"})
            continue
        try:
            fragment = convert(source.read_text(encoding="utf-8"), EXPECTED[name])
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / name
            if target.exists():
                raise ValueError("Refusing overwrite of prior dry-run artifact")
            target.write_text(fragment, encoding="utf-8")
            results.append({"article": name, "status": "DRY_RUN_VALIDATED", "bytes": len(fragment.encode())})
        except (ValueError, UnicodeError) as exc:
            results.append({"article": name, "status": "REJECTED", "reason": str(exc)})
    return results

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest", default="preview/gamma-english-sources.json")
    parser.add_argument("--source-dir", required=True, help="Directory of authenticated Gamma read responses saved as <gammaId>.txt")
    parser.add_argument("--output-dir", required=True, help="New empty dry-run destination, never live website")
    args=parser.parse_args()
    report=validate(json.loads(Path(args.manifest).read_text()), args.source_dir, args.output_dir)
    print(json.dumps(report, indent=2))
    if any(x["status"]=="REJECTED" for x in report):
        raise SystemExit(1)
if __name__=="__main__": main()
