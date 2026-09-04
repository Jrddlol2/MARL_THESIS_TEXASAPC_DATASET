# Slide 5 Revision Prompt — MSA1_B3_Presentation_v6.pptx

Revise slide 5 of MSA1_B3_Presentation_v6.pptx. Do not rebuild the deck — edit in place and preserve the existing visual system.

## What's wrong
Slide 5 ("Data Acquisition: The EDSA Constraint") is a four-node timeline of our data-request history with beats like "No response" and "No update since." To a panel this reads as a grievance narrative, and it spends a full slide on process instead of substance. The panel does not need the chronology. It needs to know what the dataset contains and why it is the right dataset for this study.

## Replace with
Title: "What the Data Gives Us" (eyebrow label stays "THE DATASET")

1. Acquisition in ONE neutral sentence, as a small lead-in line under the title — not a heading, not a timeline, no agency names, no dates, no outcome-by-outcome beats:
   > "EDSA operational data was not obtainable through official channels within our timeline, so we moved to a public, fully documented dataset. EDSA remains the corridor that motivates the study."

2. Body = four rows mapping "What the study needs" -> "What the dataset provides":
   - Per-stop passenger demand -> APC boarding and alighting counts at every stop event
   - Realistic dwell and running times -> timestamped dwell time, segment travel time and distance
   - A physical corridor to simulate -> stop-level GPS coordinates with quality flags (98.1% rated high quality)
   - Non-ideal conditions we can observe rather than invent -> joinable NOAA weather; all 229,421 events matched a reading within 90 minutes, 11,804 during rainfall

3. Closing line — why PUBLIC mattered, in one sentence: every figure is traceable to a documented public source and checksum-verified, which a private operational feed would not have allowed.

## Constraints
- No number may repeat from slide 7 (source / scale / recordkeeping) or slide 8 (cleaning funnel). Division of labor: slide 5 = why this data fits, slide 6 = why 801 over 803, slide 7 = provenance and scale, slide 8 = how it was cleaned.
- Adjust slide 6: delete its first paragraph ("We needed a public dataset we could fully document...") — that reasoning now lives on slide 5. The 801-vs-803 comparison becomes the whole slide.
- Tone: plain declarative. Past tense for the acquisition line, present tense for what the data contains. No "unfortunately," no hedging, no dramatization.
- Keep the footer "Group B3 | MARL Dynamic Bus Scheduling | MSA 1", slide number 5, 16:9 (12192000 x 6858000 EMU), and the type scale, color palette, and card/row styling used on slides 6-8.
- Speaker notes on slide 5: the full chronology (SafeTravelPH request April 2026 -> FOI PH filing -> DOTr -> LTFRB) in three factual sentences, so it can be answered if a panelist asks why the dataset changed. It belongs in Q&A, not on the slide.

## Optional
Preserve the existing timeline as a backup slide placed after "Thank You," outside the numbered flow, titled "Backup — Data Acquisition Record." Retitle each node to agency / action taken / outcome, with no editorializing.

## Deliverable
Edited .pptx: slide 5 replaced, slide 6 trimmed, speaker notes added. Slide count stays 16 (17 with the backup slide).
