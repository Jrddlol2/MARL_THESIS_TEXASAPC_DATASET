# AUDIT TRAIL (READABLE) — Group B3 Thesis Manuscript Changes
# Plain-English companion to AUDIT_TRAIL.md. Same entries, same order, same
# before/after content — but LaTeX markup stripped out (\cite{} → (Author,
# Year), \ref{}/\label{} → plain section/table names, math mode → words,
# \textbf{}/\textit{} → plain text) so the actual sentences are easy to read
# and easy to reuse when rewriting or discussing ideas.
#
# Format: every entry has a bold standalone **BEFORE** subtitle followed by
# its paragraph, then a bold standalone **AFTER** subtitle followed by its
# paragraph — skim the bold labels alone to see where something changed,
# then read the paragraph under it for what changed. Within the AFTER
# paragraph, the part that's actually new/different is **bolded**;
# unchanged surrounding text stays plain so your eye goes straight to the
# change.
#
# This file is NOT what goes into Overleaf — for the compilable LaTeX, use
# AUDIT_TRAIL.md. This file is for reading, discussing, and drafting.
# Keep both in sync: whenever AUDIT_TRAIL.md gets a new entry, add the same
# entry here in this BEFORE/AFTER format.

---

## 2026-08-06 — E1C3 — problem.tex, Section 2.2 (Research Gap)

**BEFORE**
...it cannot be determined whether reported MARL gains persist, degrade gracefully, or collapse under realistic operating disturbances, which in turn blocks the transition of MARL bus scheduling from simulation to real urban transit deployment.

**AFTER**
...blocks the transition of MARL bus scheduling from simulation to real urban transit deployment. **The weather-disturbance class (W) in particular was identified through the literature survey conducted earlier in this study (the "MARL Applied to Bus Scheduling" section), which found that no prior MARL bus-scheduling paper models heavy-tailed weather-induced travel-time delays (see the W column of the MARL literature table). Its operational relevance to the EDSA corridor is established by the rainfall-driven reductions in average speed and free-flow capacity documented in Section 1.1 (TSSP Rain 2018) and by the typhoon-related service suspensions on record for the corridor (DOTr 2020). The lognormal parameterization for this disturbance class follows the Kolmogorov-Smirnov-validated form from Patil et al., introduced here to address the resulting lack of temporally aligned, corridor-specific anomaly data (the "Disturbance Gap" section).**

**Why:** RTC comment 3 — the research gap section should explain how the weather disturbance column was arrived at.

---

## 2026-08-06 — E2C6 — introduction.tex 1.2.1, methods.tex Baseline Controllers

**BEFORE (introduction.tex)**
...allowing small headway perturbations to amplify into bunching (Daganzo 2009). Static schedules therefore remain mathematically inadequate for stochastic traffic environments, where the governing quantities are random variables rather than deterministic constants. These limitations motivated the transition toward more adaptive and data-driven scheduling methodologies.

**AFTER (introduction.tex)**
...random variables rather than deterministic constants. **Under the specific non-ideal conditions this study targets, the failure modes differ by control strategy. A fixed timetable has no feedback mechanism at all, so once bunching begins nothing in the schedule corrects it. A local reactive rule that holds a bus based only on the gap to the bus ahead can partially correct bunching under ordinary congestion, but has no way to respond to a breakdown, since it observes only the forward gap and not the enlarged gap a failed bus leaves behind it. A more globally aware reactive rule that accounts for both the forward and backward gap improves on this, but still follows a fixed, pre-specified rule rather than a learned response, so it cannot adapt its behavior to the heavier-tailed delays that severe weather introduces.** These limitations motivated the transition toward more adaptive and data-driven scheduling methodologies.

**BEFORE (methods.tex, No Control subsection, excerpt)**
...NC also provides the reference point for measuring the severity of bus bunching.

**AFTER (methods.tex, No Control subsection, excerpt)**
...the reference point for measuring the severity of bus bunching. **Under non-ideal conditions, NC has no corrective mechanism whatsoever, so demand surges, weather-induced delays, and breakdowns are expected to compound directly into bunching with no attenuation.**

