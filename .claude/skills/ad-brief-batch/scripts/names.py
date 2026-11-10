#!/usr/bin/env python3
"""Plan ad names, AIDs, checks and ClickUp payloads for a batch of concepts.

Commands
    names.py plan  --concepts C1.json [C2.json ...] --glossary G.json --funnels F.json
                   --builder B.json [--run-date YYYY-MM-DD] --out PLAN.json
        Validates every concept, claims a block of free AIDs from the builder read,
        writes PLAN.json and prints the review table for the approval step.
        Exit code 1 when any check fails (nothing should be published then).

    names.py paste --plan PLAN.json --task-urls URLS.json
        Prints the 2D values array for the paste sheet (header + one row per hook),
        with the ClickUp task link in column A. URLS.json maps concept -> task URL.

Inputs
    C*.json   one concept file (see templates/concept.example.json)
    G.json    raw Sheets get_values result for config.sheet.glossary_range
    F.json    raw Sheets get_values result for config.sheet.funnel_range
    B.json    raw Sheets get_values result for '<builder tab>'!B<row>:C<row+N>
              (column B = prefilled AIDs, column C = Product; empty C = free row)
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "config.json")))
DASHES = "\u2013\u2014"

# Builder columns B..U after the link in A. Order matters: TEXTJOIN joins B:U.
COLS = ["aid", "product", "week", "funnel", "concept", "version", "hook", "ad_type", "format",
        "persona", "pain", "story", "mech", "actor", "editor", "itnn", "duration", "geo", "fb_page", "descriptor"]
HEADER = ["ClickUp Task Link", "Unique AD ID", "Product", "AD Week (Y+WNumber)", "Funnel ", "Concept Name",
          "Concept Version", "Hook Number", "AD Type", "AD Format", "Persona", "Customer Pain Point ", "Story Type",
          "Mechanisam Lenght", "Actor", "Editor", "AD IT/NN", "AD Duration (in sec)", "GEO", "FB Page Name",
          "Descriptor", "AD Name (reference; the builder fills this itself)"]
# Glossary columns (Ad Glossary sheet) that the builder validates strictly.
GLOSSARY_COLS = {"product": "D", "version": "L", "ad_type": "P", "format": "T", "persona": "V", "pain": "X",
                 "story": "Z", "mech": "AB", "editor": "AF", "itnn": "AH", "duration": "AJ", "geo": "AL", "fb_page": "AN"}


def col_index(col):
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    return n


def load_values(path):
    d = json.load(open(path))
    return d.get("range", ""), d.get("values", [])


def glossary(gpath, fpath):
    rng, vals = load_values(gpath)
    start_col = re.search(r"!([A-Z]+)\d+", rng).group(1)
    base = col_index(start_col)
    allowed = {}
    for key, col in GLOSSARY_COLS.items():
        i = col_index(col) - base
        allowed[key] = {r[i] for r in vals if len(r) > i and r[i] != ""}
    _, fvals = load_values(fpath)
    allowed["funnel"] = {r[0] for r in fvals if r and r[0]}
    return allowed


def free_block(bpath, count):
    rng, vals = load_values(bpath)
    row0 = int(re.search(r"!B(\d+)", rng).group(1))
    run_start, run_len = None, 0
    for i, r in enumerate(vals):
        empty = len(r) < 2 or r[1] == ""
        if empty and len(r) >= 1 and r[0]:
            if run_start is None:
                run_start = i
            run_len += 1
            if run_len == count:
                aids = [vals[j][0] for j in range(run_start, run_start + count)]
                return row0 + run_start, aids
        else:
            run_start, run_len = None, 0
    raise SystemExit(f"No block of {count} free rows in {rng}. Read further down the builder.")


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\u000b", " ")).strip().lower()


def tab_text(c, title):
    return "\n".join(c.get("tabs", {}).get(title, []))


def check_concept(c, allowed, run_week, errors, warnings):
    name = c["concept"]
    hooks = c["hooks"]
    if not re.fullmatch(r"[A-Za-z0-9]+", name):
        errors.append(f"{name}: concept name must be one CamelCase word (letters and digits only)")
    seen = {}
    for i, h in enumerate(hooks, 1):
        k = norm(h)
        if k in seen:
            errors.append(f"{name}: Hook {i} is the same as Hook {seen[k]}")
        seen.setdefault(k, i)
    week = c.get("week") or run_week
    if week != run_week:
        warnings.append(f"{name}: week {week} differs from this run's week {run_week}")
    n = dict(c["naming"])
    n.update(product=c["product"], funnel=c["funnel"], fb_page=c["fb_page"])
    ed = CFG["editors"].get(c["editor"])
    n["editor"] = ed["glossary"] if ed else c.get("editor_glossary", c["editor"])
    for key in list(GLOSSARY_COLS) + ["funnel"]:
        v = n.get(key, "")
        if v not in allowed.get(key, set()):
            close = [a for a in allowed.get(key, set()) if a.strip().lower() == str(v).strip().lower()]
            if len(close) == 1:
                n[key] = close[0]
                warnings.append(f"{name}: {key} {v!r} adjusted to the glossary spelling {close[0]!r}")
            else:
                errors.append(f"{name}: {key} value {v!r} is not in the glossary")
    script = norm(tab_text(c, "Script"))
    if c.get("tabs"):
        for i, h in enumerate(hooks, 1):
            if norm(h) not in script:
                errors.append(f"{name}: Hook {i} is not word for word in the Script tab")
        for para in c.get("source_body", []):
            if norm(para) and norm(para) not in script:
                errors.append(f"{name}: body line not word for word in Script tab: {para[:60]!r}")
        alltext = "\n".join(tab_text(c, t) for t in c["tabs"])
        if any(ch in alltext for ch in DASHES):
            errors.append(f"{name}: an em or en dash is in the brief text")
    return n, week


def clickup_payload(c, names, doc_url):
    cu, f = CFG["clickup"], CFG["clickup"]["fields"]
    ed = CFG["editors"].get(c["editor"], {})
    editor_id = ed.get("clickup_id") or c.get("editor_clickup_id")
    fmt = cu["naming_format_to_clickup_format"].get(c["naming"]["format"], cu["naming_format_to_clickup_format"]["_default"])
    esc = lambda s: s.replace("_", "\\_")
    lines = [
        "### General Brief Guidelines:", " Dimensions Needed for Video Ads", "*   16x9", "*   9x16", "*   4x5", "",
        "Brief and Script doc:", f"[{esc(doc_url)}]({doc_url})", "",
        " Quality Checks for Video Editors:", "- [ ] Safe zones", "- [ ] Caption placement",
        "- [ ] Content fits in aspect ratios", "- [ ] Clip relevance to the script", "- [ ] Clip quality",
        "- [ ] Natural Voiceover", "", "**Deliverables**", "*   Frame Link:",
        f"*   Headlines and copy: [{CFG['drive']['headlines_doc_url']}]({CFG['drive']['headlines_doc_url']})",
        "*   Ad Names:", "",
    ] + [esc(x) for x in names]
    fields = [
        (f["video_editor"], json.dumps({"add": [editor_id]})),
        (f["owner"], json.dumps({"add": [cu["owner_id"]]})),
        (f["fb_page"], c["fb_page"]),
        (f["headline"], c.get("headline", "-")),
        (f["launch_date"], c["launch_date"]),
        (f["ad_type"], cu["ad_type_options"][c["naming"].get("ad_type", "VID")]),
        (f["meta"], "true"),
        (f["awareness"], cu["awareness_options"][c.get("awareness", "product")]),
        (f["concept_type"], cu["concept_type_options"][c.get("concept_type", "new")]),
        (f["format"], cu["format_options"][fmt]),
        (f["angle"], c["naming"]["pain"]),
        (f["persona"], c.get("persona_label", c["naming"]["persona"])),
    ]
    if c["product"] in cu["product_line_options"]:
        fields.append((f["product_line"], json.dumps([cu["product_line_options"][c["product"]]])))
    return {
        "list_id": cu["list_id"],
        "name": c.get("task_name") or f"PF - {c['product']} - W{c['_week'][-2:]} - {c['concept']}",
        "status": cu["default_status"],
        "assignees": [editor_id, cu["owner_id"]],
        "markdown_description": "\n".join(lines),
        "custom_fields": [{"id": i, "value": v} for i, v in fields],
    }


def plan(a):
    allowed = glossary(a.glossary, a.funnels)
    run_date = dt.date.fromisoformat(a.run_date) if a.run_date else dt.date.today()
    iy, iw, _ = run_date.isocalendar()
    run_week = f"Y{iy % 100:02d}W{iw:02d}"
    concepts = [json.load(open(p)) for p in a.concepts]
    errors, warnings = [], []
    videos = lambda c: len(c["hooks"]) + int(bool(c.get("no_hook_variation")))
    total = sum(videos(c) for c in concepts)
    first_row, aids = free_block(a.builder, total)
    offers = {}
    out = {"run_date": run_date.isoformat(), "run_week": run_week, "first_row": first_row,
           "last_row": first_row + total - 1, "concepts": []}
    k = 0
    for c in concepts:
        n, week = check_concept(c, allowed, run_week, errors, warnings)
        c["_week"] = week
        pcts = set(re.findall(r"(\d{2})% off", "\n".join(tab_text(c, t) for t in c.get("tabs", {})), re.I))
        if pcts:
            offers[c["concept"]] = pcts
        rows, names = [], []
        for h in range(1, videos(c) + 1):
            vals = dict(n, aid=aids[k], week=week, concept=c["concept"], hook=f"H{h}")
            vals.setdefault("version", "V1")
            vals.setdefault("descriptor", "")
            row = [vals.get(col, "") for col in COLS]
            full = "_".join(x for x in row if x != "")
            rows.append(row + [full])
            names.append(full)
            k += 1
        if len(names) != videos(c):
            errors.append(f"{c['concept']}: {len(names)} names for {videos(c)} videos")
        doc_url = c.get("doc_url", "DOC_URL_PENDING")
        out["concepts"].append({"concept": c["concept"], "editor": c["editor"], "doc_url": doc_url,
                                "names": names, "rows": rows, "clickup": clickup_payload(c, names, doc_url)})
    all_pcts = set().union(*offers.values()) if offers else set()
    if len(all_pcts) > 1:
        warnings.append("Offer differs between concepts: " + ", ".join(f"{k}: {'/'.join(sorted(v))}%" for k, v in offers.items()))
    if len(set(aids)) != len(aids):
        errors.append("Duplicate AIDs in the claimed block")
    out["errors"], out["warnings"] = errors, warnings
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)

    print(f"Run week {run_week}. Builder rows {first_row} to {first_row + total - 1} ({aids[0]} to {aids[-1]}).\n")
    print("| Concept | Editor | Videos | AIDs | Format | Persona | Pain | Story | Duration | Funnel | FB page |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for c, p in zip(concepts, out["concepts"]):
        r0, r1 = p["rows"][0], p["rows"][-1]
        print(f"| {c['concept']} | {c['editor']} | {videos(c)} | {r0[0]} to {r1[0]} | {r0[8]} | {r0[9]} | {r0[10]} | {r0[11]} | {r0[16]} | {r0[3]} | {r0[18]} |")
    print()
    for p in out["concepts"]:
        print(p["concept"])
        for nm in p["names"]:
            print("  " + nm)
    for w in warnings:
        print("WARNING: " + w)
    for e in errors:
        print("ERROR: " + e)
    print("\nCHECKS PASSED" if not errors else "\nCHECKS FAILED: fix the errors before publishing")
    sys.exit(1 if errors else 0)


def paste(a):
    p = json.load(open(a.plan))
    urls = json.load(open(a.task_urls))
    values = [HEADER]
    for c in p["concepts"]:
        for r in c["rows"]:
            values.append([urls.get(c["concept"], "")] + r)
    json.dump({"range": f"A1:V{len(values)}", "values": values, "paste_at": f"A{p['first_row']}"}, sys.stdout, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("plan")
    p1.add_argument("--concepts", nargs="+", required=True)
    p1.add_argument("--glossary", required=True)
    p1.add_argument("--funnels", required=True)
    p1.add_argument("--builder", required=True)
    p1.add_argument("--run-date")
    p1.add_argument("--out", required=True)
    p2 = sub.add_parser("paste")
    p2.add_argument("--plan", required=True)
    p2.add_argument("--task-urls", required=True)
    a = ap.parse_args()
    plan(a) if a.cmd == "plan" else paste(a)


if __name__ == "__main__":
    main()
