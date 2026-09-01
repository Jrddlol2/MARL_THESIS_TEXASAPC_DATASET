# Repository & Workspace Organization
*Organized 2026-09-01. Source of truth = this repo (`THESIS/MARL/`). Nothing was deleted — obsolete material was relocated to `THESIS/archive/`.*

## Where things live

### Repo `THESIS/MARL/` (canonical)
| Location | Contents |
|---|---|
| root `*.tex`, `thesis_refs.bib`, `Figures/` | LaTeX compile-set — **kept at root** for Overleaf |
| root `CLAUDE.md`, `TRACKER.md`, `REVISION_QUEUE.md`, `AUDIT_TRAIL*.md`, `RTC_DECISION_LETTER.md`, `PROGRESS.md`, `CHANGE_REPORT_*` | agent-workflow files — **kept at root** (referenced by `CLAUDE.md`) |
| `docs/planning/` | implementation roadmap, Week-1 kickoff guides |
| `docs/prompts/` | reusable prompts (reference-audit, roadmap, RTC-verification, organization, cleanup) |
| `docs/reference/` | `DATA_CLEANING.md` (data provenance) |
| `reports/` | audit reports (2026-08-23 set + `Reference_Audit_Report_2026-09-01.md`) |
| `starter/` | runnable kit: `sim_inputs/`, calibrated `sumo/`, `envs/`, `baselines/`, `scripts/` |
| `submissions/` | **frozen as-submitted checkpoints** |
| `scripts/`, `config/`, `data/audit/`, `RRL/` | existing: data pipeline, config, provenance JSONs, RRL index |

### `THESIS/` (data root)
| Item | Note |
|---|---|
| `APC_Raw_*.csv` | 3.5 GB raw data — kept, outside the repo, git-ignored |
| `MARL/` | the repo (canonical) |
| `RRW/` | canonical RRL source PDFs (50), referenced by `MARL/RRL/sources.md` |
| `archive/` | organized, dated, reversible — see below |

### `THESIS/archive/` (kept, not deleted)
`edsa-simulation/` (pre-pivot EDSA/Manila SUMO data) · `old-manuscript-repos/` (old clones) · `backups/` · `old-drafts/` · `docx-audits/` (8 working `.docx`) · `snapshots/` (`revised_2026-08-25/26`) · `duplicates/` (dup assets) · `references-old/` (`RTC_COMPLIANCE…`, `RRW-partial-old`) · `scratch/` (`tmp`). Each has a `_WHATIS.txt`.

## Checkpoint (frozen)
`MARL/submissions/2026-08-29_proposal-revision_AS-SUBMITTED/` — the exact manuscript + conformity PDFs as submitted 2026-08-29. **Do not edit or move.** Later edits happen in the `.tex` sources.

## Conventions
ISO dates (`YYYY-MM-DD`), clear prefixes (`roadmap_`, `audit_`, `prompt_`), no spaces in new folder names, one canonical home per file.

## Still on you (two follow-ups)
1. **Commit:** the repo changes are **staged, not committed** — review `git status` and commit (a `chore/organize` branch is fine). Staged report moves are `git mv` renames; `docs/`, `starter/`, `submissions/`, `ORGANIZATION.md` are new.
2. **Final de-dup:** `THESIS Claude/` still holds the original session `.md` files + `starter_kit/` — now copied into the repo. Once you've verified the repo copies, delete or archive those scratch originals so there's a single home.
