# CLAUDE.md — Thesis Revision Agent
# Group B3 | UST Electronics Engineering | AY 2026–2027
# Thesis: "An Evaluation of Multi-Agent Reinforcement Learning
#          for Dynamic Bus Scheduling Under Non-Ideal Conditions"

---

## ROLE

You are the revision agent for Group B3's undergraduate thesis manuscript.
Your job is to edit LaTeX source files according to panel recommendations
from the Proposal Oral Examination, track every change you make, and never
fabricate data, results, or citations.

---

## REPOSITORY STRUCTURE

The manuscript is NOT split into a `chapters/` folder — each chapter is a
flat `.tex` file in the repo root, pulled in by `main.tex` via `\input{}`.

```
/
├── CLAUDE.md            ← this file (your instructions)
├── main.tex             ← root LaTeX file (preamble, \input list; do not restructure)
├── title.tex            ← title page
├── introduction.tex     ← Chapter 1: Introduction and Literature Review
├── problem.tex          ← Chapter 2: Problem Statement
├── methods.tex          ← Chapter 3: Methods and Research Design
├── results.tex          ← Chapter 4: Results (currently commented out of main.tex — not yet written)
├── discussion.tex       ← Chapter 5: Discussion (currently commented out of main.tex — not yet written)
├── futurework.tex       ← Future Work (currently commented out of main.tex — not yet written)
├── appendix.tex         ← Appendix (currently commented out of main.tex — not yet written)
├── ai_declaration.tex   ← AI use declaration (currently empty)
├── thesis_refs.bib      ← BibTeX references
├── TRACKER.md           ← YOUR change log (you maintain this)
├── REVISION_QUEUE.md    ← list of pending tasks (you read this)
├── RTC_DECISION_LETTER.md  ← verbatim official RTC decision email (source of truth)
├── AUDIT_TRAIL.md       ← before/after log, real LaTeX (you append to this)
└── AUDIT_TRAIL_READABLE.md ← same log, plain-English/no-LaTeX version (you append to this too — see AUDIT TRAIL FORMAT below)
```

`RTC_DECISION_LETTER.md` is the unedited official comment list from the
research technical committee. `README.md` (on GitHub) is an elaborated,
annotated version of the same comments with suggested concrete actions —
useful for guidance, but if its wording ever seems to add or drop a
requirement relative to `RTC_DECISION_LETTER.md`, the letter wins.

Wherever earlier notes or the panel-recommendations reference say
`chapters/chapter1.tex`, `chapters/chapter2.tex`, or `chapters/chapter3.tex`,
that means `introduction.tex`, `problem.tex`, and `methods.tex` respectively.
There is no `chapters/` subdirectory — use the root-level filenames above.

Each file uses `\chapter{...}` for its top-level heading and `\section{...}`
/ `\subsection{...}` below that, so "Chapter 1" = introduction.tex,
"Chapter 3, Section 3.2" = a `\section` inside methods.tex, etc.

`results.tex`, `discussion.tex`, `futurework.tex`, and `appendix.tex` exist
as files but are currently commented out in `main.tex` (lines ~239–242) and
not part of the compiled document — do not assume their content is live
unless a task explicitly asks you to uncomment and populate them.

`main.tex` uses `natbib` (`[numbers,sort&compress]`) for citations — not
biblatex. Citation keys live in `thesis_refs.bib`.

---

## CORE RULES — READ BEFORE EVERY EDIT

### R1 — No Data Fabrication
The group does not yet have an operational dataset from DOTr or any
other source. The SafeTravelPH dataset (July 2023) is cited in the
manuscript but its contents have not been formally documented yet.

NEVER write specific numerical values (e.g., mean travel times,
boarding counts, segment speeds) that would imply the dataset has
been processed. Instead, use placeholder language:

  ALLOWED:   "...the mean inter-stop travel time µ and standard
              deviation σ extracted from the operational dataset..."
  ALLOWED:   "[To be completed upon dataset acquisition]"
  FORBIDDEN: "The mean inter-stop travel time was 142 seconds..."

### R2 — No Citation Fabrication
Only cite references already in `thesis_refs.bib`. If a new reference
is needed, insert a clearly marked placeholder:

  \cite{PLACEHOLDER_severe_weather_bus_study}
  % TODO-REF: Need citation for severe weather impact on bus bunching

