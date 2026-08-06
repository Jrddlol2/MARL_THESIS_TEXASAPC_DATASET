# AUDIT TRAIL (READABLE) — Group B3 Thesis Manuscript Changes
# Plain-English companion to AUDIT_TRAIL.md. Same entries, same order, same
# before/after content — but LaTeX markup stripped out (\cite{} → (Author,
# Year), \ref{}/\label{} → plain section/table names, math mode → words,
# \textbf{}/\textit{} → plain text) so the actual sentences are easy to read
# and easy to reuse when rewriting or discussing ideas.
#
# This file is NOT what goes into Overleaf — for the compilable LaTeX, use
# AUDIT_TRAIL.md. This file is for reading, discussing, and drafting.
# Keep both in sync: whenever AUDIT_TRAIL.md gets a new entry, add the same
# entry here in plain-text form.

---

## 2026-08-06 — E1C3 — problem.tex, Section 2.2 (Research Gap)

**Before:** The paragraph ended with: "...it cannot be determined whether reported MARL gains persist, degrade gracefully, or collapse under realistic operating disturbances, which in turn blocks the transition of MARL bus scheduling from simulation to real urban transit deployment."

**After:** Same ending, plus two new sentences: The weather-disturbance class (W) was identified through the literature survey done earlier in the thesis (the "MARL Applied to Bus Scheduling" section), which found that no prior MARL bus-scheduling paper models heavy-tailed weather-induced travel-time delays (see the W column of the MARL literature table). Its relevance to EDSA is backed by the rainfall-driven speed/capacity reductions from Section 1.1 (TSSP Rain 2018 study) and the typhoon-related service suspensions on record for the corridor (DOTr 2020). The lognormal parameterization for this disturbance class follows the Kolmogorov-Smirnov-validated form from Patil et al., introduced here to address the resulting lack of temporally-aligned, corridor-specific anomaly data (the "Disturbance Gap" section).

**Why:** RTC comment 3 — the research gap section should explain how the weather disturbance column was arrived at.

---

## 2026-08-06 — E2C6 — introduction.tex 1.2.1, methods.tex Baseline Controllers

**Before (introduction.tex):** "...allowing small headway perturbations to amplify into bunching (Daganzo 2009). Static schedules therefore remain mathematically inadequate for stochastic traffic environments, where the governing quantities are random variables rather than deterministic constants. These limitations motivated the transition toward more adaptive and data-driven scheduling methodologies."

**After (introduction.tex):** Same start and end, with this inserted in between: "Under the specific non-ideal conditions this study targets, the failure modes differ by control strategy. A fixed timetable has no feedback mechanism at all, so once bunching begins nothing in the schedule corrects it. A local reactive rule that holds a bus based only on the gap to the bus ahead can partially correct bunching under ordinary congestion, but has no way to respond to a breakdown, since it observes only the forward gap and not the enlarged gap a failed bus leaves behind it. A more globally aware reactive rule that accounts for both the forward and backward gap improves on this, but still follows a fixed, pre-specified rule rather than a learned response, so it cannot adapt its behavior to the heavier-tailed delays that severe weather introduces."

**Before (methods.tex, No Control subsection, excerpt):** "...NC also provides the reference point for measuring the severity of bus bunching."

**After (methods.tex, No Control subsection, excerpt):** Same, plus: "Under non-ideal conditions, NC has no corrective mechanism whatsoever, so demand surges, weather-induced delays, and breakdowns are expected to compound directly into bunching with no attenuation."

Similar one-sentence additions were made to the Forward Headway and Even Headway subsections, describing their own expected failure modes — Forward Headway can't see the backward gap a breakdown creates; Even Headway has no way to anticipate weather's heavy-tailed delays.

**Why:** RTC comment 6 — explain how traditional non-AI scheduling performs under bunching/weather/breakdowns.

---

## 2026-08-06 — E2C7 — methods.tex, Section 3.2.10

**Before:** The Stage A acceptance criterion was written as one sentence buried in a paragraph: "The acceptance criterion is twofold: (i) mean passenger waiting time no worse than Even Headway (no statistically significant degradation at p < 0.05 with multiple-comparison correction), and ideally a statistically significant improvement; and (ii) a statistically significant reduction in headway coefficient of variation relative to No Control."

