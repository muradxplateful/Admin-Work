#!/usr/bin/env python3
"""Work out beat timestamps from word counts.

    timing.py BEATS.json [--wps 2.7] [--hook-seconds 5]

BEATS.json is a list of {"title": "...", "text": "verbatim VO of the beat"}.
Prints each beat's start and end (the body starts after one hook) and the total.
2.7 words per second is the house pace (656 words is about 4:00).
"""
import argparse
import json
import re


def mmss(s):
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


ap = argparse.ArgumentParser()
ap.add_argument("beats")
ap.add_argument("--wps", type=float, default=2.7)
ap.add_argument("--hook-seconds", type=float, default=5)
a = ap.parse_args()
t = a.hook_seconds
total_words = 0
for i, b in enumerate(json.load(open(a.beats)), 1):
    w = len(re.findall(r"[A-Za-z0-9$%']+", b["text"]))
    total_words += w
    start, t = t, t + w / a.wps
    print(f"Beat {i}: {b['title']} ({mmss(start)} to {mmss(t)})  {w} words")
print(f"Body {total_words} words. Runtime with hook about {mmss(t)}; without hook about {mmss(t - a.hook_seconds)}.")
