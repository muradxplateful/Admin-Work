# Batch doc format

Google Doc version: "2026-11-10 - Brief - Batch Intake Template" in Murad Concepts
(https://docs.google.com/document/d/1KZG__sWIwuzWzIXwH_BRTeMDXA5SQgd6QANeWYXcOXA/edit). Make a copy per batch.

One Google Doc per batch, one tab per concept (or one H1 section per concept). Put this
header at the top of each concept, then the reference, hooks and body as usual.

```
FORMAT: Song | VO/B-roll | Cinematic
EDITOR: Azlaan
FB PAGE: FamilyKitchenGuide
FUNNEL: BOF
LAUNCH: 2026-11-09
CONCEPT NAME: (optional, CamelCase; the skill suggests one if empty)
NARRATOR: (optional, for example female, 40s)
NOTES: (optional, anything the editor must know)

REFERENCE: <link>

HOOKS:
Hook 1: ...
Hook 2: ...

BODY:
...
```

Rules the skill applies to the header:
- EDITOR must be a name in `scripts/config.json` editors (Azlaan, Kamran, Muhammad Haris)
  or a ClickUp member; the skill maps it to the right ClickUp user and glossary spelling.
- FB PAGE and FUNNEL must match the glossary spelling.
- LAUNCH is a date (YYYY-MM-DD or "November 9").
- If a header line is missing, the skill asks once for everything that is missing,
  then carries on.