**After:** Pulled the same two criteria out into a labeled, itemized callout box titled "Stage A acceptance criterion" — the wording of the two criteria is unchanged, just visually separated from the surrounding prose. Stage B's criterion sentence got the same treatment, pulled into a "Stage B acceptance criterion" callout. No new thresholds were invented — only reformatting.

**Why:** RTC comment 7 — describe what successful performance will look like, make it more visually prominent.

---

## 2026-08-06 — E3C12 — introduction.tex, Section 1.2.3 (after Figure 1.3)

**Before:** Nothing existed between Figure 1.3's caption and the next paragraph, which started: "Multi-Agent Reinforcement Learning (MARL) addresses the three limitations above..."

**After:** A new paragraph was inserted right after Figure 1.3: "In both panels of Figure 1.3, the per-bus state (the same thing methods.tex calls s_i,t in its formal notation, shown in the figure as the local observation o_i) encodes the bus's current position, forward and backward headways, onboard load, and queue length at its current stop, as defined in full in the State Space section. The action is the holding-strength and stop-skipping decision the controller emits for that bus, defined in the Action Space section. In the SARL panel (a), a single centralized network ingests all N per-bus state vectors concatenated into one global state and outputs all N actions simultaneously; in the MARL panel (b), the same shared network weights instead process each bus's local state independently, so each agent acts on only its own observation rather than the concatenated global one."

**Why:** RTC comment 12 — explain the concepts in Figure 1.3 (bus states and actions).

---

## 2026-08-06 — E3C13 — introduction.tex Section 1.1, methods.tex Section 3.2.3

**Before (introduction.tex):** "...empirical studies on Philippine expressways show that increasing rainfall intensity significantly reduces average traffic speed and free-flow capacity (TSSP Rain 2018)."

**After (introduction.tex):** Same sentence, plus: "This rainfall-impact evidence is drawn from a 2018 study of the North Luzon Expressway rather than the EDSA Busway, and is used here only as contextual motivation that weather materially affects Philippine road-traffic operations; the weather-disturbance generator in this study does not adopt this study's specific speed-reduction percentages, and EDSA-specific travel-time behavior is independently calibrated through the GEH/RMSE procedure described in Section 3.2.3."

**Before (methods.tex, Environment Model Validation opening):** "...The calibration is restricted to the bus corridor itself, since the agents' state and reward depend only on bus dynamics; surrounding mixed-traffic flows do not enter the Python environment."

**After (methods.tex, Environment Model Validation opening):** Same, plus: "This GEH/RMSE procedure calibrates EDSA-specific parameters directly from EDSA operational data and does not depend on the North Luzon Expressway rainfall-impact figures cited as motivating evidence in Section 1.1; that citation establishes only that weather materially affects Philippine road-traffic operations in general, not any EDSA-specific speed or capacity value used in this calibration."

**Why:** RTC comment 13 — Reference [10] is both dated (2018) and a different corridor (North Luzon Expressway, not EDSA); clarify whether its data was adopted or independently tuned for EDSA. This version fixes an earlier draft of the queue entry that only addressed the corridor-mismatch half, missing the "not quite new" recency half — caught during the cross-check against the verbatim RTC letter.

---

## 2026-08-06 — E3C8 — methods.tex, Section 3.2.6

**Before:** The "Stochastic Disturbance Generators" section opened straight into: "Four stochastic generators inject variability into the Python environment. Generators (i) and (ii) follow the perturbation framework of Wang and Sun; the weather generator's heavy-tailed lognormal formulation follows Patil et al.; the breakdown generator follows the rescheduling formulation of Cao et al. Table 3.1 collects the symbols used across this section and the MARL formulation that follows." — no explicit definitions of the disturbance classes came first.

**After:** A new block titled "Disturbance Classes and Independence" was inserted before that paragraph, defining five disturbance classes as a bulleted list:
- **Stochastic demand (D):** the baseline, always-present day-to-day randomness in passenger arrivals, drawn from the calibrated per-stop, per-time-of-day demand distributions. D is not a disturbance layered on top of a deterministic baseline — it IS the baseline stochastic environment, present in every run regardless of which other generators are active.
- **Demand surge (S):** an episode-level scaling factor (standard deviation sigma-d) that amplifies baseline boarding rates above their empirical mean. S is the controlled experimental variable; D is always present, and S is what's added on top of it. Setting sigma-d to zero removes the surge and leaves only baseline demand variability (D).
- **Traffic-speed perturbation (T):** an episode-level scaling of corridor cruising speed (standard deviation sigma-s), representing everyday congestion friction. T governs inter-stop travel-time variability under ideal conditions.
- **Weather-induced delay (W):** a per-segment travel-time distribution with coefficient of variation eta, drawn from a right-skewed lognormal rather than the Gaussian-based scaling used by T. W replaces T as the source of travel-time stochasticity once eta is greater than zero.
- **Discrete bus breakdown (B):** a Poisson-distributed discrete event, with rate lambda, that permanently removes one bus from the active agent set for the remainder of the simulated day.

