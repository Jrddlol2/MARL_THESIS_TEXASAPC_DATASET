# Workspace & Repo Organization Prompt — Group B3 MARL Thesis
*(Supersedes the earlier cleanup framing — the goal here is structure, not removal.)*

> **How to use.** Run with access to `C:\Users\jared\Desktop\THESIS\` (data + the git repo at `THESIS\MARL\`) and
> `C:\Users\jared\Desktop\THESIS Claude\` (the Claude scratch workspace). **Propose the structure, get approval, then
> file things into it.** The point is a navigable layout + an index — **nothing is deleted; every file keeps a home.**

## ROLE
You are a workspace organizer. You impose a clear, purpose-based structure, give every file exactly one logical home, apply consistent naming, and produce a top-level index so anyone on the team can find anything. You **keep everything** — obsolete material is filed into a dated `archive/`, not removed. You use git so repo moves are reversible, and you never break the build or the agent workflow.

## GUIDING PRINCIPLE — organize, don't cull
- **Keep every file.** Organizing ≠ deleting. If something looks obsolete, it goes to `archive/` (labeled + dated), not to the bin.
- **One home per thing.** Group by *purpose* (manuscript / code / data / provenance / references / planning docs / archive). No file in two live places — designate a **canonical** copy and file the rest under archive with a note.
- **Self-documenting.** The output includes an `ORGANIZATION.md` map so the structure explains itself.
- **Consistent naming.** ISO dates (`YYYY-MM-DD`), lowercase-kebab or clear prefixes, no spaces in new folder names, group-by-prefix (e.g. `roadmap_`, `audit_`, `prompt_`).

## SAFETY RAILS (lighter than a cleanup, but keep these)
1. **Plan first.** Produce the inventory + a **move map** (each item → its new home) + the target tree, and **wait for approval** before moving anything.
2. **Repo moves via git.** For `THESIS\MARL\`: `git checkout -b chore/organize`, small commits (`git mv` to preserve history), never force-push, never `git rm` data.
3. **Don't break `CLAUDE.md`.** It references at the repo **root** by name: `main.tex`, `introduction.tex`, `problem.tex`, `methods.tex`, `thesis_refs.bib`, `TRACKER.md`, `REVISION_QUEUE.md`, `RTC_DECISION_LETTER.md`, `AUDIT_TRAIL.md`, `AUDIT_TRAIL_READABLE.md`. Move any → update every reference in `CLAUDE.md` in the **same commit**; otherwise leave them at root.
4. **Don't break LaTeX.** `main.tex` `\input`s the chapters and `\includegraphics` from `Figures/` by relative path — move a `.tex`/figure → update the path and **recompile to 0 errors** before committing. Safe default: leave the compile-set where Overleaf expects it and organize only the loose material around it.
5. **Never move raw data into git.** The 3.5 GB `APC_Raw_*.csv`, cleaned subsets, PDFs, and the geopackage stay git-ignored.
6. **Duplicates:** confirm with a `diff`/hash before declaring one canonical; a difference means it's a version → archive it, don't overwrite.

## CURRENT STATE (inventory — verified)
**Source of truth:** `THESIS\MARL\` = git clone of `Jrddlol2/MARL_THESIS_TEXASAPC_DATASET` — `.tex` sources, `thesis_refs.bib`, `scripts/`, `envs`?, `data/audit/`, `config/`, `Figures/`, `RRL/`, plus tracking docs (`AUDIT_TRAIL*.md`, `TRACKER.md`, `REVISION_QUEUE.md`, `PROGRESS.md`, `CHANGE_REPORT_*`, `RE_AUDIT_*`, `TEXAS_CAPMETRO_*`, `RTC_DECISION_LETTER.md`, `Manuscript_Pre_Major_Revision.pdf`).

**`THESIS\` also holds:** `APC_Raw_*.csv` (3.5 GB raw — keep, git-ignored); `Simulation\` (obsolete EDSA/Manila: `edsa_*.net.xml/.osm`, `planet_*.gpkg`); `_source_repos\` (two old manuscript clones); `Backups\` (`MARL`, `GitHub_Transfers`); `RRW\` (RRL PDFs — also duplicated in the scratch dir); `Paper\` (old draft PDF V2); `tmp\` (`pdfs`, `repo_compare` scratch); `RTC_COMPLIANCE_AND_REPO_SELF_AUDIT.md`.

**`THESIS Claude\` (scratch) holds this session's outputs** to file into the repo — `Implementation_Roadmap_2026-09-01.md`, `Roadmap_Prompt.md`, `Kickoff_Guide_Week1.md`, `Kickoff_Jared_Week1.md`, `DATA_CLEANING.md`, `Reference_Audit_Report_2026-09-01.md`, `Full_Reference_Audit_Prompt.md`, `RTC_Verification_Prompt.md`, `Organization_Prompt.md`, `starter_kit\` — **plus** older audit `.docx`, the `revised_2026-08-25/26` snapshots, an `RRW\` dup, `bg_capmetro_801_corridor.pdf`, `route801_dir6_stop_coordinates.csv`, a stray `__pycache__`.

## TARGET STRUCTURE (propose a concrete tree in the plan)
**Repo `THESIS\MARL\`** — file this session's loose work into homes; keep the compile-set + CLAUDE-referenced files at root unless you also update their references:
```
MARL/
├── (manuscript at root: main.tex, *.tex, thesis_refs.bib, Figures/)   ← leave for Overleaf, or → manuscript/ + fix paths
├── code/{scripts,envs,baselines}/     ← pipeline/extract/calibrate, bus_env, even_headway
├── sim/                               ← SUMO scenarios (net, routes, stops, cfg)
├── sim_inputs/                        ← stops.csv, stop_coordinates.csv
├── data/audit/ + data/(raw,processed gitignored)
├── references/                        ← RRL/sources.md (PDFs git-ignored, single location)
├── docs/
│   ├── planning/  ← roadmap, kickoff guides
│   ├── audits/    ← reference-audit report, DATA_CLEANING, RTC compliance
│   ├── prompts/   ← the reusable prompts
│   └── process/   ← TRACKER, REVISION_QUEUE, AUDIT_TRAIL*, PROGRESS, CHANGE_REPORT, RTC_DECISION_LETTER  (move ⇒ update CLAUDE.md)
├── CLAUDE.md · README.md · .gitignore
└── ORGANIZATION.md                    ← the map (key deliverable)
```
**Data root `THESIS\`:**
```
THESIS/
├── MARL/            (repo = source of truth)
├── data-raw/        (APC_Raw CSV — kept, git-ignored)
├── references/RRW/  (RRL PDFs — one canonical location)
└── archive/         (organized + dated: edsa-simulation/, old-manuscript-repos/, backups/, old-drafts/, docx-audits/, snapshots/, tmp/)
```
**`THESIS Claude\`:** after its valuable outputs are filed into the repo, keep it as a thin scratch dir (or fold the remainder into `THESIS\archive\`).

## WHAT TO DO
1. **Inventory & move map (no changes).** For every item across the three areas: path · what it is · **destination home** · canonical? · naming fix · risk. Diff suspected duplicates (RRW copies; `revised_*` vs repo; `_source_repos` vs repo) to pick the canonical. Present the before→after tree. **Stop for approval.**
2. **Create the skeleton.** Make the target folders (`docs/…`, `code/…`, `archive/…`, etc.). No file moves yet.
3. **File the loose work.** `git mv` this session's markdown + kit into their repo homes (small commits). Update `.gitignore` (raw CSV, subsets, PDFs, `__pycache__`, `*.pyc`, `*.gpkg`). If you move a CLAUDE-referenced or `\input` file, fix the references + recompile in the same commit.
4. **Consolidate references** to one RRL location; record the canonical, file any divergent dup into `archive/` with a note.
5. **Archive (organized, not deleted).** Move `Simulation/`, `_source_repos/`, `Backups/`, `Paper/`, the docx audits, `revised_*` snapshots, and `tmp/` into dated `THESIS\archive\<category>\` with a one-line `_WHATIS.txt` in each.
6. **Write `ORGANIZATION.md`** — the map: where each kind of thing lives, the naming conventions, and where old material was filed. Add a short "layout" section to the repo README.
7. **Verify.** LaTeX compiles (0 errors); `git status` clean, no large files tracked; the index matches reality; every KEEP/ARCHIVE item is present (nothing lost).

## CONSTRAINTS
- Nothing moves before the move map is approved. Nothing is deleted — obsolete → `archive/`.
- Raw data and source PDFs stay git-ignored and out of the repo.
- Repo changes are small reversible `git mv` commits on a branch; the manuscript still compiles.
- Keep provenance together: `data/audit/*.json`, checksums, and `DATA_CLEANING.md`.
- Each finding: exact path · destination · one-line reason. No vague "organize better."

## OUTPUT FORMAT
1. **Move map** — path · type · destination home · canonical? · naming fix · risk.
2. **Before → after tree** — the three areas, current vs organized.
3. **Duplicate/version report** — diffs behind each canonical choice.
4. **Execution log** — ordered `git mv` / file moves actually performed.
5. **`ORGANIZATION.md`** — the final map + naming conventions + archive index.
6. **Verification** — compile result, `git status`, confirmation nothing was lost.
