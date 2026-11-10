# Admin-Work

Claude Code skills and helper scripts for Plateful marketing admin work.

## Ad brief batch (`/ad-brief-batch`)

Turns a batch doc of plain ad scripts into finished video ad briefs, then publishes
them to ClickUp after a review.

1. Copy the [Batch Intake Template](https://docs.google.com/document/d/1KZG__sWIwuzWzIXwH_BRTeMDXA5SQgd6QANeWYXcOXA/edit),
   one tab per concept, header filled in (format, editor, FB page, funnel, launch date).
2. In Claude Code, run `/ad-brief-batch <batch doc link>`.
3. Claude writes one Google Doc per concept (Brief, Script, Editor Brief tabs) in
   Murad Concepts, checks everything, and sends a review table with the ad names.
4. Approve or ask for changes. After approval Claude creates the ClickUp tasks in
   Creative Pipeline and a paste sheet for the Naming Convention Builder.
5. Paste the sheet's rows into the builder at the row Claude gives you (values only).

Everything lives in `.claude/skills/ad-brief-batch/`:

| Path | What it is |
|---|---|
| `SKILL.md` | The step-by-step process Claude follows |
| `reference/brief-structure.md` | What goes in each tab, per format (Song, VO/B-roll, Cinematic) |
| `reference/naming.md` | Ad naming rules |
| `scripts/config.json` | Drive, Sheet and ClickUp IDs, editors (edit here when they change) |
| `scripts/doc_requests.py` | Builds and verifies the Google Docs edits |
| `scripts/names.py` | Claims AIDs, builds ad names, ClickUp payloads, runs the checks |
| `scripts/sheet_read.py` | Reads the naming sheet directly |
| `scripts/timing.py` | Beat timestamps from word counts |
| `templates/` | Batch intake format and a finished example concept |

Add a new editor: put their name, ClickUp user ID and glossary spelling under
`editors` in `scripts/config.json` (and make sure they're in the Ad Glossary).
