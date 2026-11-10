---
name: ad-brief-batch
description: Turn Murad's batch doc of plain ad scripts (hooks, body, reference) into finished video ad briefs, one Google Doc per concept in the 3-tab structure (Brief, Script, Editor Brief), then, after Murad approves, create the ClickUp tasks in Creative Pipeline with the ad names and make the paste sheet for the Naming Convention Builder. Use when Murad shares a batch doc link and asks to build, format or brief the ads, or runs /ad-brief-batch.
---

# Ad brief batch

Manual run, one batch at a time. Nothing goes to ClickUp or the paste sheet until
Murad approves the review summary.

Read first: `reference/brief-structure.md` (what each tab contains), `reference/naming.md`
(ad names), `scripts/config.json` (IDs). Also follow the `google-workspace` skill rules
(guard every Docs batch with the latest `revisionId`) and the Plateful Drive rules
(company files never go in My Drive). No em dashes or en dashes in anything you write.

Work in a batch folder in the scratchpad, for example `<scratchpad>/batch-2026-11-10/`.
`S` below is this skill's `scripts/` folder.

## 1. Read the batch and the intake

1. Read the batch doc with Drive `read_file_content` (`includeComments: true`). Each
   tab (or each H1 section) is one concept.
2. For each concept, take the intake header (`templates/batch-intake.md`): FORMAT,
   EDITOR, FB PAGE, FUNNEL, LAUNCH, optional CONCEPT NAME, NARRATOR, NOTES. Collect
   everything missing across the whole batch and ask **once**, in one message.
3. Note anything odd in the scripts while reading (two identical hooks, offers that
   differ between concepts, typos in the VO). Do not fix the VO; ask in the same message
   or list it in the review.

## 2. Read the naming data

```bash
python3 $S/sheet_read.py "'Ad Glossary'!D8:AN110" glossary.json
python3 $S/sheet_read.py "'AdSet Glossary'!H7:H16" funnels.json
python3 $S/sheet_read.py "'Meta Ad Name Builde'!B<last_known_free_row - 10>:C<+400>" builder.json
```

`last_known_free_row` is in `config.json`. The team fills the builder fast (about 600
rows in five days in November 2026), so if `names.py` says there is no free block,
read further down (up to row 6503, the end of the prefilled AIDs) and tell Murad if the
prefilled AIDs are running out. If `sheet_read.py` fails, use the Sheets `get_values`
tool with the same ranges and save each result to the same file name.

## 3. Write one concept file per concept

Copy `templates/concept.example.json` (a finished, tested concept: ReturnedOrderVoicemail) and fill it in `concept-<Name>.json`:

- meta: concept (CamelCase), product code, funnel, editor (a key of `editors` in
  `config.json`; add a new editor there first, with their ClickUp user ID from
  `clickup_get_workspace_members` and their Ad Glossary spelling), fb_page, launch_date,
  awareness (unaware, problem, solution, product, most), concept_type (new, iteration...),
  persona_label, no_hook_variation (true for Song ads by default).
- `naming`: glossary values for format, persona, pain, story, mech, actor, itnn,
  duration, geo, version, ad_type. Pick from `glossary.json`; never invent a value.
- `hooks` and `source_body`: copied verbatim from the batch doc (used for the
  word-for-word check).
- `tabs`: the full content of Brief, Script and Editor Brief, following
  `reference/brief-structure.md` line by line. Get beat times from `timing.py`:
  write the beats to `beats-<Name>.json` and run `python3 $S/timing.py beats-<Name>.json`.

## 4. Create the docs (drafts)

For each concept:

