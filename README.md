# MARL
Examiner 1

1. "Update the manuscript with the proposed setup and discussion of dataset"

Your manuscript partially addresses this in Section 3.2.5 — you mention the SafeTravelPH crowdsourced record from July 2023 and list the required fields (GPS, boardings, speed, dwell time). What's missing is a concrete description of what the dataset actually looks like: how many trip records, how many days, how many buses, a sample of what a row contains, and maybe a small summary statistics table (e.g., mean inter-stop travel time across segments, mean boarding rate per stop-bin).

Action: Add a short subsection or paragraph in 3.2.5 after "Required Datasets" with something like a "Dataset Description" table showing: number of trip records, observation window dates, number of unique bus units, number of stops covered, mean/SD of key fields. Even a 4–5 row table would satisfy this.

2. "Provide mapping of dataset to proposed features of the study"

This is the bridge between raw data and your MARL formulation. The manuscript describes the dataset fields in 3.2.5 and the observation vector in 3.2.7 separately, but never explicitly connects them.

Action: Add a mapping table, either at the end of 3.2.5 or the start of 3.2.7, with columns like: Raw Dataset Field → Derived Parameter → MARL Component. For example: "GPS-tracked location" → "per-segment travel time μ, σ" → "anchors weather generator (η) and traffic generator (σs)"; "Boarding/alighting counts" → "per-(stop, time-of-day) demand rate" → "baseline for demand surge generator (σd), passenger waiting count in observation si,t".

3. "Research gap should include how you arrived at the column of sudden weather disturbance"

Your Section 2.2 states the gap but doesn't trace how you derived the weather disturbance (W) as a distinct column. The logic chain exists scattered across 1.2.4–1.2.5 but isn't summarized in the gap statement itself.

Action: Add 2–3 sentences in Section 2.2 explaining the derivation path: "The weather-disturbance class was identified through the literature survey in Section 1.2.4, which found that no prior MARL bus-scheduling study models heavy-tailed weather-induced travel-time delays (Table 1.2, column W). The operational relevance of this class to EDSA is documented by the rainfall-impact data in Section 1.1 [10] and the typhoon-related service suspensions [47]. The lognormal parameterization adopted for this class follows the Kolmogorov-Smirnov-validated form of Patil et al. [50]."

Examiner 2

4. "Include study that considers severe weather conditions in your comparison"

Your Table 1.2 currently has no paper with a "W" in the disturbance column. Verbich and El-Geneidy [25] is already in your bibliography and directly studies severe weather conditions and vehicle breakdowns on dynamic transit control — but it only appears in the ML section (1.2.1), not in Table 1.2.

Action: Either add Verbich & El-Geneidy [25] as a row in Table 1.2 (noting it uses heuristic control, not MARL, but covers W and B), or add a new companion table for non-MARL studies that covers weather. Also consider adding Patil et al. [50] to the comparison discussion since they validate weather-induced travel-time distributions.

5. "Explain what the dataset looks like"

Same as Examiner 1, comment #1 above — add concrete dataset descriptive statistics.

6. "Expound on how traditional, non-AI scheduling systems perform under the conditions you have specified"

Your Section 1.2.1 discusses static scheduling's inadequacy in general, and Section 3.2.8 defines the FH and EH baselines, but neither section explicitly discusses how these traditional methods degrade under bus bunching, severe weather, or breakdowns.

Action: Add a paragraph in Section 1.2.1 (after the Daganzo [18] reference) explaining specifically: static schedules have no mechanism to recover from bunching once it starts; FH can partially correct bunching but cannot handle breakdowns (it only looks at the bus ahead, not the gap created behind a failed bus); EH is better but still follows a fixed rule that doesn't account for weather-induced heavy tails. This connects your "why RL?" argument directly to the disturbance classes. You could also add 1–2 sentences in 3.2.8 under each baseline explaining its expected failure mode under non-ideal conditions.

7. "Can you describe what a successful performance will look like?"

Section 3.2.10 has acceptance criteria but they're somewhat buried in prose.

Action: Make the success criteria more explicit — perhaps a small box or bolded list. For Stage A: "MARL mean passenger waiting time ≤ EH mean passenger waiting time (p < 0.05, corrected); headway CV significantly lower than NC." For Stage B: "MARL mean passenger waiting time < best baseline mean waiting time at every swept η level; MARL degradation slope < EH degradation slope." Your current prose says essentially this, but making it visually prominent would address the comment.

Examiner 3 — RRW

8. "Define each 'disturbance' explicitly. Dependencies? Stochastic demand vs. demand surge?"

