#!/usr/bin/env python3
"""Turn a concept spec into Google Docs batchUpdate requests, and verify the result.

The brief doc is a copy of the 3-tab template (Brief, Script, Editor Brief). Each tab
is fully rewritten from the spec. Indexes are computed here, never by hand.

Spec lines (one string per paragraph, in spec["tabs"][<tab title>]):
    "H1 text"   Heading 1          "H2 text"  Heading 2         "H3 text"  Heading 3
    "P text"    body paragraph     "B text"   bullet item       "N text"   numbered item
Inline: **bold**. URLs are linked automatically. A newline inside a line becomes a
soft line break (used for rhyming couplets in the Script tab).

Usage:
    doc_requests.py build  --spec SPEC.json --doc READ_DOC.json --tab ALL > reqs.json
        (or --tab "Brief" for one tab). Tabs are separate index spaces, so all three
        tabs of a fresh copy can go in one update_doc call. The output is the full
        update_doc arguments: documentId, requests, writeControl.
    doc_requests.py verify --spec SPEC.json --doc READ_DOC.json

READ_DOC.json is the saved result of the Docs read_doc call (either the raw tool
output with a "content" key or the document itself).
"""
import argparse
import json
import re
import sys

URL_RE = re.compile(r"https?://[^\s<>\"]+")
STYLE = {"H1": "HEADING_1", "H2": "HEADING_2", "H3": "HEADING_3"}
KINDS = {"H1", "H2", "H3", "P", "B", "N"}
DASHES = "\u2013\u2014"


def u16(s):
    return len(s.encode("utf-16-le")) // 2


def load_doc(path):
    d = json.load(open(path))
    return d.get("content", d)


def tab_map(doc):
    out = {}

    def walk(tabs):
        for t in tabs:
            out[t["tabProperties"]["title"].strip()] = t
            walk(t.get("childTabs", []))

    walk(doc.get("tabs", []))
    return out


def tab_text(tab):
    txt = ""
    for el in tab["documentTab"]["body"]["content"]:
        for e in el.get("paragraph", {}).get("elements", []):
            txt += e.get("textRun", {}).get("content", "")
    return txt


def layout(lines):
    """Return (text, paragraphs, bold ranges, links) with indexes starting at 1."""
    parts, paras, bolds, links = [], [], [], []
    pos = 1
    for raw in lines:
        kind, _, body = raw.partition(" ")
        if kind not in KINDS:
            raise SystemExit(f"Unknown line kind {kind!r} in: {raw[:60]}")
        body = body.replace("\r", "").replace("\n", "\u000b")
        plain, acc = "", ""
        for i, chunk in enumerate(body.split("**")):
            if i % 2:
                bolds.append((pos + u16(acc), pos + u16(acc) + u16(chunk)))
            acc += chunk
        plain = acc
        for m in URL_RE.finditer(plain):
            url = m.group(0).rstrip(".,);:")
            s = pos + u16(plain[: m.start()])
            links.append((s, s + u16(url), url))
        line = plain + "\n"
        paras.append((kind, pos, pos + u16(line)))
        parts.append(line)
        pos += u16(line)
    return "".join(parts), paras, bolds, links


def build(spec, doc, tab_title):
    tabs = tab_map(doc)
    if tab_title not in tabs:
        raise SystemExit(f"Tab {tab_title!r} not in doc. Tabs: {list(tabs)}")
    tab = tabs[tab_title]
    tid = tab["tabProperties"]["tabId"]
    old_end = tab["documentTab"]["body"]["content"][-1]["endIndex"]
    text, paras, bolds, links = layout(spec["tabs"][tab_title])
    end = 1 + u16(text)
    rng = lambda s, e: {"startIndex": s, "endIndex": e, "tabId": tid}
    reqs = []
    if old_end - 1 > 1:
        reqs.append({"deleteContentRange": {"range": rng(1, old_end - 1)}})
    reqs.append({"insertText": {"location": {"index": 1, "tabId": tid}, "text": text}})
    reqs.append({"updateParagraphStyle": {"range": rng(1, end), "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"}, "fields": "namedStyleType"}})
    reqs.append({"deleteParagraphBullets": {"range": rng(1, end)}})
    reqs.append({"updateTextStyle": {"range": rng(1, end), "textStyle": {"bold": False, "italic": False}, "fields": "bold,italic,link"}})
    for kind, s, e in paras:
        if kind in STYLE:
            reqs.append({"updateParagraphStyle": {"range": rng(s, e), "paragraphStyle": {"namedStyleType": STYLE[kind]}, "fields": "namedStyleType"}})
    for want, preset in (("B", "BULLET_DISC_CIRCLE_SQUARE"), ("N", "NUMBERED_DECIMAL_ALPHA_ROMAN")):
        run = None
        for kind, s, e in paras + [("END", 0, 0)]:
            if kind == want:
                run = (run[0], e) if run else (s, e)
            elif run:
                reqs.append({"createParagraphBullets": {"range": rng(*run), "bulletPreset": preset}})
                run = None
    for s, e in bolds:
        if e > s:
            reqs.append({"updateTextStyle": {"range": rng(s, e), "textStyle": {"bold": True}, "fields": "bold"}})
    for s, e, url in links:
        reqs.append({"updateTextStyle": {"range": rng(s, e), "textStyle": {"link": {"url": url}}, "fields": "link"}})
    return {"tabId": tid, "requests": reqs}


def verify(spec, doc):
    tabs = tab_map(doc)
    ok = True
    for title, lines in spec["tabs"].items():
        if title not in tabs:
            print(f"FAIL {title}: tab missing")
            ok = False
            continue
        want, *_ = layout(lines)
        have = tab_text(tabs[title])
        if not have.startswith(want):
            ok = False
            i = next((k for k, (a, b) in enumerate(zip(want, have)) if a != b), min(len(want), len(have)))
            print(f"FAIL {title}: text differs at char {i}: want {want[i:i+40]!r} have {have[i:i+40]!r}")
        else:
            print(f"OK   {title}: text matches ({len(want)} chars)")
        if any(c in have for c in DASHES):
            ok = False
            print(f"FAIL {title}: contains an em or en dash")
    print("ALL OK" if ok else "PROBLEMS FOUND")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "verify"])
    ap.add_argument("--spec", required=True)
    ap.add_argument("--doc", required=True)
    ap.add_argument("--tab")
    a = ap.parse_args()
    spec, doc = json.load(open(a.spec)), load_doc(a.doc)
    if a.cmd == "build":
        if not a.tab:
            raise SystemExit("--tab is required for build (a tab title, or ALL)")
        titles = list(spec["tabs"]) if a.tab == "ALL" else [a.tab]
        reqs = []
        for t in titles:
            reqs += build(spec, doc, t)["requests"]
        out = {"documentId": doc.get("documentId"), "requests": reqs,
               "writeControl": {"requiredRevisionId": doc.get("revisionId")}}
        json.dump(out, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    else:
        sys.exit(0 if verify(spec, doc) else 1)


if __name__ == "__main__":
    main()