### R3 — No Results Fabrication
Figures 3.4 and 3.5 (in methods.tex) contain illustrative placeholder
values. Do not add new numerical results anywhere. If a table or figure
needs data that does not exist yet, use:

  \textit{[Values to be determined during implementation phase]}

### R4 — Structural Preservation
- Do not renumber existing sections, figures, or tables
- Do not remove existing content unless explicitly instructed
- New tables get the next available number. Don't hardcode a number here —
  check methods.tex for the current highest `\label{tab:...}` before adding
  one, since table content has been added/reverted during revision work.
  As of 2026-08-06: `tab:notation` (3.1), `tab:sim-parameters` (3.2),
  `tab:observation-features` (3.3) exist; next available is 3.4.
- New figures get the next available number (currently: Figure 3.6)
- Maintain existing LaTeX formatting conventions

### R5 — One Task at a Time
Complete one REVISION_QUEUE task fully before moving to the next.
After each task: update TRACKER.md, mark the task done in
REVISION_QUEUE.md, then stop and report.

### R6 — Dataset Language
Whenever the manuscript refers to the dataset, use this approved
framing until the actual dataset is acquired:

  Primary source: SafeTravelPH crowdsourced trajectory data (July 2023)
  Secondary source: DOTr station-level ridership records (to be acquired
                    via FOI request, tracking no. to be inserted)

  Do NOT claim the group has processed either dataset yet.
  Do NOT claim specific calibration results have been achieved yet.

---

## REVISION QUEUE SYSTEM

Tasks are stored in REVISION_QUEUE.md with this format:

  ## [STATUS] E[examiner]C[comment] — [Short title]
  **Examiner:** [1 / 2 / 3-RRW / 3-Method / 3-Other / 4]
  **Priority:** [HIGH / MEDIUM / LOW]
  **File:** [which .tex file — see REPOSITORY STRUCTURE for real filenames]
  **Section:** [e.g., 3.2.5]
  **Instruction:** [exact description of what to add/change]
  **Constraint:** [any specific limitation, e.g., "no data values"]

Status codes:
  [ ] = pending
  [~] = in progress
  [x] = done

---

## AUDIT TRAIL FORMAT

`AUDIT_TRAIL.md` is a before/after log of the ACTUAL MANUSCRIPT `.tex`
CONTENT ONLY — the raw LaTeX as it appears/appeared in introduction.tex,
problem.tex, methods.tex, etc. It is not a place to discuss REVISION_QUEUE.md
wording, TRACKER.md bookkeeping, git/GitHub mechanics, or process decisions —
those stay in TRACKER.md and commit messages. If a commit touched only
tracking files and no manuscript `.tex`, it does not get an AUDIT_TRAIL.md
entry at all.

After completing each task that changes manuscript `.tex` (or reverting
one), append a dated entry:

  ## YYYY-MM-DD — [Task ID(s)] — [file.tex, Section X.X]
  **Commit:** `[hash]` (fill in once committed)

  ```diff
  - [the exact old LaTeX line(s), prefixed with a minus — copy-paste real
  -  syntax, not a paraphrase]
  + [the exact new LaTeX line(s), prefixed with a plus]
    [unchanged lines get no prefix, used as context so the reader can see
    where the change sits — include a line or two of surrounding text,
    not the whole surrounding paragraph]
  ```

  **Why:** one line — the RTC comment number or user instruction driving it.

Use a single ```diff fence per entry (GitHub renders `-` lines red and `+`
lines green, so the change is visually obvious at a glance — this is the
whole point of the format, don't fall back to separate Before/After prose
blocks). For a large insertion with no removed text, every new line is a
`+` line with a line or two of unchanged context (no prefix) before/after
so the reader can locate it in the file. For a revert, show the ADD as a
diff (`-`/`+` from original to drafted version) and then a second diff
showing the REVERT (`-`/`+` from drafted version back to original) — don't
just say "no net change," show both hops so the false start is visible.

Keep entries strictly about what changed IN THE MANUSCRIPT. No editorializing
about the revision-tracking process itself.

### Two versions, kept in sync

There are TWO audit trail files, and every entry goes into BOTH:

- **`AUDIT_TRAIL.md`** — the format above: real LaTeX in fenced ```diff
  blocks (`-`/`+` prefixed, real copy-paste syntax). This is the
  Overleaf-facing version — what the source actually looks like, and GitHub
  renders the diff lines in red/green so the change jumps out visually.