Section 3.2.6 describes each generator but doesn't open with crisp one-line definitions, and doesn't explicitly state whether they're independent or causally linked.

Action: Add a definition block at the start of 3.2.6 (or 2.5), something like:

Stochastic demand (D): Baseline day-to-day variability in passenger arrivals, present in all runs, drawn from calibrated per-(stop, time-of-day) distributions.
Demand surge (S): An episode-level scaling factor σd that multiplies baseline demand above 1×, representing event let-outs or mode shifts. D is always present; S is the controlled variable that amplifies it.
Traffic-speed perturbation (T): Episode-level scaling of corridor cruising speed within ±20% of baseline.
Weather-induced delay (W): Lognormal-distributed inter-stop travel time with CV = η, replacing T under non-ideal conditions.
Discrete breakdown (B): Poisson-distributed bus removal events.

Then add: "The four generators are injected independently; no causal chain links them. A breakdown does not trigger a weather event, and a demand surge does not cause a speed reduction. In reality, some disturbances may co-occur (e.g., rain causing both slower speeds and higher demand at sheltered stops), but this study treats each as an independent factor to isolate its individual and combined effect on controller performance."

9. "Consider adding an ML/SARL VSP table showing the disturbance column"

Table 1.1 compares paradigms but doesn't show disturbance coverage. Table 1.2 only covers MARL papers.

Action: Add a new Table 1.1b (or expand Table 1.1) covering ML and SARL VSP studies with an S/T/W/B disturbance column. Candidate entries from your bibliography: Wang et al. [15] (ML, data-driven bus scheduling — D only), Barrera Hernandez et al. [21] (ML-assisted — D), Zhao et al. [29] (SARL, STHD-DQN — D, T), Zhang & Zheng [30] (SARL, SA-DRL — D, T), Verbich & El-Geneidy [25] (heuristic — W, B). This makes the funnel structure cleaner: ML table → SARL table → MARL table → your study fills the remaining gaps.

10. "Table 1.2 breakdown column — presentation vs. manuscript mismatch"

Your Table 1.2 shows only Shi et al. [46] with "B." If your presentation showed two papers with breakdowns, check if Cao et al. [39] (train rescheduling with breakdowns) was shown — but it's a train paper, not bus. Or Verbich & El-Geneidy [25].

Action: Verify which paper was the second "B" in your presentation. If it was a non-MARL paper, either move it to the new ML/SARL table or add a footnote. If Table 1.2 is accurate as-is (only Shi et al. has B for MARL bus papers), add a clarifying footnote: "Cao et al. [39] model breakdowns in a train rescheduling context; Verbich & El-Geneidy [25] address breakdowns under heuristic transit control. Neither applies MARL to bus scheduling with breakdown events."

11. "Some figures do not have citations (e.g., Figure 1.3)"

Figure 1.3 (SARL vs MARL comparison) and Figure 1.4 (CTDE) appear to be original diagrams you created. If so, they don't need external citations — but you should state "Adapted from [source]" or "Authors' illustration" in the caption.

Action: For each figure, either add "adapted from [X]" if based on a source, or add "(authors' illustration)" to the caption. Check all figures: 1.1 has [6], 1.2 has [10], 3.1–3.5 appear original. Figures 1.3 and 1.4 need attribution or an "authors' illustration" note.

12. "Explain the concepts in Figure 1.3 (bus states and actions)"

The caption describes the architecture but doesn't explain what "state si" or "action ai" mean in bus terms.

Action: Add 2–3 sentences after the figure reference in the text: "In both panels, the per-bus state si encodes the bus's current position, forward and backward headways, onboard load, and queue length at its current stop. The action ai is the holding/skipping decision the controller emits for that bus. In the SARL panel (a), a single network ingests all N state vectors concatenated and outputs all N actions simultaneously; in the MARL panel (b), the same shared network processes each bus's state independently."

Examiner 3 — Methodology

13. "Reference [10] — different corridor. Will you adopt or tune for EDSA?"

Reference [10] is about the North Luzon Expressway, not EDSA. Your manuscript uses its rainfall-impact percentages in Section 1.1 but doesn't clarify whether those numbers transfer.

Action: Add a clarifying sentence in Section 1.1 where [10] is cited: "These rainfall-impact percentages are drawn from a Philippine expressway study [10] and are used here as contextual evidence that weather materially affects corridor operations. The weather-disturbance generator in this study (Section 3.2.6) does not adopt [10]'s specific speed-reduction values; instead, it parameterizes travel-time variability through a lognormal CV sweep anchored to Patil et al.'s [50] validated range. Segment-level speed and capacity parameters for the EDSA corridor are independently calibrated through the GEH/RMSE procedure described in Section 3.2.3."

