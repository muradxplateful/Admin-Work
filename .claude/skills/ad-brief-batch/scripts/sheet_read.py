#!/usr/bin/env python3
"""Read a range of the Naming Convention Builder straight from the Sheets API.

    sheet_read.py "'Ad Glossary'!D8:AN110" OUT.json [--sheet SHEET_ID]

Works in cloud sessions where the agent proxy injects Google credentials for
*.googleapis.com (no key needed). The output has the same shape as the Sheets
connector's get_values result, so names.py accepts either. If this fails (403, no
proxy), call the Google Sheets get_values tool with the same range and save the
result to OUT.json instead.
"""
import json
import os
import subprocess
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "config.json")))


def main():
    args = sys.argv[1:]
    sheet = CFG["sheet"]["builder_id"]
    if "--sheet" in args:
        i = args.index("--sheet")
        sheet = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        raise SystemExit(__doc__)
    rng, out = args
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet}/values/{urllib.parse.quote(rng)}"
    res = subprocess.run(["curl", "-sS", "--fail-with-body", url, "-H", "Authorization: Bearer proxy-injected"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise SystemExit(f"Sheets read failed ({res.returncode}): {res.stdout[:300]} {res.stderr[:300]}")
    data = json.loads(res.stdout)
    json.dump(data, open(out, "w"), ensure_ascii=False)
    print(f"{data.get('range')}: {len(data.get('values', []))} rows -> {out}")


if __name__ == "__main__":
    main()