Followed by a paragraph stating the four generators (S, T, W, B) are injected independently with no causal chain — a breakdown doesn't trigger a demand surge or weather delay, and a weather event doesn't cause a mechanical failure — while acknowledging that in reality some disturbances do co-occur causally (e.g., heavy rain both slowing buses and crowding shelters), but this study treats each as independent to isolate individual and combined effects, connecting to the single-disturbance ablation described later in Evaluation Methods.

**Why:** RTC comment 8 — define each disturbance explicitly, clarify independence, distinguish stochastic demand from demand surge.

---

## 2026-08-06 — E3C15 — methods.tex, Section 3.2.4 (end)

**Before:** Section 3.2.4 (Operating Conditions) ended with "...A condition is a state of the world; a controller is a choice of algorithm." and moved straight into the "Data Processing" section — no summary table of simulation parameters existed anywhere.

**After:** A new table titled "Simulation parameter summary: fixed, swept/variable, and derived parameters" was inserted, with three grouped sections:

*Fixed simulation parameters:* Simulation horizon (single operating day, exact hours still TBD), total stop count (24, reused from the SARL dimensionality discussion in Section 1.2.2), fleet size (approx. 12–30 buses, same source), control stop count (TBD, depends on the criteria in Section 3.2.2 once the dataset is processed), scheduled headway (TBD, from DOTr schedule), bus capacity (TBD, from DOTr fleet spec), max holding duration (TBD), holding action bins ({0.0, 0.1, 0.2, 0.3, 0.4}), action space size (10 = 5 hold options × 2 skip options), Monte Carlo runs per cell (at least 30), and discount parameters (TBD).

*Swept/variable parameters:* weather disturbance intensity ({0.0, 0.3, 0.6, 1.0, 1.3}), demand scaling clip ([1,3]), traffic-speed scaling clip ([0.8, 1.2]), breakdown rate (TBD).

*Derived parameters (computed during SUMO calibration):* baseline inter-stop travel time and its standard deviation (both TBD, from the dataset), baseline coefficient of variation (TBD, computed from the dataset), and the lognormal shape/location parameters (computed via method-of-moments formulas already defined elsewhere in the chapter).

A closing sentence explains that TODO-VAL items need confirmation once the dataset/schedule records arrive, and TODO-DATA items get computed during SUMO calibration; also notes the stop count and fleet-size range are reused, not new, values.

**Why:** RTC comment 15 — summarize fixed and variable simulation parameters with target values.

---

## 2026-08-06 — E4C20 — methods.tex, Section 3.2.6 (four generator subsections)

Added one implementation-mechanics sentence to each of the four disturbance generator descriptions, explaining exactly *when* the random value is sampled and *how* it's applied — filling in a gap where the text described what each generator represents statistically but not the concrete simulation mechanic.

**Passenger Demand — added:** "In implementation, the scaling factor is sampled once per episode at initialization and applied uniformly to every per-stop, per-time-of-day arrival rate for the duration of that simulated operating day, so all stops experience the same proportional demand shift within a single run while the shift itself varies across runs."

**Traffic Delays — added:** "In implementation, the speed scaling factor is sampled once per episode and applied to the bus's mean cruising speed on every inter-stop segment traversal during that day, producing a uniformly slower or faster corridor for that run without segment-level variation beyond the calibrated baseline."

**Weather-Induced Anomalies — added:** "In implementation, when the weather intensity parameter is greater than zero, a fresh travel-time sample is drawn independently for each bus at each inter-stop segment traversal during the episode, replacing the traffic-speed generator's output for that traversal; the lognormal parameters are computed from the segment's empirical mean and the swept intensity value via the method-of-moments equations given earlier."