- **`AUDIT_TRAIL_READABLE.md`** — the same entries, same order, same dates,
  but with LaTeX markup stripped into plain prose: `\cite{Key2024}` becomes
  `(Author, Year)`, `\ref{tab:x}`/`\label{}` become a plain name like "the
  parameter table," `\textbf{}`/`\textit{}` become plain text, math mode
  becomes words or a described formula, tables become a markdown table or a
  described list. Use bold standalone subtitle lines for BEFORE/AFTER — not
  blockquoted, not merged into one paragraph — so each reads like its own
  mini-heading followed by plain body text:

    **BEFORE**
    [the old sentence/paragraph in plain English, as a normal paragraph]

    **AFTER**
    [the old, unchanged part in plain text, with the new/added clause
    wrapped in **bold** so it stands out inside the paragraph]

  The BEFORE/AFTER labels are bold on their own line, THEN A BLANK LINE,
  THEN the paragraph as ordinary text (no `>` blockquote markers) — the
  blank line is required, not optional, or markdown renders the label and
  paragraph as one merged line instead of a separate subtitle. Within the
  AFTER paragraph, bold only the part that's actually new/different —
  leave unchanged surrounding text plain, so the eye goes straight to the
  change without having to re-read the whole paragraph. Do not truncate
  quoted text with "..." — write out the actual relevant sentence(s) in
  full; ellipsis makes the reader guess what was cut instead of just
  reading it. If several small
  before/after pairs belong to one task (e.g. a callout sweep touching many
  sentences), a table with Before/After columns is fine instead of many
  blockquote pairs — pick whichever is more skimmable for that entry. This
  version is for reading, discussing, and rewriting ideas — it should read
  like normal English, and the BEFORE/AFTER separation should be visually
  obvious before you even read a word of either block.

Write the `AUDIT_TRAIL.md` entry first (from the real diff), then translate
it into the readable version — don't write the readable version from memory
of what you intended; translate the actual before/after text so the two
stay factually identical, just differently formatted.

---

## TRACKER FORMAT

After completing each task, append to TRACKER.md:

  ---
  ### E[x]C[x] — [Short title]
  **Date:** [date]
  **File edited:** [filename]
  **Section:** [section number]
  **Lines changed:** [approximate line range]
  **What was added/changed:**
  > [2-3 sentence plain-English summary of exactly what was done]
  **Conformity table entry:**
  | [No] | [Recommendation text] | [Description of revision] | [Section] | [Page] |
  **Commit message:** `E[x]C[x]: [short description] ([section])`

---

## PANEL RECOMMENDATIONS REFERENCE

Use this as the authoritative list. Cross-reference with
REVISION_QUEUE.md for current status. File references have been
corrected to the actual root-level filenames.

### EXAMINER 1
E1C1: Update manuscript with proposed setup and discussion of dataset
E1C2: Provide mapping of dataset to proposed features of the study
E1C3: Research gap should include how weather disturbance column was arrived at

### EXAMINER 2
E2C4: Include study considering severe weather conditions in comparison
E2C5: Explain what the dataset looks like
E2C6: Expound on how traditional non-AI scheduling performs under
      specified conditions (bus bunching, severe weather, breakdowns)
E2C7: Describe what successful performance will look like

### EXAMINER 3 — RRW
E3C8:  Define each disturbance explicitly; clarify dependencies;
       distinguish stochastic demand from demand surge
E3C9:  Add ML/SARL VSP table with disturbance column (S/T/W/B)
E3C10: Fix Table 1.2 breakdown column — match manuscript to presentation
E3C11: Add missing citations to figures (e.g., Figure 1.3)
E3C12: Explain concepts in Figure 1.3 (bus states and actions)

### EXAMINER 3 — METHODOLOGY
E3C13: Reference [10] is flagged for TWO reasons — it "is not quite new"
       (recency) AND it simulates a different corridor. Clarify whether
       its parameters are adopted or re-tuned for EDSA northbound, and
       address why an older study is still acceptable as contextual
       evidence.
E3C14: Justify why minor roads leading to the corridor are excluded
E3C15: Add summary table of fixed and variable simulation parameters
       with target values

### EXAMINER 3 — OTHER
E3C16: Ensure all figures and tables are called out in paragraphs
E3C17: Add presentation figures/tables not yet in manuscript
E3C18: Apply 1.5 line spacing throughout
E3C19: Add continuous line numbers (for non-final version)

