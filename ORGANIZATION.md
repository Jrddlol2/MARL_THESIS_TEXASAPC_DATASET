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
| `MARL/` | the repo (canonical). The raw APC file lives at `data/raw/capmetro/APC_Raw_July_2021_December_2021_full.csv` |
| `RRW/` | canonical RRL source PDFs (50), referenced by `MARL/RRL/sources.md` |
| `archive/` | organized, dated, reversible — see below |

*Updated 2026-09-13:* the top-level `APC_Raw_*.csv` (byte-identical to the repo copy) moved to
`archive/duplicates/`, and `_backups/` moved to `archive/backups/2026-09_repo_snapshots/`. Both are safe to delete.

### `THESIS/archive/` (kept, not deleted)
`edsa-simulation/` (pre-pivot EDSA/Manila SUMO data) · `old-manuscript-repos/` (old clones) · `backups/` · `old-drafts/` · `docx-audits/` (8 working `.docx`) · `snapshots/` (`revised_2026-08-25/26`) · `duplicates/` (dup assets) · `references-old/` (`RTC_COMPLIANCE…`, `RRW-partial-old`) · `scratch/` (`tmp`). Each has a `_WHATIS.txt`.

## Checkpoint (frozen)
`MARL/submissions/2026-08-29_proposal-revision_AS-SUBMITTED/` — the exact manuscript + conformity PDFs as submitted 2026-08-29. **Do not edit or move.** Later edits happen in the `.tex` sources.

## Conventions
ISO dates (`YYYY-MM-DD`), clear prefixes (`roadmap_`, `audit_`, `prompt_`), no spaces in new folder names, one canonical home per file.

## Follow-ups (both done 2026-09-13)
1. **Commit:** done; later work is committed on `session-update`.
2. **De-dup:** `THESIS Claude/` is reorganized into `1_MSA1_current/`, `2_reports/`, `3_prompts/`, `4_member_prep/`,
   `tools/` and `_archive/` (see its `README.md`). Files already in this repo, and the retired `starter_kit/`,
   are in `THESIS Claude/_archive/`.
