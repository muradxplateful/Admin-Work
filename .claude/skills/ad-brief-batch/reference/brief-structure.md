# Brief structure

Every concept gets its own Google Doc, copied from the 3-tab template, with the tabs
**Brief**, **Script** and **Editor Brief**. The model brief is
`PF-BVS-W45-ToddlerMomStoryAd-4V` (config `drive.model_brief_doc_id`). Read it with
Drive `read_file_content` when in doubt about tone or depth: match it.

Spec line kinds used below: `H1`, `H2`, `H3`, `P`, `B` (bullet), `N` (numbered).
`**bold**` inline. A newline inside a line is a soft line break (couplets).

## Writing rules (apply to every tab)

- **Never change the VO.** Hooks and body go in word for word, in the Script tab and in
  the beats. Only split lines where the rhyme or the sentence breaks. Fix nothing,
  not even typos or awkward lines; list doubts under the strategist notes instead.
- **No em dashes or en dashes anywhere** (company rule). Use a comma, colon, period or
  parentheses. Hyphens inside words are fine. Strip dashes from source stage directions.
- **Don't invent claims, prices or offers.** Use the offer as written in the script. If
  something is missing, write "Not in script".
- **Name every person** who appears (lead, family, friends, extras with a role) and use
  the same names everywhere.
- **Find the turn:** the line where the narrator decides or realizes something. The
  product enables the turn; it must not make it. Flag it under "Where it is weak" if
  the product drives the turn.
- **Timing:** hooks about 5 seconds; body at 2.7 words per second. Use
  `scripts/timing.py` on the beats to get start and end times and the runtime.
- **Beats:** split the body into 6 to 9 beats at the story turns (backstory, problem,
  dilemma, evidence, realization, product, new normal, offer).

## Tab 1: Brief

```
H1 PF-<CODE>-W<ww>-<ConceptName>
P **Concept:** <short concept label> · **Product:** <product> · **Format:** <format>, about <runtime>[ plus a 40 second cutdown]
H2 Hypothesis
P <Who the avatar is, the tension or dilemma, how the ad reframes the problem, why the product becomes the way out. End: "We expect this <angle type> angle to hold viewers longer and convert better with this avatar than a <default angle> pitch.">
H2 Audience
B **Who:** <avatar, age range, buying behavior>
B **Core belief:** "<belief in their own words, ideally a script line>"
B **Core wound:** <the painful feeling>
B **Core desire:** <what they want to be true>
H2 Awareness stage
P **Target: <stage>.** <What they know, what they blame, what they don't know yet.>
P The ad moves her/him through three stages in order:
N **Problem aware (<start> to <end>):** <hooks and beats that name the problem>
N **Solution aware (<start> to <end>):** <beat that reframes the cause, with the key quote>
N **Product aware (<start> on):** <how the product arrives and what job it does>
H2 Market sophistication
P <Which claims are familiar in the category; how this ad stands out; where product claims sit.>
H2 Angle and mechanism
B **Angle:** <emotional angle and the dilemma it resolves>
B **Mechanism:** <simple cause and effect>
B **The turn:** <the decision, quoted>. The product enables it but does not make it.
H2 Objections handled
B "<objection>" <where and how it is answered>   (3 to 5 of these)
```

For a bottom-of-funnel ad (most of the deal or offer ads) the target is usually
product aware; say what they already know about the product and what pushes them now.

## Tab 2: Script

```
P **Hook 1:**
P <hook 1 verbatim>
... one pair per hook ...
P **BODY**
P <body verbatim, one sentence or couplet per paragraph; couplet lines joined with a newline>
```

For a cinematic (dialogue) ad, write each line as `P **<Speaker>:** <line>` and stage
directions as `P [Visual] <direction>`, exactly as the script gives them.

## Tab 3: Editor Brief