**Bus Breakdowns — added:** "In implementation, at each discrete simulation timestep, a Bernoulli trial (essentially a weighted coin flip) with probability lambda times the timestep length is evaluated independently for each active bus; a 'heads' removes that bus from the active agent set for the remainder of the simulated day."

**Why:** RTC comment 20 — explain in detail how each disturbance scenario is actually simulated.

---

## 2026-08-06 — E4C21 — methods.tex, Sections 3.2.9 and 3.2.7

**Part A — Before (3.2.9 opening):** The "Data Analysis Methods" section jumped straight into: "For each (control strategy, disturbance level) cell, at least 30 independent Monte Carlo runs are executed using matched random seeds across strategies. Three response variables are logged per run: mean passenger waiting time, mean total travel time, and headway coefficient of variation." — with no formal definition of what those three metrics actually mean mathematically.

**Part A — After:** A new opening was added defining each metric formally:
- **Mean passenger waiting time:** the average time from a passenger's arrival at a stop to their successful boarding, averaged across all passengers served and all stops over one simulated day. (Given as an explicit averaging formula.)
- **Mean total travel time:** the average elapsed time from a bus's departure from the origin terminal to its arrival at the final stop, averaged across all completed trips.
- **Headway coefficient of variation:** the standard deviation of observed inter-bus headways divided by their mean, computed across all stops over one simulated day. A value of zero means perfectly regular headways; larger values mean worse bunching. This mirrors the same baseline coefficient-of-variation definition already used elsewhere in the chapter for travel time, just applied to headways instead.

Then the original sentence about 30+ Monte Carlo runs follows unchanged.

**Part B — Before (3.2.7 State Space, end of the observation-vector bullet list):** The bullet list of observation components (spatial location, headways, demand, environmental flags) ended, then jumped straight to the "Action Space" subsection.

**Part B — After:** A new table titled "Agent observation vector: features, symbols, and data sources" was inserted between the bullet list and the Action Space section, listing 7 features (control stop index, forward headway, backward headway, onboard passenger count, waiting passenger count, disturbance intensity flag, breakdown flag) with two columns each: what real-world sensor system would supply that feature in deployment (AVL feed, APC system, AFC terminal, weather API, incident management system), versus what supplies it in this simulation (hardcoded stop list, event-driven bus model, active generator parameter, etc.). A closing sentence clarifies all simulated features are synthetic — no real sensor data is used during training or evaluation.

**Why:** RTC comment 21 — include details on the metrics and description of observation features.

---

## 2026-08-06 — E1C1+E2C5+E4C22 — REVERTED, no net change

A "Dataset Description" section was drafted, describing SafeTravelPH as a crowdsourced GPS-trajectory mobile app, its July 2023 EDSA Busway collection window, and its per-trip record structure — plus a 6-row table mapping dataset fields to their roles in calibration, and a closing sentence about the secondary DOTr FOI ridership source. All specific numbers used TODO-DATA placeholders correctly.

**Why reverted:** The user caught this before any commit: the group doesn't actually have access to the SafeTravelPH dataset yet, and even though the numbers were placeholder-tagged, the *qualitative* description (what kind of app it is, how its records are structured, why record density would vary) asserted more familiarity with the dataset than is currently honest. The whole addition was removed, restoring the section to exactly what it said before the edit. Full detail on what was drafted and why it was pulled is in TRACKER.md.

---

## 2026-08-06 — Citation fix: Patil2025Conformal — methods.tex, Section 3.2.6

**Before:** "Patil et al. validated this parameterization against INRIX freeway data via the Kolmogorov-Smirnov test, reporting a close fit at the highest variability level they tested (KS = 0.036, p = 0.94 at CV = 1.0)."

**After:** "Patil et al. tested this parameterization by generating SUMO-simulated travel times under the same CV-driven lognormal recipe — with time windows and mean travel times anchored to INRIX historical data for an urban arterial corridor, not a freeway — and confirming via the Kolmogorov-Smirnov test that the simulated distribution matches the assumed log-normal shape, reporting a close fit at the highest variability level they tested (KS = 0.036, p = 0.94 at CV = 1.0)."

**Why:** Checked against the actual paper. Its own Table V classifies the test route as "Local, Minor/Principal Arterials" — not a freeway. Also, the KS test in the paper checks whether SUMO-simulated travel times follow the assumed log-normal shape; it isn't a direct statistical comparison against INRIX's own data. The numeric KS/p values themselves were confirmed correct.

---

