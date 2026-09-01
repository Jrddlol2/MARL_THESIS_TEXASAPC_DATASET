# Workspace & Repo Cleanup Prompt — Group B3 MARL Thesis

> **How to use.** Run in a session with access to `C:\Users\jared\Desktop\THESIS\` (data + the git repo at
> `THESIS\MARL\`) and `C:\Users\jared\Desktop\THESIS Claude\` (the Claude scratch workspace). **Plan first, get
> approval, then execute** — this reorganizes real files, so nothing is moved or deleted until the plan is signed off.

## ROLE
You are a careful workspace and repository organizer. You consolidate to a single source of truth, de-duplicate, and archive obsolete material **without losing data and without breaking the build or the agent workflow**. You prefer moving/archiving over deleting, you use git so every repo change is reversible, and you never touch raw data.

## ⚠️ SAFETY RULES (read before touching anything)
1. **Plan before acting.** Produce the full inventory + a per-item **KEEP / MOVE / ARCHIVE / DELETE** table + a before→after tree, and **wait for explicit approval** before any move or delete.
2. **Never delete raw data or sources.** The 3.5 GB `APC_Raw_*.csv`, the geopackage, and all RRL/source PDFs are archive-at-most, never delete.
3. **Move/archive, don't delete.** Create `THESIS\_archive\` and move obsolete/superseded items there. Delete only true junk (`__pycache__`, `*.pyc`, `tmp/` scratch) and only with explicit confirmation.
4. **Repo = git, reversible.** For anything under `THESIS\MARL\`: branch first (`git checkout -b chore/cleanup`), commit in small logical steps with clear messages, never `git rm` data, never force-push.
5. **Don't break the agent workflow.** `MARL\CLAUDE.md` references these at the repo **root** by name: `main.tex`, `introduction.tex`, `problem.tex`, `methods.tex`, `thesis_refs.bib`, `TRACKER.md`, `REVISION_QUEUE.md`, `RTC_DECISION_LETTER.md`, `AUDIT_TRAIL.md`, `AUDIT_TRAIL_READABLE.md`. If you move any, **update every reference in `CLAUDE.md` in the same commit**, or leave them at root.
6. **Don't break LaTeX.** `main.tex` `\input`s the chapter files and `\includegraphics` from `Figures/` by relative path. If you move a `.tex` or a figure, update the path and **recompile to confirm 0 errors** before committing.
7. **Verify duplicates before removing.** `diff` (or hash) a suspected duplicate against the canonical copy; if it differs, it's a version, not a dupe — archive it, don't delete.
8. **Confirm the source of truth first.** `THESIS\MARL\` (the git clone) is canonical for manuscript + code + data-provenance. Everything else is reconciled against it.

## CURRENT STATE (inventory — verified)
**Canonical repo:** `THESIS\MARL\` (git clone of `Jrddlol2/MARL_THESIS_TEXASAPC_DATASET`) — holds the `.tex` sources, `thesis_refs.bib`, `scripts/`, `data/audit/`, `config/`, `Figures/`, `RRL/`, and many tracking docs (`AUDIT_TRAIL*.md`, `TRACKER.md`, `REVISION_QUEUE.md`, `PROGRESS.md`, `CHANGE_REPORT_*`, `RE_AUDIT_*`, `TEXAS_CAPMETRO_*`, `RTC_DECISION_LETTER.md`, `Manuscript_Pre_Major_Revision.pdf`).

**`THESIS\` (data root) also contains:**
- `APC_Raw_July_2021_-_December_2021_20260824.csv` — **3.5 GB raw data. Keep. Must be git-ignored.**
- `Simulation\` — **obsolete EDSA (Manila) pre-pivot data** (`edsa_corridor.net.xml`, `edsa_raw.osm`, `planet_*.gpkg`). Superseded by CapMetro → archive.
- `_source_repos\` — **two old manuscript git clones** (`Group-B3-Manuscript-Draft-V3_main`, `GroupB3_Manuscript_main`). Superseded → archive.
- `Backups\` (`MARL`, `GitHub_Transfers`) — backup copies → consolidate under `_archive\` or a single backup location.
- `RRW\` — RRL source PDFs (**duplicated** with `THESIS Claude\RRW\`).
- `Paper\` — an old manuscript draft PDF (V2) → archive.
- `tmp\` (`pdfs`, `repo_compare`) — scratch → clear.
- `RTC_COMPLIANCE_AND_REPO_SELF_AUDIT.md` — decide: fold into repo `docs/` or archive.

**`THESIS Claude\` (Claude scratch workspace) contains:**
- **New, valuable deliverables (this session)** → consolidate into the repo: `Implementation_Roadmap_2026-09-01.md`, `Roadmap_Prompt.md`, `Kickoff_Guide_Week1.md`, `Kickoff_Jared_Week1.md`, `DATA_CLEANING.md`, `Reference_Audit_Report_2026-09-01.md`, `Full_Reference_Audit_Prompt.md`, `RTC_Verification_Prompt.md`, `Cleanup_Prompt.md`, and `starter_kit\` (runnable: sim_inputs, calibrated `sumo/`, `envs/`, `baselines/`, `scripts/`).
- **Older audit artifacts (docx)** → archive: `*_Changes_*.docx`, `Conformity_of_Revisions_*.docx` (×2 — check for dupe), `Manuscript_Change_Audit_*.docx`, `Methodology_Audit_Ch3.docx`, `Overleaf_Revision_Sheet.docx`, `RTC_Verification_Report.docx`.
- **Snapshots** `revised_2026-08-25\`, `revised_2026-08-26\` — reconcile against the repo, then archive (the repo is newer; `revised_2026-08-26` is a partial older copy).
- `RRW\` (dup of `THESIS\RRW\`), `bg_capmetro_801_corridor.pdf`, `route801_dir6_stop_coordinates.csv`, `starter_kit\envs\__pycache__\` (delete).

## TARGET (principles — propose a concrete tree in the plan)
- **One source of truth:** `THESIS\MARL\` (the repo) for manuscript + code + provenance.
- **Repo gets a `docs/` (or `planning/`) folder** for the roadmap, kickoff guides, data-cleaning record, reference-audit report, and the reusable prompts — so this session's outputs live with the project, versioned. (Decide whether to also move the root tracking docs there **and** update `CLAUDE.md`, or leave them at root.)
- **Runnable kit** → repo as `starter/` (or merge into existing `scripts/`+`envs/`).
- **`THESIS\_archive\`** holds: `Simulation\` (EDSA), `_source_repos\`, `Backups\`, `Paper\`, the docx audits, and the `revised_*` snapshots — nothing deleted, just out of the way.
- **One RRL PDF location** (e.g. `THESIS\RRW\`, git-ignored), referenced by `RRL/sources.md`; remove the duplicate copy after confirming they match.
- **`.gitignore` covers:** the raw CSV, any cleaned subset CSV, `RRL/*.pdf`, `__pycache__/`, `*.pyc`, `*.gpkg`, and other large binaries. Verify `git status` shows no huge/binary files staged.

## WHAT TO DO
**Phase 1 — Inventory & plan (no changes).** Walk all three areas; for every top-level item output a row: path · what it is · **KEEP / MOVE→dest / ARCHIVE / DELETE** · reason · risk. Diff suspected duplicates (RRW copies; `revised_*` vs repo; `_source_repos` vs repo) to confirm. Present the before→after tree. **Stop and get approval.**

**Phase 2 — Repo hygiene (after approval).** `git checkout -b chore/cleanup`. Fix `.gitignore` first; confirm the raw CSV and other large files are ignored and not tracked. Create `docs/` and move this session's markdown in (and the kit as `starter/`), committing in small steps. If you move any root tracking doc or `.tex`/figure, update `CLAUDE.md` / `\input` / `\includegraphics` in the **same** commit and recompile.

**Phase 3 — Consolidate scratch.** Move the valuable `THESIS Claude\` deliverables into the repo (Phase 2 destinations). Copy, verify, then archive the originals — don't leave two live copies.

**Phase 4 — Archive obsolete + de-dupe.** Create `THESIS\_archive\` and move `Simulation\`, `_source_repos\`, `Backups\`, `Paper\`, the docx audits, and the `revised_*` snapshots there. Remove the duplicate RRW copy (after the diff), clear `tmp\` and `__pycache__` (with confirmation).

**Phase 5 — Verify.** LaTeX compiles with 0 errors; `git status` clean and no large files tracked; a short `ORGANIZATION.md` (or README section) documents the final structure and where things went; nothing on the KEEP/ARCHIVE list is missing.

## CONSTRAINTS
- Nothing is moved or deleted before the Phase-1 plan is approved.
- Raw data and source PDFs are never deleted.
- Every repo change is a small, reversible git commit on a branch; the manuscript must still compile.
- Preserve provenance: keep `data/audit/*.json`, checksums, and `DATA_CLEANING.md` intact and together.
- For each finding: exact path + action + one-line reason. No vague "tidy up."

## OUTPUT FORMAT
1. **Disposition table** — path · type · KEEP/MOVE/ARCHIVE/DELETE · destination · reason · risk.
2. **Before → after tree** — the three areas, current vs proposed.
3. **Duplicate/obsolete report** — diffs confirming what's safe to remove.
4. **Execution log** — ordered git commits + file moves actually performed (Phase 2–4).
5. **Verification** — compile result, `git status`, and the final `ORGANIZATION.md`.