*(Similar one-sentence additions were made to Forward Headway and Even Headway's subsections — FH can't see the backward gap a breakdown creates; EH has no way to anticipate weather's heavy-tailed delays.)*

**Why:** RTC comment 6 — explain how traditional non-AI scheduling performs under bunching/weather/breakdowns.

---

## 2026-08-06 — E2C7 — methods.tex, Section 3.2.10

**BEFORE**
The acceptance criterion is twofold: (i) mean passenger waiting time no worse than Even Headway (no statistically significant degradation at p < 0.05 with multiple-comparison correction), and ideally a statistically significant improvement; and (ii) a statistically significant reduction in headway coefficient of variation relative to No Control. *(written as one sentence buried inside a longer paragraph)*

**AFTER**
**Same two criteria, pulled out into a labeled, itemized callout box titled "Stage A acceptance criterion":**
**(i)** Mean passenger waiting time no worse than Even Headway...
**(ii)** A statistically significant reduction in headway coefficient of variation relative to No Control.
*(Stage B's criterion got the same treatment — pulled into its own "Stage B acceptance criterion" callout, wording unchanged.)*

**Why:** RTC comment 7 — describe what successful performance will look like, make it more visually prominent. No new thresholds were invented — only reformatting.

---

## 2026-08-06 — E3C12 — introduction.tex, Section 1.2.3 (after Figure 1.3)

**BEFORE**
*(nothing — Figure 1.3's caption was immediately followed by the next paragraph, which started:)* "Multi-Agent Reinforcement Learning (MARL) addresses the three limitations above..."

**AFTER**
**A new paragraph inserted right after Figure 1.3: "In both panels of Figure 1.3, the per-bus state (the same thing methods.tex calls s_i,t in its formal notation, shown in the figure as the local observation o_i) encodes the bus's current position, forward and backward headways, onboard load, and queue length at its current stop, as defined in full in the State Space section. The action is the holding-strength and stop-skipping decision the controller emits for that bus, defined in the Action Space section. In the SARL panel (a), a single centralized network ingests all N per-bus state vectors concatenated into one global state and outputs all N actions simultaneously; in the MARL panel (b), the same shared network weights instead process each bus's local state independently, so each agent acts on only its own observation rather than the concatenated global one."**
Then unchanged: "Multi-Agent Reinforcement Learning (MARL) addresses the three limitations above..."

**Why:** RTC comment 12 — explain the concepts in Figure 1.3 (bus states and actions).

---

## 2026-08-06 — E3C13 — introduction.tex Section 1.1, methods.tex Section 3.2.3

**BEFORE (introduction.tex)**
...empirical studies on Philippine expressways show that increasing rainfall intensity significantly reduces average traffic speed and free-flow capacity (TSSP Rain 2018).

**AFTER (introduction.tex)**
...reduces average traffic speed and free-flow capacity (TSSP Rain 2018). **This rainfall-impact evidence is drawn from a 2018 study of the North Luzon Expressway rather than the EDSA Busway, and is used here only as contextual motivation that weather materially affects Philippine road-traffic operations; the weather-disturbance generator in this study does not adopt this study's specific speed-reduction percentages, and EDSA-specific travel-time behavior is independently calibrated through the GEH/RMSE procedure described in Section 3.2.3.**

**BEFORE (methods.tex, Environment Model Validation opening)**
...The calibration is restricted to the bus corridor itself, since the agents' state and reward depend only on bus dynamics; surrounding mixed-traffic flows do not enter the Python environment.

**AFTER (methods.tex, Environment Model Validation opening)**
...surrounding mixed-traffic flows do not enter the Python environment. **This GEH/RMSE procedure calibrates EDSA-specific parameters directly from EDSA operational data and does not depend on the North Luzon Expressway rainfall-impact figures cited as motivating evidence in Section 1.1; that citation establishes only that weather materially affects Philippine road-traffic operations in general, not any EDSA-specific speed or capacity value used in this calibration.**

**Why:** RTC comment 13 — Reference [10] is both dated (2018) and a different corridor (North Luzon Expressway, not EDSA); clarify whether its data was adopted or independently tuned for EDSA. This version fixes an earlier draft that only addressed the corridor-mismatch half, missing the "not quite new" recency half — caught during the cross-check against the verbatim RTC letter.

---

## 2026-08-06 — E3C8 — methods.tex, Section 3.2.6

**BEFORE**
The "Stochastic Disturbance Generators" section opened straight into: "Four stochastic generators inject variability into the Python environment. Generators (i) and (ii) follow the perturbation framework of Wang and Sun; the weather generator's heavy-tailed lognormal formulation follows Patil et al.; the breakdown generator follows the rescheduling formulation of Cao et al. Table 3.1 collects the symbols used across this section and the MARL formulation that follows." *(no explicit definitions of the disturbance classes came first)*

**AFTER**
**A new "Disturbance Classes and Independence" block was inserted before that paragraph, defining five disturbance classes as a bulleted list:**
- **Stochastic demand (D):** the baseline, always-present day-to-day randomness in passenger arrivals... D is not a disturbance layered on top of a deterministic baseline — it IS the baseline stochastic environment.
- **Demand surge (S):** an episode-level scaling factor that amplifies baseline boarding rates above their empirical mean. S is the controlled experimental variable; D is always present, and S is added on top of it.
- **Traffic-speed perturbation (T):** an episode-level scaling of corridor cruising speed, representing everyday congestion friction.
- **Weather-induced delay (W):** a per-segment travel-time distribution drawn from a right-skewed lognormal. W replaces T once the weather intensity parameter exceeds zero.
- **Discrete bus breakdown (B):** a Poisson-distributed discrete event that permanently removes one bus from the active agent set.

**Followed by a paragraph stating the four generators (S, T, W, B) are injected independently with no causal chain — a breakdown doesn't trigger a demand surge or weather delay, and a weather event doesn't cause a mechanical failure — while acknowledging some disturbances do co-occur causally in reality, but this study treats each as independent to isolate individual and combined effects.**

Then unchanged: "Four stochastic generators inject variability... Table 3.1 collects the symbols..."

**Why:** RTC comment 8 — define each disturbance explicitly, clarify independence, distinguish stochastic demand from demand surge.

---

## 2026-08-06 — E3C15 — methods.tex, Section 3.2.4 (end)

**BEFORE**
Section 3.2.4 ended with "...A condition is a state of the world; a controller is a choice of algorithm." and moved straight into the "Data Processing" section. *(no summary table of simulation parameters existed anywhere)*

**AFTER**
**A new table titled "Simulation parameter summary: fixed, swept/variable, and derived parameters" was inserted, with three groups:**
- **Fixed:** simulation horizon (hours TBD), stop count (24, reused from Section 1.2.2), fleet size (~12-30, same source), control stop count (TBD), scheduled headway (TBD), bus capacity (TBD), max holding duration (TBD), holding bins ({0.0, 0.1, 0.2, 0.3, 0.4}), action space size (10), Monte Carlo runs (≥30), discount parameters (TBD).
- **Swept/variable:** weather intensity ({0.0, 0.3, 0.6, 1.0, 1.3}), demand scaling clip ([1,3]), traffic-speed scaling clip ([0.8, 1.2]), breakdown rate (TBD).
- **Derived (from SUMO calibration):** baseline travel time and its std dev (both TBD), baseline coefficient of variation (TBD), lognormal shape/location parameters (computed via formulas already given).

Then unchanged: "...moved into Data Processing."

**Why:** RTC comment 15 — summarize fixed and variable simulation parameters with target values.

---

## 2026-08-06 — E4C20 — methods.tex, Section 3.2.6 (four generator subsections)

Added one implementation-mechanics sentence to each of the four disturbance generator descriptions, explaining exactly *when* the random value is sampled and *how* it's applied.

**Passenger Demand — AFTER (added sentence):**
**"In implementation, the scaling factor is sampled once per episode at initialization and applied uniformly to every per-stop, per-time-of-day arrival rate for the duration of that simulated operating day, so all stops experience the same proportional demand shift within a single run while the shift itself varies across runs."**

**Traffic Delays — AFTER (added sentence):**
**"In implementation, the speed scaling factor is sampled once per episode and applied to the bus's mean cruising speed on every inter-stop segment traversal during that day, producing a uniformly slower or faster corridor for that run without segment-level variation beyond the calibrated baseline."**

**Weather-Induced Anomalies — AFTER (added sentence):**
**"In implementation, when the weather intensity parameter is greater than zero, a fresh travel-time sample is drawn independently for each bus at each inter-stop segment traversal during the episode, replacing the traffic-speed generator's output for that traversal; the lognormal parameters are computed from the segment's empirical mean and the swept intensity value via the method-of-moments equations given earlier."**

**Bus Breakdowns — AFTER (added sentence):**
**"In implementation, at each discrete simulation timestep, a Bernoulli trial (a weighted coin flip) with probability lambda times the timestep length is evaluated independently for each active bus; a 'heads' removes that bus from the active agent set for the remainder of the simulated day."**

**Why:** RTC comment 20 — explain in detail how each disturbance scenario is actually simulated. (BEFORE in each case: the paragraph described what the generator represents statistically, but never said when/how the sampling actually happens during a run — that's exactly what each added sentence fills in.)

---

## 2026-08-06 — E4C21 — methods.tex, Sections 3.2.9 and 3.2.7

**BEFORE (3.2.9 opening)**
"For each (control strategy, disturbance level) cell, at least 30 independent Monte Carlo runs are executed using matched random seeds across strategies. Three response variables are logged per run: mean passenger waiting time, mean total travel time, and headway coefficient of variation." *(no formal definition of what those three metrics actually mean)*

**AFTER (3.2.9 opening)**
**New opening added, defining each metric formally:**
- **Mean passenger waiting time:** the average time from a passenger's arrival at a stop to their successful boarding, averaged across all passengers and stops over one simulated day.
- **Mean total travel time:** the average elapsed time from a bus's departure from the origin terminal to its arrival at the final stop, averaged across all completed trips.
- **Headway coefficient of variation:** standard deviation of inter-bus headways divided by their mean. Zero means perfectly regular; larger means worse bunching. Mirrors the same coefficient-of-variation definition already used for travel time elsewhere in the chapter.

Then unchanged: "...at least 30 Monte Carlo runs are executed..."

**BEFORE (3.2.7 State Space, end of bullet list)**
The observation-vector bullet list ended, then jumped straight to the "Action Space" subsection.

**AFTER (3.2.7 State Space, end of bullet list)**
**A new table "Agent observation vector: features, symbols, and data sources" inserted, listing 7 features (control stop index, forward/backward headway, onboard count, waiting count, disturbance flag, breakdown flag) with two columns: what real-world sensor supplies it in deployment (AVL feed, APC system, AFC terminal, weather API, incident system) vs what supplies it in simulation (hardcoded list, event-driven bus model, generator parameter, etc.). Closing sentence: all simulated features are synthetic — no real sensor data used during training/evaluation.**
Then unchanged: "Action Space" subsection begins.

**Why:** RTC comment 21 — include details on the metrics and description of observation features.

---

## 2026-08-06 — E1C1+E2C5+E4C22 — REVERTED, no net change

**DRAFTED (mid-session, never committed)**
A "Dataset Description" section describing SafeTravelPH as a crowdsourced GPS-trajectory mobile app, its July 2023 EDSA Busway collection window, and its per-trip record structure — plus a 6-row table mapping dataset fields to their roles in calibration, and a closing sentence about the secondary DOTr FOI ridership source. All specific numbers used TODO-DATA placeholders correctly.

**REVERTED TO (final, pushed state — identical to original)**
The section reads exactly as it did before this session started: the "Corridor bus operational data" bullet flows straight into "Severe-weather conditions are not estimated from operational data in this study..." — no dataset description paragraph, no field table.

**Why reverted:** The user caught this before any commit: the group doesn't actually have access to the SafeTravelPH dataset yet, and even though the numbers were placeholder-tagged, the *qualitative* description (what kind of app it is, how its records are structured) asserted more familiarity with the dataset than is currently honest. Full detail in TRACKER.md.

---

## 2026-08-06 — Citation fix: Patil2025Conformal — methods.tex, Section 3.2.6

**BEFORE**
"Patil et al. validated this parameterization against **INRIX freeway data** via the Kolmogorov-Smirnov test, reporting a close fit at the highest variability level they tested (KS = 0.036, p = 0.94 at CV = 1.0)."

**AFTER**
"Patil et al. **tested this parameterization by generating SUMO-simulated travel times under the same CV-driven lognormal recipe — with time windows and mean travel times anchored to INRIX historical data for an urban arterial corridor, not a freeway — and confirming via the Kolmogorov-Smirnov test that the simulated distribution matches the assumed log-normal shape**, reporting a close fit at the highest variability level they tested (KS = 0.036, p = 0.94 at CV = 1.0)."

**Why:** Checked against the actual paper. Its own Table V classifies the test route as "Local, Minor/Principal Arterials" — not a freeway. Also, the KS test checks whether SUMO-simulated travel times follow the assumed log-normal shape; it isn't a direct comparison against INRIX's own data. The numeric KS/p values themselves were confirmed correct — only the description of what was tested and against what changed.

---

## 2026-08-06 — Citation fix: Rodriguez2023Cooperative — methods.tex, Section 3.2.7

**BEFORE**
"...A continuous holding parameter was considered but rejected for three reasons. First, continuous actions require actor-critic algorithms with training instability. Second, **Rodriguez et al. showed that a 5-bin discretization achieves combined holding-and-skipping control on a comparable corridor without measurable loss of performance versus continuous formulations.** Third, real driver compliance with second-level holding instructions is itself coarse, so continuous precision is not meaningful at deployment."

**AFTER**
"...**This study's action space (10 discrete actions: 5 holding strengths × 2 skip choices, selected independently) is broader than Rodriguez et al.'s combined holding-and-skipping controller, which instead selects among 6 mutually exclusive actions: 5 holding strengths (where zero-strength already covers 'no holding') plus a single separate skip action. The same 5-value holding-strength set is used in both studies.** A continuous holding parameter was considered but rejected for two reasons: continuous actions require actor-critic algorithms with training instability, and **real driver compliance with holding instructions is itself imperfect — Rodriguez et al. model non-compliant drivers as executing only 60-80% of the instructed holding time** — so continuous precision isn't meaningful at deployment anyway."

**Why:** Checked against the full paper — no comparison against a continuous action space exists anywhere in it; that claim (bolded, removed above) was unsupported. Rodriguez's actual action space is a 6-way mutually exclusive choice, not a 10-way independent combination like this thesis's own design — corrected to reflect that difference honestly, while keeping this thesis's own 10-action design unchanged.

---

## 2026-08-06 — Citation fix: Wangsun — methods.tex, Section 3.2.6

**BEFORE**
"...perturbed each episode by a scaling factor..., clipped to [1, 3], following Wang and Sun. ...The upper bound of 3 corresponds to roughly a tripling of baseline boarding rates, **spanning the range observed during major event let-outs and severe-weather mode shifts.**"

**AFTER**
"...clipped to [1, 3], **following the general Gaussian-clipped demand-scaling mechanism of Wang and Sun, though this study adopts a narrower clip than their [1, 10] range.** ...The upper bound of 3, corresponding to roughly a tripling of baseline boarding rates, **is this study's own choice (flagged to revisit against Wang and Sun's wider range during implementation) rather than a value drawn from prior work.**"

**Why:** Checked against the actual paper. Their own equation clips the demand-scaling factor to [1, 10], not [1, 3] — and the "event let-outs" justification for the number 3 doesn't appear anywhere in their paper either. Kept the study's own [1, 3] choice (changing it would be a real experimental redesign, not a citation fix) but stopped implying that specific number came from Wang and Sun.

---

## 2026-08-06 — E3C9 + E2C4 — introduction.tex, after Section 1.2.2 (SARL)

**BEFORE**
The SARL limitations section ended with a paragraph about SA-DRL's competitive results, then jumped straight to the Multi-Agent RL section.

**AFTER**
**New introductory sentence:** "To situate the MARL literature reviewed next within the broader ML and SARL landscape, [this table] extends the paradigm comparison from Table 1.1 with a disturbance-coverage column, using the same D/S/T/W/B notation as the main MARL comparison table."

**New table, "Disturbance coverage across ML and SARL vehicle-scheduling studies":**
| Paper | Paradigm | Method | Disturbances |
|---|---|---|---|
| Wang et al. | ML (data-driven) | Bus scheduling incorporating time-dependent traffic and demand | D |
| Barrera Hernandez et al. | ML-assisted (heuristic dispatcher) | Passenger-demand forecasting supporting a heuristic dispatcher | D |
| Zhao et al. | SARL | STDH-DQN; self-attention state encoder over spatial-temporal AVL features | D, T |
| Zhang and Zheng | SARL | SA-DRL; categorical identity features | D, T |
| Verbich and El-Geneidy | Heuristic (non-MARL) | Dynamic transit control under severe weather and vehicle breakdowns | W, B |

**New closing paragraph:** "The funnel is now complete: no ML or SARL study covers W or B, and among MARL studies, only Verbich and El-Geneidy's heuristic controller addresses both — and it's explicitly non-MARL. Patil et al. similarly validate weather-induced travel-time distributions but don't address bus control at all; their contribution here is the lognormal parameterization for the weather generator, not a bus-control baseline. No prior study — ML, SARL, or MARL — combines W and B coverage with an actual MARL bus-scheduling controller, which is the specific gap this study fills."

**Why:** RTC comment 9 (asks for an ML/SARL disturbance table) and comment 4 (asks for a severe-weather comparison study) — solved together, since Verbich & El-Geneidy is exactly what comment 4 wants and fits naturally as a row here.

---

## 2026-08-06 — E3C10 — introduction.tex, before Table 1.2 discussion

**BEFORE**
The paragraph right before the Table 1.2 summary jumped straight into: "Table 1.2 summarizes what each study evaluated, what disturbances it modeled, and what it reported."

**AFTER**
**New paragraph added right before that:** "Only Shi et al. carries a breakdown (B) entry in Table 1.2. Cao et al., who also model discrete vehicle failures, are deliberately excluded from this count: their MARL application is to train rescheduling, not bus scheduling, so they don't belong in a table scoped to MARL bus-control literature. Verbich and El-Geneidy likewise model breakdowns but use heuristic, non-MARL control (see the new ML/SARL table), so they're excluded for the same reason. Among MARL bus-scheduling studies specifically, Shi et al. remains the only one to model discrete breakdowns."
Then unchanged: "Table 1.2 summarizes what each study evaluated..."

**Why:** RTC comment 10 — the table shows only one breakdown paper but the presentation reportedly showed two. Couldn't confirm what was actually shown (no slide access), so used the RTC letter's own suggested fallback: explain why the two "candidate" second papers are correctly excluded, rather than guessing at an unverified row.

---

## 2026-08-06 — E3C11 — figure caption attribution (introduction.tex, methods.tex)

**BEFORE**
7 original diagrams (Figures 1.3, 1.4, 3.1–3.5) had captions ending in plain description with no source note.

**AFTER**
**Each caption now ends with "Authors' illustration."** added after the existing description — nothing else in any caption changed.

Figures 1.1 and 1.2 already had proper citations (DOTr ridership data, TSSP rainfall study) and were left as-is.

**Why:** RTC comment 11 — some figures lack citations; original diagrams should say so explicitly rather than looking uncredited.

---

## 2026-08-06 — E3C14 — problem.tex, Delimitations (a)

**BEFORE**
"(a) Due to computational constraints, the simulation is restricted to a defined operational sub-segment of the EDSA Carousel corridor rather than the entire metropolitan road network. The restriction is justified by the need to preserve 1:1 empirical traffic volumes for GEH calibration without resorting to flow scaling; corresponding GEH calibration statistics are reported in Chapter 4."

**AFTER**
"(a) Due to computational constraints, the simulation is restricted to a defined operational sub-segment of the EDSA Carousel corridor rather than the entire metropolitan road network, **and minor feeder roads leading into the corridor are not modeled. Both restrictions are justified by the same structural fact: the EDSA Carousel operates on a physically separated, barrier-protected busway, so the agents' state and reward depend only on bus dynamics within the dedicated lane — specifically headways, dwell times, and onboard loads — none of which are directly observed by or computed from feeder-road traffic. Feeder roads affect the corridor only indirectly, through the passenger arrival rates they produce at each stop, and that effect is already captured by the calibrated per-stop demand distributions without needing to simulate the feeder network itself. Modeling feeder roads in SUMO would add computational cost without adding any new information the agents' observation or reward could use, since** the sub-corridor restriction also preserves 1:1 empirical traffic volumes for GEH calibration without resorting to flow scaling; corresponding GEH calibration statistics are reported in Chapter 4."

**Why:** RTC comment 14 — explain why minor roads leading to the corridor are excluded from the simulation.

---

## 2026-08-06 — E3C16 — figure/table callout sweep (introduction.tex, methods.tex)

Ten short additions, each linking an existing sentence to a figure/table that was never explicitly named anywhere in the prose:

| Location | Before | After |
|---|---|---|
| Ridership stat (intro) | "...up from 63.02M in 2024." | "...up from 63.02M in 2024 **(Figure 1.1)**." |
| Rainfall stat (intro) | "The reduction in average speeds are about 5.34%..." | "**As Figure 1.2 shows,** the reduction in average speeds are about 5.34%..." |
| CTDE intro (intro) | "...use Centralized Training with Decentralized Execution (CTDE)." | "...use CTDE, **illustrated in Figure 1.4**." |
| Pipeline intro (methods) | "The pipeline proceeds in two phases." | "**As shown in Figure 3.1,** the pipeline proceeds in two phases." |
| GEH statistic (methods) | "...measures the discrepancy...on individual corridor segments:" | "...measures the discrepancy...**illustrated in panel (a) of Figure 3.2**:" |
| RMSE (methods) | "RMSE evaluates how closely simulated bus speed trajectories match empirical observations:" | "...match empirical observations, **illustrated in panel (b) of Figure 3.2**:" |
| Parameter table close (methods) | "Parameters marked TODO-VAL are to be confirmed..." | "**Table 3.2 therefore serves as the single reference point for every parameter used across this chapter.** Parameters marked TODO-VAL..." |
| Observation features (methods) | "In simulation, all observation features are generated synthetically..." | "**As Table 3.3 shows,** in simulation all observation features are generated synthetically..." |
| Training loop (methods) | "The learning process follows the standard RL feedback loop..." | "...follows the standard...feedback loop..., **illustrated in Figure 3.3**." |
| Stage A (methods) | "...are each run for ≥30 Monte Carlo iterations with matched seeds." | "...matched seeds, **reported in the format shown in Figure 3.4**." |
| Stage B (methods) | "...with the breakdown generator active at each level." | "...active at each level, **using the Monte Carlo evaluation procedure illustrated in Figure 3.5**." |

**Why:** RTC comment 16 — figures and tables should be called and discussed in the paragraphs, not just placed. Found 10 with zero references despite adjacent topical discussion; added one reference each without touching the discussion itself. Table 3.1 (the notation table) — the RTC's own example of a too-thin callout — was checked and already has 5 separate substantive references elsewhere in the chapter, so no fix was needed there.

---

## 2026-08-06 — E3C18 + E3C19 — main.tex preamble

**BEFORE**
`setspace` package not loaded. `\onehalfspacing` not called. `lineno` package already loaded, but `\linenumbers` was commented out.

**AFTER**
**Added `\usepackage{setspace}` to the preamble. Added `\onehalfspacing` right after `\begin{document}`. Uncommented `\linenumbers`.** Everything else in the preamble is unchanged.

**Why:** RTC comments 18 and 19 — 1.5 line spacing and line numbers for the non-final manuscript. Applied last, after all other content edits in this revision round, per CLAUDE.md's own guidance to avoid disrupting line references mid-revision.

---

## 2026-08-06 — E1C2 — methods.tex, Section 3.2.5 (end)

**BEFORE**
The "Required Datasets" bullet list (GPS location, boarding/alighting events, occupancy, speed, dwell time) ended, then jumped straight to "Severe-weather conditions are not estimated from operational data..."

**AFTER**
**New table inserted, "Mapping of required raw dataset fields to derived parameters and their role in the MARL formulation":**
| Raw Field | Derived Parameter | MARL Component |
|---|---|---|
| GPS-tracked vehicle location | Per-segment travel-time distribution | SUMO speed calibration; anchors traffic-speed and weather generators |
| Boarding events | Per-stop demand rate | Demand-surge generator baseline; waiting-count observation feature |
| Alighting events | Through-passenger volume per stop | Control-stop selection criterion 3 (avoid high through-volume stops) |
| Passenger occupancy | Per-segment load profile | Onboard-count observation feature; dwell-time estimation |
| Operating speed | Per-segment cruising speed | SUMO volume calibration; traffic-speed generator baseline |
| Dwell time | Per-stop dwell distribution | Event-driven bus model, advances the simulation clock |

**Preceded by a sentence noting this reflects design intent, not properties of a dataset the group has actually processed.**
Then unchanged: "Severe-weather conditions are not estimated from operational data..."

**Bug caught while drafting:** one of the new cross-references initially pointed at the wrong section (the data pre-processing pipeline instead of control-stop selection, which didn't have a label yet). Added the missing label and fixed both references before finalizing.

**Why:** RTC comment 2 — map dataset fields to the study's proposed features. Judged safe without dataset access, since it connects two things already spelled out elsewhere in the manuscript (required fields, MARL components) rather than describing the dataset itself.

---

## 2026-08-06 — E3C17 — introduction.tex (Background), methods.tex (Weather-Induced Anomalies)

**BEFORE**
The corridor was described in prose only, with no map figure. The Introduction had two figures (ridership, rainfall impact). The η disturbance-intensity sweep values were explained in prose only, no table.

**AFTER**
**Added a new figure right after the ridership figure: the EDSA Carousel corridor map** (Monumento to PITX route with jeepney/MRT/LRT/tricycle/UV-FX transport-mode legend at each stop), extracted from the group's defense presentation. **Added a new table right after the existing η-sweep prose in methods.tex**, listing each η value (0.0, 0.3, 0.6, 1.0, 1.3) alongside its basis (generator off / inside Patil et al.'s validated range / top of validated range / extrapolated stress test) — the existing prose explaining this was kept unchanged, the table just gives readers a quick-reference version.

**Why:** RTC comment 17 — include figures/tables shown in the defense but missing from the manuscript. All 58 slides of the defense deck were reviewed against the manuscript; most content (SARL vs MARL, CTDE, calibration formulas, parameter notation, training-vs-execution protocol) duplicated what's already written — adding it again would just repeat existing material. These two were the genuinely new items. The corridor map specifically matches the example the RTC letter itself gave for what might be missing.

**Judged out of scope, not added:** Work Plan Gantt charts (project timeline, not manuscript content) and a software/tools appendix (SUMO, PettingZoo, PyTorch, etc. — implementation detail for later, not this revision round).

**Important:** this repo doesn't have a `Figures/` folder for any of the existing images — they live only on Overleaf. A `Figures/` folder was created locally just to hold the new map image. **The user needs to upload `bg_fig3_edsa_corridor_map.pdf` to Overleaf's Figures folder too**, or the new figure won't show up when compiled there.

---

*Nothing follows.*
