# Reusable prompt — line-by-line code walkthrough

**Purpose:** produce a walkthrough of a source file (or folder) that a teammate
or a thesis panel can follow without reading the code, and that makes every
non-obvious decision in the code explicit.

**How to use:** paste this into a fresh session with repo access, fill in the
TARGET block, run it. Written to be run against the live repo, never against a
summary or a pasted snippet.

---

## ROLE

You are documenting code you did not write and must not trust. Read every line
of the target before writing a word about it. If you cannot explain why a line
exists, say so explicitly rather than inventing a rationale — an honest "this
appears to be vestigial, no caller found" is worth more than a confident guess.

## TARGET (fill this in)

```
FILES:      <paths, or a folder>
AUDIENCE:   <e.g. teammates who know pandas but not this project; a thesis panel>
DEPTH:      <line-by-line | block-level | mixed — say which files get which>
```

## HARD RULES

1. **Cite real line numbers.** Every claim points at `file.py:NN`. Re-read the
   file to get them; do not carry numbers over from memory or from an earlier
   version.
2. **Verify, do not assume.** Before writing "this is called by X", grep for it.
   Before writing "this takes N seconds", time it. Before writing "this produces
   N rows", run it or read the recorded output. Mark anything you could not
   check as `UNVERIFIED`.
3. **Explain the WHY, not the WHAT.** `df = df.copy()` does not need a sentence.
   `na_filter=False` does — it changes how every comparison below it behaves.
   Skip the self-evident; expand the load-bearing.
4. **Name every landmine.** Anything that would bite the next reader:
   off-by-one risk, a parameter whose default matters, a silent type coercion,
   a value that must match something in another file, a comment that no longer
   matches the code.
5. **Report dead code.** Functions with no callers, unreachable branches,
   parameters never passed, imports never used. Grep to confirm before saying
   so. This is often the most valuable output of the exercise.
6. **No invented history.** Do not speculate about why something was written a
   certain way unless git blame or a comment says so.

## WHAT TO PRODUCE

For **each file**, in this order:

### 1. One-sentence purpose
What breaks if this file is deleted.

### 2. Position in the pipeline
What feeds it, what it feeds. One diagram line is fine.

### 3. Walkthrough
Work top to bottom. Group consecutive trivial lines (`L45–52 — imports`) and
expand the rest individually. For each expanded line or block give:

```
L<NN>   <the line, or a faithful paraphrase>
        WHAT  one clause
        WHY   the reason it is written this way, if non-obvious
        WATCH the failure mode, if there is one
```

Omit `WHY` and `WATCH` when there genuinely isn't one — padding every entry
makes the important ones invisible.

### 4. Inputs and outputs
Exact paths. Which are read, which are written, which are overwritten.

### 5. Numbers this file produces
Every figure that ends up in a slide, a report, or the manuscript, with the
line that computes it. This is the traceability table — it is what lets someone
answer "where did 229,421 come from?" without reading the code.

### 6. Findings
Dead code · stale comments · hardcoded values that should be config · anything
duplicated elsewhere · anything you could not verify. Empty section if clean —
say "none found", do not omit the heading.

## STYLE

- Plain English. A reader who knows Python but not this project should follow it.
- Tables for anything with more than three parallel items.
- Short paragraphs. No preamble, no "in this section we will".
- Do not restate the file's own docstring back at the reader — build on it.

## OUTPUT

One markdown file: `docs/reference/CODE_WALKTHROUGH_<scope>.md`.

Open with a **file index** (name · lines · one-line purpose) so the reader can
jump. Close with a **consolidated findings list** across all files, most
important first.

## SELF-CHECK BEFORE YOU FINISH

- [ ] Every cited line number re-read from the current file, not remembered
- [ ] Every "is called by" / "is unused" claim confirmed by grep
- [ ] Every runtime or row-count claim measured, or marked UNVERIFIED
- [ ] Every number that appears in a deliverable appears in section 5
- [ ] Findings section present for every file, even if it says "none found"
