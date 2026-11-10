# Ad naming rules

Builder: "Naming Convention Builder for Ads 2026" (config `sheet.builder_id`), tab
`Meta Ad Name Builde`. Column A is the ClickUp task link, B the prefilled AID, C to U
the parts below, and V is `=TEXTJOIN("_",TRUE,B:U)`. The cloud account has view-only
access, so the run makes a paste sheet and Murad pastes it in.

Order (B to U):

```
AID_Product_Week_Funnel_Concept_Version_Hook_AdType_Format_Persona_PainPoint_StoryType_MechanismLength_Actor_Editor_ITNN_Duration_GEO_FBPage[_Descriptor]
AID7073_BVS_Y26W45_BOF_ReturnedOrderVoicemail_V1_H1_VID_Broll_BVSBudgetFoodStretcher_Price_Customer_Short_No_Azlaan _NN_120sec+_US_FamilyKitchenGuide
```

| Part | Source | Rule |
|---|---|---|
| AID | builder column B | One per video, consecutive, from the first block of rows where column C is empty. Never reuse one. `names.py` claims them. |
| Product | glossary | BVS, JVS, Pan, FWM, CB, CWS, Wok, TFP |
| Week | run date | `Y<yy>W<ww>` = ISO week of the day the brief is written, same for every hook (no drag-fill drift). Task name uses the same week. |
| Funnel | intake header | TOF, MOF or BOF (AdSet Glossary) |
| Concept | the skill | One CamelCase word, the same in the doc title, task name and every name |
| Version | V1 unless an iteration | |
| Hook | H1..Hn | One per video. A no-hook variation is the next number. |
| AdType | VID or IMG | |
| Format | glossary | Broll, ASMR, Pixar, AISong, AIAvatar, BrandApology, FullAI, Podcast, Yapper, ... |
| Persona | glossary | Product-prefixed, for example BVSBulkBuyer, BVSSoloHousehold |
| PainPoint | glossary | For example FoodGoesBad, LosingMoney, WasteMoney, Price |
| StoryType | glossary | For example Emotional, Educational, Customer, Banned, NegativeMarketing |
| MechanismLength | glossary | No, Short (0 to 15 s), Medium (15 to 45 s), Long (45 s+): how long the "why it works" part runs |
| Actor | free text | No unless a named creator is on camera |
| Editor | config `editors` | The glossary value, trailing space included where the glossary has one ("Azlaan ") |
| IT/NN | glossary | NN for a new concept; FOOTAGIT, HOOKIT, AVATARIT, SCRIPTIT, VEIT for iterations |
| Duration | glossary | Bucket for the longest video: 15sec+, 30sec+, 45sec+, 60sec+, 90sec+, 120sec+ |
| GEO | glossary | US |
| FBPage | intake header | Exact glossary spelling, for example FamilyKitchenGuide |

Every validated part must match the glossary exactly, because the builder's
dropdowns are strict and reject a paste with any other value. `names.py` checks this
against a fresh read of the glossary and points out near matches ("Azlaan" vs
"Azlaan ").

If a value the brief needs is not in the glossary yet (a new editor, persona or page),
stop and ask Murad to add it to the Ad Glossary first.