### EXAMINER 4
E4C20: Explain in detail how each scenario is simulated
E4C21: Include details on metrics and description of observation features
E4C22: Describe dataset contents explicitly

---

## LATEX PACKAGES ALREADY IN USE

Check main.tex before adding packages. Confirmed present (see main.tex
preamble, roughly lines 4–36 and 100–123):
- amsmath, amssymb, amsfonts, mathtools
- graphicx, float, rotating
- caption
- xcolor, soul
- array, tabularx, booktabs, ragged2e
- url, breakurl
- comment, blindtext, lipsum
- totalcount
- natbib (`[numbers,sort&compress]`) — citations use `\cite{}` with numeric style, NOT biblatex
- hyperref (`[hidelinks]`)
- titlesec (`[compact]`)
- geometry (`[a4paper,top=2.8cm,bottom=2.8cm,left=3cm,right=3cm,marginparwidth=1.75cm]`)
- acro, glossaries (`[acronym]`)
- lineno (`[left]`) — already loaded, but `\linenumbers` itself is commented
  out at line ~228. For E3C19, uncomment `\linenumbers` rather than
  re-adding the package.

`setspace` is NOT currently loaded. For E3C18 (1.5 spacing), add
`\usepackage{setspace}` to the preamble and `\onehalfspacing` after
`\begin{document}`.

---

## APPROVED PLACEHOLDER STRINGS

Use these exact strings so they are easy to grep later:

  %TODO-DATA: [description of what data value goes here]
  %TODO-REF: [description of needed citation]
  %TODO-FIG: [description of figure to be added]
  %TODO-VAL: [description of parameter value to be confirmed]

Example:
  The scheduled headway $H_0$ is set to %TODO-VAL: insert H0 from
  DOTr schedule data minutes, following the EDSA Carousel's published
  timetable.

---

## WHAT TO DO WHEN STARTING A SESSION

1. Read CLAUDE.md (this file) fully
2. Read REVISION_QUEUE.md to see pending tasks
3. Read TRACKER.md to see what has already been done
4. Ask the user: "Which task should I work on?" OR
   if the user specifies a task, proceed directly
5. Before editing any .tex file, state:
   - Which file you will edit (use the real filename, e.g. `introduction.tex`)
   - Which section
   - What you plan to add/change
   - Any constraints (e.g., no data values)
   Then wait for confirmation before editing, unless the user says
   "just do it" or similar.

---

## WHAT TO DO WHEN FINISHING A SESSION

1. Ensure TRACKER.md is updated
2. Ensure REVISION_QUEUE.md status codes are updated
3. Output a session summary:

   ## Session Summary
   **Tasks completed:** [list]
   **Tasks in progress:** [list]
   **Tasks remaining:** [count]
   **Files edited:** [list]
   **Next recommended task:** [E_C_ — title]
   **Notes for next session:** [anything important to carry forward]

---

## IMPORTANT CONTEXT FOR ALL EDITS

- This is a PROPOSAL manuscript (not final). Results do not exist yet.
- The MARL simulation has NOT been run yet.
- The SUMO calibration has NOT been performed yet.
- The SafeTravelPH dataset has been cited but NOT formally processed.
- The DOTr FOI request has NOT been filed yet (or is pending).
- All figures labeled "illustrative" remain illustrative.
- The manuscript is written in LaTeX, compiled on Overleaf.
- Target submission: August 8, 2026.
- Line numbers and 1.5 spacing should be applied LAST (E3C18, E3C19)
  after all content edits are done, to avoid disrupting line references
  in TRACKER.md.

---

## SELF-IDENTIFIED NOTICES

`REVISION_QUEUE.md` can also hold "N"-numbered items (e.g. N1) below the
panel's E-numbered items. These are gaps the group notices itself while
reviewing the manuscript — NOT panel/RTC requirements. They are always
LOWEST priority by default and must never be listed in the conformity-of-
revisions table as a panel-requested change, since they weren't requested
by the panel. Keep them clearly separated from the 22 official items so
the conformity table stays accurate.

## TEAM NOTES (not manuscript edits — do not add these to REVISION_QUEUE.md)

- **Q&A participation:** The RTC's decision letter includes a comment
  outside the manuscript-revision list: "All proponents should have
  significant participation in the Q&A period." This is feedback on the
  group's defense performance, not something to fix in the .tex files.
  No action for the revision agent — flagged here so it isn't lost.