14. "Justify why minor roads leading to the corridor are no longer considered"

Section 2.5 mentions the sub-corridor restriction but the justification is brief.

Action: Expand the justification in Section 2.5 (Delimitations, item a) or in 3.2.1: "Minor feeder roads are excluded because the EDSA Carousel operates on a physically separated, barrier-protected busway [5]. Bus agents' states and rewards depend only on bus dynamics within the dedicated lane (headways, dwell times, loads); traffic on feeder roads affects the corridor only through passenger arrival rates at stops, which are captured by the calibrated per-stop demand distributions. Including feeder-road networks would increase SUMO computational cost without entering the agents' observation or reward."

15. "Summarize fixed and variable simulation parameters with target values"

This is a clear gap. Your manuscript describes parameters in prose throughout 3.2.4–3.2.7 but never collects them into one summary table.

Action: Add a new table (Table 3.2 or similar) with three sections:

Fixed parameters: Fleet size N (target value: TBD from data, expected 12–30), number of stops M (24), number of control stops (TBD from data), simulation horizon (single operating day, e.g. 05:00–23:00), scheduled headway H₀ (TBD), max holding duration ΔT (TBD), bus capacity (TBD), ε-greedy schedule, replay buffer size, learning rate, target network update frequency.

Swept/variable parameters: η ∈ {0.0, 0.3, 0.6, 1.0, 1.3}, σd (range), σs (range), λ (rate, TBD), demand scaling clip [1, 3], speed scaling clip [0.8, 1.2].

Derived parameters: μ (from data), σ (from data), CV₀ (from data), μ_ln and σ_ln (from method-of-moments equations 3.4–3.5).

Examiner 3 — Other

16. "Figures and tables should be called out and discussed in the paragraphs"

Action: Do a full sweep of the manuscript. Search for every "Figure" and "Table" reference and confirm each one is discussed in the surrounding text (not just placed). In particular, check that Table 3.1 is explicitly discussed, not just referenced with "Table 3.1 collects the symbols."

17. "Include other figures/tables from the presentation that should also be in the manuscript"

Action: Review your defense slide deck. Any figure or table you showed the panel that isn't in the manuscript should be added — for example, if you showed an EDSA corridor map, a sample dataset screenshot, a disturbance-interaction diagram, or any additional comparison table.

18. "Consider 1.5 line spacing"

Action: In your LaTeX preamble, add \usepackage{setspace} and \onehalfspacing. This is a one-line fix.

19. "Consider putting line numbers"

Action: Add \usepackage{lineno} and \linenumbers to your LaTeX preamble. Remove for the final version.

Examiner 4

20. "Explain in detail the different scenarios and how to simulate this data"

Section 3.2.6 covers this but could be more explicit about the simulation mechanics.

Action: For each generator, add a sentence describing the implementation step: "At the start of each episode, the demand scaling factor is sampled once from N(1, σd²) and applied uniformly to all stop arrival rates for the duration of that simulated day." Similarly for traffic: "At each inter-stop segment traversal, the bus's cruising speed is scaled by a factor drawn from N(1, σs²), producing a segment-specific travel time." For weather: "When η > 0, the traffic-speed generator is replaced: each inter-stop travel time is drawn independently from LogNormal(μ_ln, σ_ln) with parameters computed from the segment's empirical mean μ and the swept CV = η." For breakdowns: "At each simulation timestep, a Bernoulli trial with rate λ·dt determines whether each active bus fails; upon failure, the bus is removed from the active agent set and its downstream passengers accumulate at stops."

21. "Include details on the metrics and description of features"

The metrics (waiting time, travel time, headway CV) are mentioned in 3.1 and 3.2.9 but never formally defined.

Action: Add formal one-line definitions in 3.2.9 or 3.2.10:

Mean passenger waiting time: the average time a passenger waits at a stop from arrival to boarding, averaged across all passengers and all stops in one simulated day.
Mean total travel time: the average end-to-end time from a bus's dispatch at the origin terminal to its arrival at the final stop, averaged across all buses in one simulated day.
Headway coefficient of variation: CV_h = σ_h / μ_h, where σ_h and μ_h are the standard deviation and mean of observed inter-bus headways at all stops over one simulated day.

For features, the observation vector components in 3.2.7 are listed but could have a small summary table with columns: Feature Name | Symbol | Source (deployment) | Source (simulation).

22. "What are the contents of the dataset?"

Same as comments #1 and #5 — add concrete dataset description.