```
H1 PF-<CODE>-W<ww>-<ConceptName>
P W<ww> <CODE> Ads
H2 Inspo
P <reference link(s)>, or "None provided"
H2 Song            (song ads)   or   H2 Music   (all other ads)
P <style, tempo, mood; for VO ads the music bed and how loud it sits under the voice>
H2 Format
P <animation or footage style, for example Pixar style animation, AI UGC avatar + B-roll, live action>
H2 Concept overview
P <3 to 4 sentences: who, what they believe, what they realize, what changes>
B **Concept name:** <label>
B **Format:** 9:16 vertical, <VO style> over B-roll
B **Avatar:** <avatar>
B **Product:** <product description>
B **Runtime:** About <runtime> (hooks about 5 seconds)[, plus one 40 second cutdown]
B **First clear product shot:** About <time> ("<line>")
B **Core dilemma:** <option A and its cost, or option B and its cost>
B **Emotional engine:** <the promise or belief, quoted>
B **Old methods on trial:** <what failed before>
B **Tone:** <tone, plus the grade for flashback, problem and resolution>
B **Offer:** <offer from script>
B **CTA:** <CTA from script>
B **Signature motifs:** <3 to 5 recurring images>
P **The hook question for the viewer:** <the question the ad answers>
H2 Story check (cinematic guidelines)
P **One-sentence test:** A <character> is afraid of <fear>, made real by <memory or image>, at <place>; the product enters once <realization>; the turn is <decision>.
B **Dramatic question:** <yes or no question>
B **Want:** <external goal>. **Need:** <internal goal>.
B **Really about:** <real theme>, not <surface topic>.
B **The turn:** <decision, quoted>. The product only enables it.
B **Ending:** <new equilibrium, quoted>
B **Where it is weak:** <honest gaps>
H2 Character sheet
P <"One voice carries the whole ad. Everyone else appears in B-roll only." or who speaks>
H3 <Lead name> (lead, narrator, the avatar)
B **Age:** / **Backstory:** / **Look and wardrobe:** / **Personality:** / **Role:** / **Casting note:**
H3 <Each other person> (<relation>)
B **Age:** / **Look and wardrobe:** / **Role:** / **Casting note:**
H3 Supporting and non-speaking
B **Hand model:** For macro demo shots if the lead's hands aren't used.
P **Wardrobe continuity:** <which beats must match>
H2 Hooks
P Each about 5 seconds, VO over B-roll, then straight into Beat 1.[ Variation N has no hook.]
H3 Hook 1
P <hook verbatim, split at the rhyme or sentence>
P [Visual] <shot>
... one H3 per hook ...
H3 Variation <N>: No hook        (only when the concept has no_hook_variation)
P Open cold on Beat 1: "<first words of the body>..."
H2 Script (about <runtime>)
P VO is verbatim. One B-roll direction per beat; cut on every line.
H3 Beat 1: <title> (<start> to <end>)
P [Visual] <one B-roll direction>
P <verbatim VO, one sentence or couplet per paragraph>
... beats ...
P [On-screen text] <key line>        (on the turn beat and the offer beat)
P **End card:** <product> by Plateful. <offer>. <CTA>.
H2 Production notes
H3 Key shots and styling
B **<Shot pair or match cut>:** ...
B **The turn:** Beat <n> is the most important shot in the ad: ... Hold it.
B **Grade:** ...
B **Sound:** ... Drop the music for the first product moment so the product sound plays alone.
B **On-screen text:** ... Captions on every VO line, broken where the line breaks.
H3 Props
B <prop groups, then the product unit and accessories>
H3 Notes for the strategist          (only if there are open questions)
B <claims to check, voice or casting to confirm, script lines that look wrong>
```

## Format differences

| Format | Song/Music | Script tab | Beats | Defaults |
|---|---|---|---|---|
| Song (Pixar Song Ad) | H2 Song: genre, tempo (80 to 100 BPM so the VO is audible), mood | couplets with soft line breaks | 6 to 9 beats, rhyming VO | Variation N with no hook, one 40 second cutdown, CTA "Tap below" |
| VO / B-roll / AI UGC | H2 Music: bed under the VO | one sentence per paragraph | 6 to 9 beats | no cutdown unless asked |
| Cinematic (dialogue) | H2 Music: score and where it drops | speaker lines and [Visual] directions as written | scenes instead of beats: `H3 Scene N: <title> (<start> to <end>)`, dialogue lines `P **<Speaker>:** <line>` | character sheet lists every speaking role; hooks can be full cold-open scenes |

Product facts that every VacuSeal (BVS) brief can rely on, unless the script says
otherwise: compact cordless handheld sealer (about the size of a TV remote) on the
valve of Plateful reusable zip bags; no jars, bottles or liquids; the seal is shown at
real speed, never sped up; no real brand logos (no Ziploc box, no store names).