## 2026-08-06 — Citation fix: Rodriguez2023Cooperative — methods.tex, Section 3.2.7

**Before:** "...A continuous holding parameter was considered, following Wang and Sun, but rejected for three reasons. First, continuous actions require actor-critic algorithms, whose training instability compounds across the swept-disturbance evaluation budget. Second, Rodriguez et al. showed that a 5-bin discretization of the holding parameter achieves combined holding-and-skipping control on a comparable corridor without measurable loss of performance versus continuous formulations. Third, real driver compliance with second-level holding instructions is itself coarse, so continuous precision is not meaningful at deployment."

**After:** "...This study's action space (10 discrete actions: 5 holding strengths × 2 skip choices, selected independently) is broader than Rodriguez et al.'s combined holding-and-skipping controller, which instead selects among 6 mutually exclusive actions: 5 holding strengths (where the zero-strength option already covers 'no holding') plus a single separate skip action. The same 5-value holding-strength set is used in both studies. A continuous holding parameter was considered but rejected for two reasons: continuous actions require actor-critic algorithms with training instability that compounds across the evaluation budget, and real driver compliance with holding instructions is itself imperfect — Rodriguez et al. model non-compliant drivers as executing only 60-80% of the instructed holding time — so continuous precision isn't meaningful at deployment anyway."

**Why:** Checked against the full paper. No comparison against a continuous action space exists anywhere in it — that specific claim was unsupported and has been removed. Also, Rodriguez's actual action space is a 6-way mutually exclusive choice, not a 10-way independent combination like this thesis's own design — the description was corrected to reflect that difference honestly, while keeping this thesis's own 10-action design unchanged (it's used elsewhere in the manuscript, so changing it would ripple through other sections).

---

## 2026-08-06 — Citation fix: Wangsun — methods.tex, Section 3.2.6

**Before:** "The baseline empirical transit demand is perturbed each episode by a scaling factor..., clipped to [1, 3], following Wang and Sun. ...The upper bound of 3 corresponds to roughly a tripling of baseline boarding rates, spanning the range observed during major event let-outs and severe-weather mode shifts."

**After:** "...clipped to [1, 3], following the general Gaussian-clipped demand-scaling mechanism of Wang and Sun, though this study adopts a narrower clip than their [1, 10] range. ...The upper bound of 3, corresponding to roughly a tripling of baseline boarding rates, is this study's own choice (flagged to revisit against Wang and Sun's wider range during implementation) rather than a value drawn from prior work."

**Why:** Checked against the actual paper. Their own equation clips the demand-scaling factor to [1, 10], not [1, 3] — and the "event let-outs" justification for the number 3 doesn't appear anywhere in their paper either. Kept the study's own [1, 3] choice (since changing it to [1, 10] would be a real experimental redesign, not a citation fix) but stopped implying that specific number came from Wang and Sun.

---

## 2026-08-06 — E3C9 + E2C4 — introduction.tex, after Section 1.2.2 (SARL)

**Before:** The Single-Agent RL limitations section ended with a paragraph about SA-DRL's competitive results, then jumped straight to the Multi-Agent RL section.

**After:** A new introductory sentence and table were inserted between them: "To situate the MARL literature reviewed next within the broader ML and SARL landscape, [this table] extends the paradigm comparison from Table 1.1 with a disturbance-coverage column, using the same D/S/T/W/B notation as the main MARL comparison table."

New table, "Disturbance coverage across ML and SARL vehicle-scheduling studies":
| Paper | Paradigm | Method | Disturbances covered |
|---|---|---|---|
| Wang et al. | ML (data-driven) | Bus scheduling incorporating time-dependent traffic and demand | D |
| Barrera Hernandez et al. | ML-assisted (heuristic dispatcher) | Passenger-demand forecasting supporting a heuristic dispatcher | D |
| Zhao et al. | SARL | STDH-DQN; self-attention state encoder over spatial-temporal AVL features | D, T |
| Zhang and Zheng | SARL | SA-DRL; categorical identity features (vehicle, station, trip ID) | D, T |
| Verbich and El-Geneidy | Heuristic (non-MARL) | Dynamic transit control under severe weather and vehicle breakdowns | W, B |

Footnote clarifies the D/S/T/W/B classifications for the four sources without a local PDF follow the RTC panel's own characterization from their review letter, not independently re-verified text.

