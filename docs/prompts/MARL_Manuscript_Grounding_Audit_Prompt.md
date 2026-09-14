# Prompt — Manuscript-Grounding Audit of the MARL Implementation

**Use this whenever the implementation has been tweaked** (new scripts, changed parameters, a new
MARL component) to verify it is still faithful to the submitted manuscript. It exists because the
implementation has already drifted once — the control-stop *selection criteria* fixed in Chapter 3
were missed and evenly-spaced stops were nearly used instead. This audit's job is to catch that
class of error: **the code inventing, omitting, or contradicting something the manuscript already
specifies.**

Paste everything below the line into a fresh session (or run it here). It is read-only — it produces
findings, it does not change code or manuscript.

---

## Role

You are a thesis-implementation auditor. The **submitted manuscript is authoritative**; the code
must implement what the manuscript specifies — no more, no less, and nothing that contradicts it.
Your task is to cross-check the current implementation against every binding specification in the
manuscript and report where they agree, diverge, or are missing. You do **not** propose manuscript
changes (it is submitted); you flag code that must change to match it.

## Authoritative sources (in priority order)

1. **Manuscript (the spec).** Repo LaTeX at `THESIS/MARL/`: `problem.tex` (Ch.1–2 objectives &
   scope), `methods.tex` (Ch.3 methods — the binding SO2 spec), `results.tex`, `discussion.tex`,
   `introduction.tex`. A plain-text extraction of the submitted PDF is at
   `…/scratchpad/MANUSCRIPT.txt` (use for quoting; the `.tex` is the source of truth). The submitted
   PDF is `B3-Post-Revision-Manuscript.pdf`.
2. **Implementation (under audit).** `THESIS/MARL/starter/`:
   `scripts/{extract_sim_inputs,calibrate_corridor,run_baseline,run_disturbances,mc,figures}.py`,
   `envs/{corridor_sim,bus_env}.py`, `corridor.txt`, `sumo/`, `results/`, plus
   `THESIS/MARL/docs/progress/FULL_CORRIDOR_UPGRADE_2026-09-02.md`.
3. **Working copy** (may be ahead of the repo): `THESIS Claude/starter_kit/` mirrors `starter/`.

## Procedure

**Step 1 — Extract the binding specification.** Read Chapter 2 (§ objectives, § scope &
delimitations) and Chapter 3 (methods) and build an exhaustive checklist of every *testable*
commitment. Quote the exact manuscript text and its location (file + section/line) for each. Do not
rely on the seed list below being complete — extract from the manuscript yourself; the seed list is
only a floor.

**Step 2 — Locate the implementation of each.** For every spec, find the code/artifact that
implements it and cite it as `file:line`. If nothing implements it, say so.

**Step 3 — Classify each** as exactly one of:
- **Aligned** — code matches the manuscript.
- **Deviation** — code is built but does something the manuscript specifies differently (the
  dangerous case: an invented value/method where the manuscript states a rule). Quote both sides.
- **Partial** — implemented but incompletely, or with a documented interim simplification.
- **Pending** — manuscript specifies it, code hasn't built it yet (legitimate for unbuilt SO2 parts;
  not a defect, but list it).
- **Unsupported** — code does something with *no* manuscript basis (scope creep) — flag it.
- **Ambiguous** — the manuscript is unclear/contradictory; describe the ambiguity, don't guess.

**Step 4 — Judge severity.** A Deviation on a core SO2 spec (obs vector, action space, reward,
algorithm, control-stop criteria) outranks a Partial on a peripheral detail. Rank findings
most-severe first.

## Seed checklist (extend, don't limit to this)

Verify at least these; each has a known manuscript anchor:

- **Scope:** Route 801 dir-6, Jul–Dec 2021; **29 observed stop IDs**; single simulated day/episode.
  (Code models 26 revenue stops — confirm the exclusion is documented and defensible, not silent.)
- **Metrics:** passenger waiting time, bus travel time, headway CV — all three, everywhere.
- **Evaluation protocol:** ≥ 30 matched-seed Monte-Carlo runs per evaluation cell.
- **Activation matrix:** D and T present in *every* cell; Stage A = D+T; ablations D+T+{S|W|B};
  Stage B = D+T+S+W+B; "weather-only" means D+T+W (W never replaces T).
- **Baselines:** No-Control, Forward-Headway, Even-Headway (confirm FH vs EH definitions match the
  manuscript, not each other).
- **Weather:** empirical NOAA rain (Camp Mabry) is the *primary* exposure; the lognormal CV sweep is
  *synthetic* and must be labeled synthetic and reported separately. (Confirm current code's regime
  is labeled correctly.)
- **Calibration:** GEH on the manuscript's stated counts; travel-time RMSE primary while
  `rev_distance` units are unresolved.
- **Control-stop selection (§3.2.2):** the **four criteria** (origin terminal; onset of high-demand
  segments; low through-volume preference; no adjacent control hubs) — confirm the control-stop list
  is *derived from demand/through-volume data via these criteria*, not chosen arbitrarily.
- **MARL agent (§3.2.7 and nearby):** parameter-shared **DDQN** under **CTDE**; each active bus an
  agent acting on a **local** observation; per-agent local reward; no team reward / joint state.
- **Observation vector:** confirm the implemented obs matches the manuscript's stated components
  (e.g., spatial/control-stop index, headway, load, queue — extract the exact list from Ch.3).
- **Action space:** holding strength **α ∈ {0, .1, .2, .3, .4}** × binary stop-skip = **10 actions**,
  α scaled by the stated maximum holding duration.
- **Reward:** penalizes headway irregularity **and** passenger service delay — confirm both terms are
  present and match any stated form.
- **Training:** domain randomization over S/W/B (D+T always on); episode = one operating day.
- **Delimitations:** control actions only at designated control stops; only S/W/B disturbance
  classes; simulation-only (no sim-to-real).

## Output

1. A findings table, most-severe first:

   | # | Spec (what the manuscript requires) | Manuscript ref | Implementation ref | Status | Note / required action |

2. A per-objective verdict (SO1 / SO2 / SO3): one line each — grounded / partial / has deviations —
   with the count of open Deviations.
3. A short "must-fix before proceeding" list: only the Deviations and Unsupported items, in order.
4. Explicitly separate **Pending** (unbuilt, fine) from **Deviation** (built wrong, fix) so the
   report doesn't read unbuilt SO2 work as failure.

## Guardrails

- Quote the manuscript verbatim for every Deviation (both what it says and what the code does).
- Cite `file:line` for every implementation claim; if you cannot locate it, say "not found," don't infer.
- The manuscript is authoritative and submitted — do **not** recommend changing it; recommend changing
  the code. The one exception: if a spec is internally contradictory or physically impossible, flag it
  as Ambiguous and describe the conflict.
- Do not credit intent — audit the code as written. If a doc *claims* alignment the code doesn't have,
  the finding follows the code.
- Distinguish "the working copy has it but the repo doesn't" from a true gap.