1. Drive `copy_file` of `drive.brief_template_doc_id` into `drive.concepts_folder_id`,
   title `YYYY-MM-DD - Brief - PF - <CODE> - W<ww> - <ConceptName>` (today's date).
2. Docs `read_doc` the copy. A large result is saved to a file; use that path. A fresh
   copy of the template is small and comes back inline: then write a minimal doc file
   with `documentId`, `revisionId` and, per tab, `tabProperties` (tabId, title) and the
   body's last `endIndex` (see `templates/doc.minimal.example.json`).
3. Build the requests and send their `documentId`, `requests` and `writeControl` to
   Docs `update_doc`. Keep each call under about 25 KB (bigger tool output gets cut
   off before you can copy it): send Brief and Script together, then read again and
   send Editor Brief on its own.
   `python3 $S/doc_requests.py build --spec concept-<Name>.json --doc <read path> --tab Brief`
   (`--tab Script`, `--tab "Editor Brief"`, or `--tab ALL` when the total is small).
   Requests for different tabs built from the same read can go in one call.
   A long tab (a cinematic Editor Brief can pass 13,000 characters) still goes over
   25 KB on its own: split it with `--lines 0:<n>` (replaces the tab with lines
   0 to n) and then, after a fresh read, `--lines <n>:` (appends the rest).
4. `read_doc` again and run `python3 $S/doc_requests.py verify --spec concept-<Name>.json --doc <read path>`.
   It must print ALL OK. Fix and resend anything that fails.
5. Put the doc link (`https://docs.google.com/document/d/<id>/edit`) in the concept
   file as `doc_url`.

## 5. Plan names and checks

```bash
python3 $S/names.py plan --concepts concept-*.json --glossary glossary.json \
  --funnels funnels.json --builder builder.json --out plan.json
```

It claims the next free block of AIDs, builds every name, the ClickUp payloads and
runs the checks: glossary spelling, unique AIDs, one name per video, duplicate hooks,
hooks and body word for word in the Script tab, dashes, week, offer consistency.
Fix every ERROR (edit the concept file, rebuild the doc tab if text changed) and run
it again until CHECKS PASSED.

## 6. Review (stop here)

Send Murad one message with:
- a link to each brief doc;
- the table `names.py` printed (concept, editor, videos, AIDs, naming values);
- every WARNING, and every open question or assumption (concept names you chose,
  editor split, narrator, claims to check).

Wait. Apply any changes he asks for (doc edits through `update_doc`, concept file
edits, then `names.py plan` again). Do not publish until he approves.

## 7. Publish (after approval)

1. Re-read `builder.json` and run `names.py plan` again, in case someone took the
   AIDs since the review. If the AIDs changed, tell Murad the new range.
2. For each concept in `plan.json`, call ClickUp `clickup_create_task` with its
   `clickup` payload (list_id, name, status, assignees, markdown_description,
   custom_fields). Save the returned task URLs to `task-urls.json`
   (`{"ConceptName": "https://app.clickup.com/t/..."}`).
3. Check one task with `clickup_get_task` (include custom_fields).
4. Paste sheet: Drive `create_file` (spreadsheet) in the concepts folder, title
   `YYYY-MM-DD - Export - Ad Names - PF - W<ww> - <short batch name>`. Run
   `python3 $S/names.py paste --plan plan.json --task-urls task-urls.json` and write
   its `values` to `Sheet1!A1` with Sheets `update_values`; rename the tab to
   `Ad Names`, bold and freeze row 1. Read row 2 back to confirm.
5. Set `sheet.last_known_free_row` in `config.json` to `plan.json` `last_row + 1`,
   and commit that change to the repo.

## 8. Final message

Short: the task links (as markdown links with the task name), the paste sheet link and
where to paste it (`paste_at` from `names.py paste`, values only, Ctrl+Shift+V), and
anything still open. Link every doc and sheet you name.

## Known limits

- The Docs connector can't rename tabs (`updateDocumentTabProperties` returns an
  internal error). That's why each brief is a copy of the template, which already has
  the right tab names.
- `replaceAllText` gives the replacement the style of the first character it replaces;
  for small edits next to a bold label, delete and insert at the exact range instead.
- The Naming Convention Builder is view-only for the cloud account; keep the paste
  sheet.
- ClickUp custom field and option IDs live in `config.json`. If a create call fails on
  a field, read the list's fields with `clickup_get_custom_fields` (list
  `901516927548`) and update the config.