Followed by a paragraph: "The funnel is now complete: no ML or SARL study covers W or B, and among MARL studies, only Verbich and El-Geneidy's heuristic controller addresses both — and it's explicitly non-MARL. Patil et al. similarly validate weather-induced travel-time distributions but don't address bus control at all; their contribution to this study is the lognormal parameterization for the weather generator, not a bus-control baseline. No prior study — ML, SARL, or MARL — combines W and B coverage with an actual MARL bus-scheduling controller, which is the specific gap this study fills."

**Why:** RTC comment 9 (asks for an ML/SARL disturbance table) and comment 4 (asks for a severe-weather comparison study) — solved together, since Verbich & El-Geneidy is exactly the kind of study comment 4 wants, and it fits naturally as a row in the comment-9 table rather than duplicating it elsewhere.

---

## 2026-08-06 — E3C10 — introduction.tex, before Table 1.2 discussion

**Before:** The paragraph right before the Table 1.2 summary jumped straight into: "Table 1.2 summarizes what each study evaluated, what disturbances it modeled, and what it reported."

**After:** A new paragraph was added right before that: "Only Shi et al. carries a breakdown (B) entry in Table 1.2. Cao et al., who also model discrete vehicle failures, are deliberately excluded from this count: their MARL application is to train rescheduling, not bus scheduling, so they don't belong in a table scoped to MARL bus-control literature. Verbich and El-Geneidy likewise model breakdowns but use heuristic, non-MARL control (see the new ML/SARL table), so they're excluded for the same reason. Among MARL bus-scheduling studies specifically, Shi et al. remains the only one to model discrete breakdowns."

**Why:** RTC comment 10 — the table shows only one breakdown paper (Shi et al.) but the presentation reportedly showed two; verify and fix. Couldn't confirm what was actually shown in the presentation slides (no access to them), so used the RTC letter's own suggested fallback: explain clearly why the two "candidate" second papers (Cao et al. — a train paper; Verbich & El-Geneidy — non-MARL) are correctly excluded, rather than guessing at adding an unverified row.

---

## 2026-08-06 — E3C11 — figure caption attribution (introduction.tex, methods.tex)

Added the note "Authors' illustration." to the end of 7 figure captions that were original diagrams with no source citation and no attribution note:
- Figure 1.3 (SARL vs. MARL architecture comparison)
- Figure 1.4 (Centralized training / decentralized execution)
- Figure 3.1 (Two-phase simulation pipeline)
- Figure 3.2 (Illustrative SUMO calibration output)
- Figure 3.3 (Agent-environment cycle during training)
- Figure 3.4 (Illustrative Stage A output format)
- Figure 3.5 (Monte Carlo evaluation layer)

Figures 1.1 and 1.2 already had proper citations (DOTr ridership data, TSSP rainfall study) and were left as-is.

**Why:** RTC comment 11 — some figures lack citations; original diagrams should say so explicitly rather than looking uncredited.

---

## 2026-08-06 — E3C14 — problem.tex, Delimitations (a)

**Before:** "(a) Due to computational constraints, the simulation is restricted to a defined operational sub-segment of the EDSA Carousel corridor rather than the entire metropolitan road network. The restriction is justified by the need to preserve 1:1 empirical traffic volumes for GEH calibration without resorting to flow scaling; corresponding GEH calibration statistics are reported in Chapter 4."

**After:** "(a) Due to computational constraints, the simulation is restricted to a defined operational sub-segment of the EDSA Carousel corridor rather than the entire metropolitan road network, and minor feeder roads leading into the corridor are not modeled. Both restrictions are justified by the same structural fact: the EDSA Carousel operates on a physically separated, barrier-protected busway, so the agents' state and reward depend only on bus dynamics within the dedicated lane — specifically headways, dwell times, and onboard loads — none of which are directly observed by or computed from feeder-road traffic. Feeder roads affect the corridor only indirectly, through the passenger arrival rates they produce at each stop, and that effect is already captured by the calibrated per-stop demand distributions without needing to simulate the feeder network itself. Modeling feeder roads in SUMO would add computational cost without adding any new information the agents' observation or reward could use, since the sub-corridor restriction also preserves 1:1 empirical traffic volumes for GEH calibration without resorting to flow scaling; corresponding GEH calibration statistics are reported in Chapter 4."

**Why:** RTC comment 14 — explain why minor roads leading to the corridor are excluded from the simulation.

---

*Nothing follows.*
