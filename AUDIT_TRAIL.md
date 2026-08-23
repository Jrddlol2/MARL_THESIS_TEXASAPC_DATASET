# AUDIT TRAIL — Group B3 Thesis Manuscript Changes
# Before/after log of the ACTUAL .tex CONTENT ONLY. Not a task tracker
# (see REVISION_QUEUE.md) and not a process log (see TRACKER.md / git log) —
# this file is strictly "what did the LaTeX look like before, what does it
# look like now." Append a new entry per task that touches manuscript .tex.
#
# Format: one ```diff fence per entry. `-` = removed, `+` = added, no
# prefix = unchanged context. GitHub renders `-` red and `+` green, so the
# actual change is visually obvious. See AUDIT_TRAIL_READABLE.md for the
# plain-English companion (bold-highlighted instead of diff syntax).
#
# Numbering note (2026-08-23): E3C17 later inserted the corridor map, shifting
# the historical SARL/MARL and CTDE figure numbers from 1.3/1.4 to 1.4/1.5.
# Historical entries retain the numbering used when the edits were made.

---

## 2026-08-06 — E1C3 — problem.tex, Section 2.2 (Research Gap)
**Commit:** `34017d3` (entry backfilled — missed at the time)

```diff
  Without this characterization, it cannot be determined whether reported MARL gains persist, degrade gracefully, or collapse under realistic operating disturbances, which in turn blocks the transition of MARL bus scheduling from simulation to real urban transit deployment.
+
+ The weather-disturbance class (W) in particular was identified through the literature survey conducted earlier in this study (Section~\ref{subsec:marl-applied}), which found that no prior MARL bus-scheduling paper models heavy-tailed weather-induced travel-time delays (Table~\ref{tab:marl_performance}, column W). Its operational relevance to the EDSA corridor is established by the rainfall-driven reductions in average speed and free-flow capacity documented in Section~1.1 \cite{TSSP_Rain2018} and by the typhoon-related service suspensions recorded for the corridor \cite{DOTr2020Suspension}. The lognormal parameterization adopted for this disturbance class follows the Kolmogorov--Smirnov-validated form of Patil et al.~\cite{Patil2025Conformal}, introduced in this study to address the resulting lack of temporally aligned, corridor-specific anomaly data (Section~\ref{subsec:disturbance-gap}).
```

**Why:** RTC comment 3 — research gap should include how the weather disturbance column was arrived at.

---

## 2026-08-06 — E2C6 — introduction.tex 1.2.1, methods.tex Baseline Controllers
**Commit:** `34017d3` (entry backfilled)

```diff
  ...allowing small headway perturbations to amplify into bunching \cite{Daganzo2009}. Static schedules therefore remain mathematically inadequate for stochastic traffic environments, where the governing quantities are random variables rather than deterministic constants.
+ Under the specific non-ideal conditions this study targets, the failure modes differ by control strategy. A fixed timetable has no feedback mechanism at all, so once bunching begins nothing in the schedule corrects it. A local reactive rule that holds a bus based only on the gap to the bus ahead can partially correct bunching under ordinary congestion, but has no way to respond to a breakdown, since it observes only the forward gap and not the enlarged gap a failed bus leaves behind it. A more globally aware reactive rule that accounts for both the forward and backward gap improves on this, but still follows a fixed, pre-specified rule rather than a learned response, so it cannot adapt its behavior to the heavier-tailed delays that severe weather introduces.
  These limitations motivated the transition toward more adaptive and data-driven scheduling methodologies.
```

```diff
  (methods.tex, No Control subsection, excerpt)
  ...NC also provides the reference point for measuring the severity of bus bunching.
+ Under non-ideal conditions, NC has no corrective mechanism whatsoever, so demand surges, weather-induced delays, and breakdowns are expected to compound directly into bunching with no attenuation.
```

(Equivalent one-sentence additions were made to the Forward Headway and Even Headway subsections, describing their own expected failure modes — FH: can't observe the backward gap a breakdown creates; EH: no mechanism to anticipate weather's heavy tails.)

**Why:** RTC comment 6 — expound on how traditional non-AI scheduling performs under bunching/weather/breakdowns.

---

## 2026-08-06 — E2C7 — methods.tex, Section 3.2.10
**Commit:** `34017d3` (entry backfilled)

```diff
- \textbf{Stage A: Ideal-condition evaluation.} ...The acceptance criterion is twofold: (i) mean passenger waiting time no worse than EH (no statistically significant degradation at $p < 0.05$ with multiple-comparison correction), and ideally a statistically significant improvement; and (ii) a statistically significant reduction in headway coefficient of variation relative to NC. Under ideal conditions EH is already near-optimal...
+ \textbf{Stage A: Ideal-condition evaluation.} ...Under ideal conditions EH is already near-optimal, so parity with EH is an acceptable Stage A outcome. Outperforming EH is the target but not required to pass Stage A...
+
+ \paragraph{Stage A acceptance criterion}
+ \begin{itemize}
+ \item[(i)] Mean passenger waiting time no worse than EH (no statistically significant degradation at $p < 0.05$ with multiple-comparison correction), and ideally a statistically significant improvement.
+ \item[(ii)] A statistically significant reduction in headway coefficient of variation relative to NC.
+ \end{itemize}
```
(Stage B's criterion sentence was similarly pulled into a `\paragraph{Stage B acceptance criterion}` callout, unchanged in substance.)

**Why:** RTC comment 7 — describe what successful performance will look like, more visually prominent.

---

## 2026-08-06 — E3C12 — introduction.tex, Section 1.2.3 (after Figure 1.3)
**Commit:** `34017d3` (entry backfilled)

```diff
      \label{fig:sarl-vs-marl}
  \end{figure}
+
+ In both panels of Figure~\ref{fig:sarl-vs-marl}, the per-bus state (denoted $s_{i,t}$ in the formal MDP notation of Section~\ref{subsec:state-space}, and shown in the figure as the local observation $o_i$) encodes the bus's current position, forward and backward headways, onboard load, and queue length at its current stop, as defined in full in Section~\ref{subsec:state-space}. The action $a_{i,t}$ is the holding-strength and stop-skipping decision the controller emits for that bus, defined in Section~\ref{subsec:action-space}. In the SARL panel (a), a single centralized network ingests all $N$ per-bus state vectors concatenated into one global state $s \in \mathbb{R}^{N \cdot d}$ and outputs all $N$ actions simultaneously; in the MARL panel (b), the same shared network weights $\theta$ instead process each bus's local state independently, so each agent acts on only its own observation rather than the concatenated global one.
+
  Multi-Agent Reinforcement Learning (MARL) addresses the three limitations above
```

**Why:** RTC comment 12 — explain the concepts in Figure 1.3 (bus states and actions).

---

## 2026-08-06 — E3C13 — introduction.tex Section 1.1, methods.tex Section 3.2.3
**Commit:** `34017d3` (entry backfilled)

```diff
  (introduction.tex)
- ...empirical studies on Philippine expressways show that increasing rainfall intensity significantly reduces average traffic speed and free-flow capacity \cite{TSSP_Rain2018}.
+ ...empirical studies on Philippine expressways show that increasing rainfall intensity significantly reduces average traffic speed and free-flow capacity \cite{TSSP_Rain2018}. This rainfall-impact evidence is drawn from a 2018 study of the North Luzon Expressway rather than the EDSA Busway, and is used here only as contextual motivation that weather materially affects Philippine road-traffic operations; the weather-disturbance generator in this study (Section~3.2.6) does not adopt this study's specific speed-reduction percentages, and EDSA-specific travel-time behavior is independently calibrated through the GEH/RMSE procedure described in Section~3.2.3.
```

```diff
  (methods.tex, Environment Model Validation opening)
- ...The calibration is restricted to the bus corridor itself, since the agents' state and reward depend only on bus dynamics; surrounding mixed-traffic flows do not enter the Python environment.
+ ...The calibration is restricted to the bus corridor itself, since the agents' state and reward depend only on bus dynamics; surrounding mixed-traffic flows do not enter the Python environment. This GEH/RMSE procedure calibrates EDSA-specific parameters directly from EDSA operational data and does not depend on the North Luzon Expressway rainfall-impact figures cited as motivating evidence in Section~1.1 \cite{TSSP_Rain2018}; that citation establishes only that weather materially affects Philippine road-traffic operations in general, not any EDSA-specific speed or capacity value used in this calibration.
```

**Why:** RTC comment 13 — Reference [10] is both dated (2018) and a different corridor (North Luzon Expressway); clarify whether adopted or independently tuned for EDSA. (This is the corrected version of the task — the original queue entry only covered the corridor-mismatch half until cross-checked against RTC_DECISION_LETTER.md.)

---

## 2026-08-06 — E3C8 — methods.tex, Section 3.2.6
**Commit:** `01c49bf`

```diff
  \subsection{Stochastic Disturbance Generators}
  \label{subsec:stochastic-vars}

+ \paragraph{Disturbance Classes and Independence}
+
+ This study distinguishes five disturbance classes, denoted D, S, T, W, and B:
+
+ \begin{itemize}
+ \item \textbf{Stochastic demand (D):} the baseline, always-present day-to-day randomness in passenger arrivals, drawn from the calibrated per-(stop, time-of-day) demand distributions (Section~\ref{subsec:data-pipeline}). D is not a disturbance layered on top of a deterministic baseline; it \textit{is} the baseline stochastic environment, present in every run regardless of which other generators are active.
+ \item \textbf{Demand surge (S):} an episode-level multiplicative scaling factor, with standard deviation $\sigma_d$ (Table~\ref{tab:notation}), that amplifies baseline boarding rates above their empirical mean. S is the controlled experimental variable; D is always present, and S is what is added on top of it. Setting $\sigma_d = 0$ removes the surge and leaves only baseline demand variability (D).
+ \item \textbf{Traffic-speed perturbation (T):} an episode-level scaling of corridor cruising speed, with standard deviation $\sigma_s$, representing everyday congestion friction. T governs inter-stop travel-time variability under ideal conditions.
+ \item \textbf{Weather-induced delay (W):} a per-segment travel-time distribution with coefficient of variation $\eta$, drawn from a right-skewed lognormal rather than the Gaussian-based scaling used by T. W replaces T as the source of travel-time stochasticity once $\eta > 0$ (Section~\ref{subsec:stochastic-vars}).
+ \item \textbf{Discrete bus breakdown (B):} a Poisson-distributed discrete event, with rate $\lambda$, that permanently removes one bus from the active agent set for the remainder of the simulated day.
+ \end{itemize}
+
+ The four generators that produce S, T, W, and B are injected independently: no causal chain links them within the simulation. A breakdown event (B) does not trigger a demand surge (S) or a weather delay (W), and a weather event does not induce a mechanical failure. In practice, some real-world disturbances co-occur causally --- for example, heavy rain may both slow buses (W) and concentrate passengers at covered stops (S) --- but this study treats each generator as an independent factor. This design choice isolates the individual and combined effect of each disturbance class on controller performance and allows the single-disturbance ablation (Section~\ref{subsec:evaluation}) to attribute degradation unambiguously to a specific class.
+
  Four stochastic generators inject variability into the Python environment. Generators (i) and (ii) follow the perturbation framework of Wang and Sun~\cite{Wangsun}; the weather generator's heavy-tailed lognormal formulation follows Patil et al.~\cite{Patil2025Conformal}; the breakdown generator follows the rescheduling formulation of Cao et al.~\cite{Cao2022Train}. Table~\ref{tab:notation} collects the symbols used across this section and the MARL formulation that follows.
```

**Why:** RTC comment 8 — define each disturbance explicitly, clarify independence, distinguish stochastic demand from demand surge.

---

## 2026-08-06 — E3C15 — methods.tex, Section 3.2.4 (end)
**Commit:** `01c49bf`

```diff
  Throughout this chapter, \textit{ideal conditions} and \textit{non-ideal conditions} refer to these operating states of the simulated environment. \textit{Baseline controllers} refers separately to the three non-MARL control strategies (No Control, Forward Headway, Even Headway) against which the MARL policy is benchmarked. A condition is a state of the world; a controller is a choice of algorithm.

+ \begin{table}[htbp]
+ \centering
+ \caption{Simulation parameter summary: fixed, swept/variable, and derived parameters.}
+ \label{tab:sim-parameters}
+ ...
+ [three-part table: Fixed parameters (simulation horizon, M=24 stops,
+ N≈12-30 fleet, control stop count TBD, H_0 TBD, capacity TBD, ΔT TBD,
+ Ω={0.0,0.1,0.2,0.3,0.4}, |A_i|=10, N_runs≥30, γ/β TBD) | Swept/variable
+ parameters (η sweep, σ_d clip [1,3], σ_s clip [0.8,1.2], λ TBD) | Derived
+ parameters (μ, σ, CV_0 all TBD-DATA; σ_ln, μ_ln via method of moments)]
+ ...
+ \end{table}
+
+ Parameters marked \%TODO-VAL are to be confirmed during the implementation phase upon receipt of the operational dataset and DOTr schedule records; parameters marked \%TODO-DATA will be computed during the SUMO calibration phase described in Section~3.2.3. The stop count ($M=24$) and fleet-size range ($N \approx 12$--$30$) are carried over from the state-space dimensionality discussion in Section~1.2.2 and are not new values introduced here.

  \subsection{Data Processing}
```

**Why:** RTC comment 15 — summarize fixed/variable simulation parameters with target values.

---

## 2026-08-06 — E4C20 — methods.tex, Section 3.2.6 (four generator subsections)
**Commit:** `01c49bf`

```diff
  (Passenger Demand)
  ...Sampling occurs at the start of each simulation run, producing varied demand profiles across episodes.
+ In implementation, the scaling factor $f_d \sim \mathcal{N}(1, \sigma_d^2)$ is sampled once per episode at initialization and applied uniformly to every per-stop, per-time-of-day arrival rate for the duration of that simulated operating day, so all stops experience the same proportional demand shift within a single run while the shift itself varies across runs.
```

```diff
  (Traffic Delays)
  ...clipped to $[0.8, 1.2]$, representing typical daily congestion friction \cite{Wangsun}.
+ In implementation, the speed scaling factor $f_s \sim \mathcal{N}(1, \sigma_s^2)$ is sampled once per episode and applied to the bus's mean cruising speed on every inter-stop segment traversal during that day, producing a uniformly slower or faster corridor for that run without segment-level variation beyond the calibrated baseline.
  This generator provides the baseline stochastic variability in inter-stop travel time when the weather generator is inactive.
```

```diff
  (Weather-Induced Anomalies)
  ...regardless of its meteorological label.
+ In implementation, when $\eta > 0$ a fresh travel-time sample $T \sim \text{LogNormal}(\mu_{ln}, \sigma_{ln})$ is drawn independently for each bus at each inter-stop segment traversal during the episode, replacing the traffic-speed generator's output for that traversal; the lognormal parameters $\mu_{ln}$ and $\sigma_{ln}$ are computed from the segment's empirical mean $\mu$ and the swept $\eta$ via Equations~\eqref{eq:sigma_ln}--\eqref{eq:mu_ln}.
  The disturbance intensity sweep is therefore read as a span of travel-time variability magnitudes, not as a sweep across named weather categories.
```

```diff
  (Bus Breakdowns)
  ...with a configurable rate $\lambda$ (Table~\ref{tab:notation}).
+ In implementation, at each discrete simulation timestep of length $dt$, a Bernoulli trial with probability $\lambda \cdot dt$ is evaluated independently for each active bus; a success removes that bus from the active agent set for the remainder of the simulated day.
  When a breakdown occurs at bus $b_k$, $b_k$ is removed from the active agent set...
```

**Why:** RTC comment 20 — explain in detail how each disturbance scenario is simulated.

---

## 2026-08-06 — E4C21 — methods.tex, Sections 3.2.9 and 3.2.7
**Commit:** `01c49bf`

```diff
  (3.2.9 opening)
  \subsection{Data Analysis Methods}

+ The three response variables logged per run are defined as follows. \textbf{Mean passenger waiting time} ($\bar{W}$) is the average time elapsed from a passenger's arrival at a stop to their successful boarding, averaged across all passengers served and all stops over one simulated operating day:
+
+ \begin{equation}
+ \bar{W} = \frac{1}{P} \sum_{p=1}^{P} \left(t_p^{\text{board}} - t_p^{\text{arrive}}\right)
+ \label{eq:waiting_time}
+ \end{equation}
+
+ where $P$ is the total number of passengers served in the run... \textbf{Mean total travel time} ($\bar{T}$) is the average elapsed time from a bus's departure from the origin terminal to its arrival at the final stop of the sub-corridor... \textbf{Headway coefficient of variation} ($CV_h$) measures headway regularity:
+
+ \begin{equation}
+ CV_h = \frac{\sigma_h}{\mu_h}
+ \label{eq:headway_cv}
+ \end{equation}
+
+ where $\sigma_h$ and $\mu_h$ are the standard deviation and mean of observed inter-bus headways... This construction mirrors the baseline coefficient of variation $CV_0$ already defined for travel time (Table~\ref{tab:notation}), applied here to the headway distribution instead.
+
  For each (control strategy, disturbance level) cell, $N \geq 30$ independent Monte Carlo runs are executed using matched random seeds across strategies. Three response variables are logged per run: mean passenger waiting time, mean total travel time, and headway coefficient of variation.
```

```diff
  (3.2.7 State Space, end of bullet list)
  \item \textbf{Environmental flags:} encoded indicators for the current disturbance intensity and any active downstream incident or breakdown.
  \end{itemize}

+ \begin{table}[htbp]
+ \centering
+ \caption{Agent observation vector: features, symbols, and data sources.}
+ \label{tab:observation-features}
+ ...
+ [7-row table: control stop index, forward/backward headway, onboard count,
+ waiting count, disturbance flag, breakdown flag — each with Deployment
+ Source (AVL/APC/AFC/weather API/incident system) vs Simulation Source]
+ ...
+ \end{table}
+
+ In simulation, all observation features are generated synthetically by the Python environment at each control event by querying the analytical bus model and the active stochastic generators; no real sensor data is consumed during training or evaluation.
+
  \subsubsection{Action Space ($A_i$)}
```

**Why:** RTC comment 21 — metric definitions and observation-feature descriptions.

---

## 2026-08-06 — E1C1+E2C5+E4C22 — REVERTED

**Step 1 — Added (mid-session, not committed):**
```diff
  \item \textbf{Corridor bus operational data.} A per-trip record of EDSA Carousel bus operation... The baseline operating point for this study is established from a crowdsourced operational record collected from the EDSA Busway during July 2023 through the SafeTravelPH mobile application.

  \end{itemize}

+ \paragraph{Dataset Description}
+
+ The baseline operating point described above is grounded in the SafeTravelPH dataset: a crowdsourced mobile application through which commuters submit trip-level GPS trajectory reports while travelling along Philippine transit corridors... Each submission corresponds to a single commuter trip and yields a per-trip trajectory log rather than a fixed-interval sensor feed, so record density varies by segment and time of day according to rider participation. The dataset comprises \%TODO-DATA: insert total trip record count...
+
+ [Table 3.2: "SafeTravelPH dataset fields and their role in simulation calibration" — 6 rows]
+
+ A secondary source of station-level ridership aggregates...is to be acquired from the Department of Transportation (DOTr) under the Freedom of Information framework...
+
  Severe-weather conditions are not estimated from operational data in this study but are injected as a controlled experimental variable, with disturbance magnitudes anchored to validated literature values rather than to a corridor-specific severe-weather sample.
```

**Step 2 — User caught it before commit:** "I should have said that you should not edit yet anything regarding the dataset. Because, we still dont have access to it yet." — the numeric placeholders were fine, but the qualitative claims about the dataset's structure assumed more familiarity than is honest right now.

**Step 3 — Reverted (back to original):**
```diff
+ \item \textbf{Corridor bus operational data.} A per-trip record of EDSA Carousel bus operation... The baseline operating point for this study is established from a crowdsourced operational record collected from the EDSA Busway during July 2023 through the SafeTravelPH mobile application.
+
+ \end{itemize}
+
- \paragraph{Dataset Description}
- [...entire drafted block removed...]
-
  Severe-weather conditions are not estimated from operational data in this study but are injected as a controlled experimental variable...
```

**Net result:** the pushed commit (`01c49bf`) contains no trace of the drafted block — this section reads exactly as it did before the session started. Full detail on what was drafted and why it was pulled is in `TRACKER.md`.

---

## 2026-08-06 — Citation fix: Patil2025Conformal — methods.tex, Section 3.2.6
**Commit:** `4fcc1a1` (as part of the citation-verification pass)

```diff
- Travel time is drawn as $T \sim \text{LogNormal}(\mu_{ln}, \sigma_{ln})$. Patil et al.~\cite{Patil2025Conformal} validated this parameterization against INRIX freeway data via the Kolmogorov-Smirnov test, reporting a close fit at the highest variability level they tested ($KS = 0.036$, $p = 0.94$ at $CV = 1.0$).
+ Travel time is drawn as $T \sim \text{LogNormal}(\mu_{ln}, \sigma_{ln})$. Patil et al.~\cite{Patil2025Conformal} tested this parameterization by generating SUMO-simulated travel times under the same CV-driven lognormal recipe --- with time windows and mean travel times anchored to INRIX historical data for an urban arterial corridor, not a freeway --- and confirming via the Kolmogorov-Smirnov test that the simulated distribution matches the assumed log-normal shape, reporting a close fit at the highest variability level they tested ($KS = 0.036$, $p = 0.94$ at $CV = 1.0$).
```

**Why:** Verified against the actual PDF (RRL/Travel_Time_and_Weather-Aware...pdf). The paper's Table V classifies its route as "Local, Minor/Principal Arterials," not freeway; the KS test checks the simulated distribution's shape, not a direct INRIX comparison. The numeric KS/p values were confirmed correct.

---

## 2026-08-06 — Citation fix: Rodriguez2023Cooperative — methods.tex, Section 3.2.7
**Commit:** `4fcc1a1`

```diff
- The full action set is the Cartesian product of these two components: $|A_i| = 5 \times 2 = 10$ discrete actions per control event. A continuous holding parameter $\alpha \in [0, 1]$ was considered, following Wang and Sun~\cite{Wangsun}, but rejected for three reasons. First, continuous actions require actor-critic algorithms, whose training instability compounds across the swept-disturbance evaluation budget. Second, Rodriguez et al.~\cite{Rodriguez2023Cooperative} showed that a 5-bin discretization of $\alpha$ achieves combined holding-and-skipping control on a comparable corridor without measurable loss of performance versus continuous formulations. Third, real driver compliance with second-level holding instructions is itself coarse \cite{Rodriguez2023Cooperative}, so continuous precision in $\alpha$ is not meaningful at deployment.
+ The full action set is the Cartesian product of these two components: $|A_i| = 5 \times 2 = 10$ discrete actions per control event, allowing the agent to select a holding strength and a skip decision independently at each control event. This is a broader action space than Rodriguez et al.~\cite{Rodriguez2023Cooperative}, whose combined holding-and-skipping controller (DDQN-HA) instead selects among six \textit{mutually exclusive} actions: five holding strengths $\Omega = \{0.0, 0.1, 0.2, 0.3, 0.4\}$ (with $\omega = 0$ already covering the no-holding case) plus a single skip action. The discretized holding-strength set $\Omega$ adopted here matches theirs exactly. A continuous holding parameter $\alpha \in [0, 1]$ was considered, following Wang and Sun~\cite{Wangsun}, but rejected for two reasons. First, continuous actions require actor-critic algorithms, whose training instability compounds across the swept-disturbance evaluation budget. Second, real driver compliance with holding instructions is itself imperfect: Rodriguez et al.~\cite{Rodriguez2023Cooperative} model non-compliant drivers as departing after only 60--80\% of the instructed holding time, so continuous precision in $\alpha$ is not meaningful at deployment.
```

**Why:** Verified against the actual PDF. No continuous-vs-discrete comparison exists anywhere in the paper — that claim was unsupported. Rodriguez's actual action space is 6 mutually-exclusive actions, not this study's 10-action independent Cartesian space. Kept the thesis's own $|A_i|=10$ design unchanged (load-bearing elsewhere); only corrected what is attributed to Rodriguez.

---

## 2026-08-06 — Citation fix: Wangsun — methods.tex, Section 3.2.6
**Commit:** `b366932`

```diff
- The baseline empirical transit demand is perturbed each episode by a scaling factor sampled from $\mathcal{N}(1, \sigma_d^2)$, clipped to $[1, 3]$, following Wang and Sun~\cite{Wangsun}. The asymmetric clip focuses the test on demand surges rather than symmetric variation, since demand drops produce lightly loaded conditions that do not stress-test the controller. The upper bound of 3 corresponds to roughly a tripling of baseline boarding rates, spanning the range observed during major event let-outs and severe-weather mode shifts.
+ The baseline empirical transit demand is perturbed each episode by a scaling factor sampled from $\mathcal{N}(1, \sigma_d^2)$ and clipped to $[1, 3]$, following the general Gaussian-clipped demand-scaling mechanism of Wang and Sun~\cite{Wangsun}, though this study adopts a narrower clip than their $[1, 10]$ range. The asymmetric clip focuses the test on demand surges rather than symmetric variation, since demand drops produce lightly loaded conditions that do not stress-test the controller. The upper bound of 3, corresponding to roughly a tripling of baseline boarding rates, is this study's own choice (\%TODO-VAL: revisit against Wang and Sun's wider range during implementation) rather than a value drawn from prior work.
```

**Why:** Verified against the actual PDF. Their Eq. 22 clips the demand scaling factor to $[1,10]$, not $[1,3]$ — the manuscript's specific bound and its "event let-outs" justification were not supported by the source.

---

## 2026-08-06 — E3C9 + E2C4 — introduction.tex, after Section 1.2.2 (SARL)
**Commit:** `4fcc1a1`

```diff
  ...which motivates the MARL choice here while acknowledging this caveat.

+ To situate the MARL literature reviewed in the next subsection within the broader ML and SARL landscape, Table~\ref{tab:ml_sarl_coverage} extends the paradigm comparison of Table~\ref{tab:control_paradigms} with a disturbance-coverage column, using the same D/S/T/W/B notation as Table~\ref{tab:marl_performance}.
+
+ \begin{table}[htbp]
+ \centering
+ \caption{Disturbance coverage across ML and SARL vehicle-scheduling studies...}
+ \label{tab:ml_sarl_coverage}
+ ...
+ [5-row table: Wang2017 (ML, D), Barrera2025Optimization (ML-assisted, D),
+ Zhao2022STDH (SARL, D+T), Zhang2025SADRL (SARL, D+T), verbich2021
+ (heuristic, W+B)]
+ ...
+ \end{table}
+
+ The funnel is now complete: no ML or SARL study covers W or B, and among MARL studies (Table~\ref{tab:marl_performance}), only Verbich and El-Geneidy's heuristic controller~\cite{verbich2021} addresses both --- and it is explicitly non-MARL. Patil et al.~\cite{Patil2025Conformal} similarly validate weather-induced travel-time distributions but do not address bus control at all... No prior study, ML, SARL, or MARL, combines W and B coverage with an actual MARL bus-scheduling controller, which is the specific gap this study fills.
+
  \subsection{Multi-Agent Reinforcement Learning}
```

**Why:** RTC comment 9 (ML/SARL disturbance table) and comment 4 (severe-weather comparison study) — satisfied together via a companion table rather than adding Verbich as a Table 1.2 row (the RTC letter offered both as valid options). Disturbance-coverage classifications for the four sources without a local PDF are attributed to the panel's own characterization in a table footnote, not presented as independently verified — Barrera2025Optimization's classification was checked against its local PDF.

---

## 2026-08-06 — E3C10 — introduction.tex, before Table 1.2 discussion
**Commit:** `4fcc1a1`

```diff
+ Only Shi et al.~\cite{Shi2022DistDRL} carries a B (breakdown) entry in Table~\ref{tab:marl_performance}. Cao et al.~\cite{Cao2022Train}, which also models discrete vehicle failures, is deliberately excluded from this count: their MARL application is to \textit{train} rescheduling, not bus scheduling, so it does not belong in a table scoped to MARL bus-control literature. Verbich and El-Geneidy~\cite{verbich2021} likewise model breakdowns but use heuristic, non-MARL control (Table~\ref{tab:ml_sarl_coverage}), so they are excluded for the same reason. Among MARL bus-scheduling studies specifically, Shi et al. remains the only one to model discrete breakdowns.
+
  Table~\ref{tab:marl_performance} summarizes what each study evaluated, what disturbances it modeled, and what it reported.
```

**Why:** RTC comment 10 — Table 1.2 shows only one B-paper but the presentation reportedly showed two. Could not confirm what was actually shown (no slide access), so applied the RTC letter's own conservative fallback: a clarifying footnote explaining why Cao et al. (train paper) and Verbich & El-Geneidy (non-MARL) are correctly excluded, rather than guessing at an unverified second row.

---

## 2026-08-06 — E3C11 — figure caption attribution (introduction.tex, methods.tex)
**Commit:** `4fcc1a1`

```diff
  (one example — introduction.tex Figure 1.3; same pattern applied to 6 more captions)
- across $N$ agents, each acting on its own local observation $o_i$.}
+ across $N$ agents, each acting on its own local observation $o_i$. Authors' illustration.}
  \label{fig:sarl-vs-marl}
```

**Why:** RTC comment 11 — some figures lack citations; Figures 1.3 and 1.4 are original diagrams needing an "authors' illustration" note. Applied the same note to methods.tex Figures 3.1–3.5 for consistency (also original, previously unattributed — flagged as in-scope in REVISION_QUEUE.md: "3.1–3.5 appear original"). Figures 1.1 and 1.2 already had citations and were left unchanged.

---

## 2026-08-06 — E3C14 — problem.tex, Delimitations (a)
**Commit:** `4fcc1a1`

```diff
- \textbf{Delimitations.} (a) Due to computational constraints, the simulation is restricted to a defined operational sub-segment of the EDSA Carousel corridor rather than the entire metropolitan road network. The restriction is justified by the need to preserve 1:1 empirical traffic volumes for GEH calibration without resorting to flow scaling; corresponding GEH calibration statistics are reported in Chapter~4.
+ \textbf{Delimitations.} (a) Due to computational constraints, the simulation is restricted to a defined operational sub-segment of the EDSA Carousel corridor rather than the entire metropolitan road network, and minor feeder roads leading into the corridor are not modeled. Both restrictions are justified by the same structural fact: the EDSA Carousel operates on a physically separated, barrier-protected busway \cite{Chua2026}, so the agents' state and reward depend only on bus dynamics within the dedicated lane, specifically headways, dwell times, and onboard loads, none of which are directly observed by or computed from feeder-road traffic. Feeder roads affect the corridor only indirectly, through the passenger arrival rates they produce at each stop, and that effect is already captured by the calibrated per-stop demand distributions (Section~3.2.5) without needing to simulate the feeder network itself. Modeling feeder roads in SUMO would add computational cost without adding any new information the agents' observation or reward could use, since the sub-corridor restriction also preserves 1:1 empirical traffic volumes for GEH calibration without resorting to flow scaling; corresponding GEH calibration statistics are reported in Chapter~4.
```

**Why:** RTC comment 14 — justify why minor roads leading to the corridor are no longer considered.

---

## 2026-08-06 — E3C16 — figure/table callout sweep (introduction.tex, methods.tex)
**Commit:** not yet committed

Ten one-clause insertions, each adding a missing `\ref{}` to an existing sentence next to a previously-uncited figure/table:

```diff
  (introduction.tex)
- ...up from 63.02 million in 2024 \cite{DOTr2025Ridership}.
+ ...up from 63.02 million in 2024 (Figure~\ref{fig:bg-ridership}) \cite{DOTr2025Ridership}.

- The reduction in average speeds are about 5.34\%...
+ As Figure~\ref{fig:bg-rainfall} shows, the reduction in average speeds are about 5.34\%...

- To address this, most modern formulations use \textbf{Centralized Training with Decentralized Execution (CTDE)}.
+ To address this, most modern formulations use \textbf{Centralized Training with Decentralized Execution (CTDE)}, illustrated in Figure~\ref{fig:ctde}.
```

```diff
  (methods.tex)
- The pipeline proceeds in two phases.
+ As shown in Figure~\ref{fig:pipeline}, the pipeline proceeds in two phases.

- ...measures the discrepancy between simulated and observed hourly bus volumes on individual corridor segments:
+ ...measures the discrepancy...on individual corridor segments, illustrated in panel (a) of Figure~\ref{fig:calibration-illustrative}:

- RMSE evaluates how closely simulated bus speed trajectories match empirical observations:
+ RMSE evaluates...match empirical observations, illustrated in panel (b) of Figure~\ref{fig:calibration-illustrative}:

- Parameters marked \%TODO-VAL are to be confirmed...
+ Table~\ref{tab:sim-parameters} therefore serves as the single reference point for every parameter used across this chapter. Parameters marked \%TODO-VAL are to be confirmed...

- In simulation, all observation features are generated synthetically...
+ As Table~\ref{tab:observation-features} shows, in simulation all observation features are generated synthetically...

- The learning process follows the standard reinforcement-learning feedback loop...
+ ...follows the standard...feedback loop..., illustrated in Figure~\ref{fig:aec-training}.

- ...are each run for $N \geq 30$ Monte Carlo iterations with matched seeds. Under ideal conditions EH is already near-optimal,
+ ...matched seeds, reported in the format shown in Figure~\ref{fig:stage-a-illustrative}. Under ideal conditions EH is already near-optimal,

- ...with the breakdown generator active at each level.
+ ...active at each level, using the Monte Carlo evaluation procedure illustrated in Figure~\ref{fig:aec-eval}.
```

**Why:** RTC comment 16 — figures and tables should be called and discussed in the paragraphs, not just placed. A sweep of all 15 figures/tables found 10 with zero `\ref{}` anywhere despite adjacent topical discussion; added one reference each without altering the discussion itself. Table 3.1 (tab:notation) — the RTC's own example of a too-thin callout — was checked and found to already have 5 separate substantive references elsewhere in the chapter, so it needed no fix beyond what existed.

---

## 2026-08-06 — E3C18 + E3C19 — main.tex preamble
**Commit:** not yet committed

```diff
  \usepackage{ragged2e}
  \usepackage{totalcount}
+ \usepackage{setspace}
```

```diff
  %TC:ignore
  \begin{document}
  %TC:ignore
+ \onehalfspacing
  \input{title.tex} % Putting the title page
```

```diff
  % --------------------------------------------------------------------------------
  % Start line numbering
- %\linenumbers
+ \linenumbers
```

**Why:** RTC comments 18 and 19 — 1.5 line spacing and line numbers for the non-final manuscript. Applied last, after all other content edits in this revision round, per CLAUDE.md's own guidance to avoid disrupting line references mid-revision.

---

## 2026-08-06 — E1C2 — methods.tex, Section 3.2.5 (end)
**Commit:** not yet committed

```diff
  \end{itemize}

+ Table~\ref{tab:field-mapping} maps each required raw field to the parameter derived from it and the MARL component that parameter feeds into, connecting the data requirements above to the disturbance generators (Section~\ref{subsec:stochastic-vars}), the control-stop selection criteria (Section~\ref{subsec:control-stop-selection}), and the agent observation vector (Section~\ref{subsec:state-space}). The mapping reflects the study's design intent, not properties of a processed dataset; specific statistics remain \%TODO-DATA pending dataset acquisition.
+
+ \begin{table}[htbp]
+ \centering
+ \caption{Mapping of required raw dataset fields to derived parameters and their role in the MARL formulation.}
+ \label{tab:field-mapping}
+ ...
+ [6-row table: GPS location → travel-time distribution → SUMO calibration/
+ traffic-speed & weather generators; boarding events → demand rate →
+ demand-surge generator/observation feature; alighting events →
+ through-volume → control-stop selection criterion 3; occupancy → load
+ profile → observation feature/dwell-time estimation; operating speed →
+ cruising speed → GEH calibration/traffic-speed generator; dwell time →
+ dwell distribution → event-driven bus model]
+ ...
+ \end{table}
+
  Severe-weather conditions are not estimated from operational data in this study but are injected as a controlled experimental variable...
```

Also added `\label{subsec:control-stop-selection}` to the previously-unlabeled "Control-Stop Selection" subsection, and fixed two cross-references that initially pointed at the wrong label (`subsec:data-pipeline`) before that label existed.

**Why:** RTC comment 2 — map dataset fields to proposed features of the study. Judged safe to do without dataset access: connects two already-published specs (required fields in 3.2.5, MARL components in 3.2.6/3.2.7/3.2.2) rather than describing the actual dataset's contents, unlike the reverted E1C1/E2C5/E4C22 task. See TRACKER.md for the full reasoning.

---

## 2026-08-06 — E3C17 — introduction.tex (Background), methods.tex (Weather-Induced Anomalies)
**Commit:** not yet committed

```diff
  (introduction.tex, after the ridership figure)
      \label{fig:bg-ridership}
  \end{figure}
  %%

+ Figure~\ref{fig:bg-corridor-map} shows the EDSA Carousel Southbound route from Monumento to PITX, the corridor this study is grounded in, together with the other public transport modes (jeepney, MRT, LRT, tricycle, UV/FX) that intersect it at each major stop.
+
+ \begin{figure}[htbp]
+     \centering
+     \includegraphics[width=0.75\textwidth]{Figures/bg_fig3_edsa_corridor_map.pdf}
+     \caption[EDSA Carousel corridor map]{EDSA Carousel Southbound route
+     (Monumento to PITX) with intersecting public transport modes at each
+     stop. Authors' illustration, adapted from the group's defense
+     presentation.}
+     \label{fig:bg-corridor-map}
+ \end{figure}
+
  Despite the gradual increase in demand,
```

```diff
  (methods.tex, Weather-Induced Anomalies subsubsection)
  ...results at this level are interpreted as a probe of controller behavior under extreme conditions rather than as a calibrated scenario.
+ Table~\ref{tab:eta-basis} summarizes this reasoning.
+
+ \begin{table}[htbp]
+ \centering
+ \caption{Basis for each swept weather-disturbance intensity value.}
+ \label{tab:eta-basis}
+ ...
+ [5-row table: η=0.0 generator off; η=0.3/0.6 inside Patil et al.'s
+ validated range; η=1.0 top of validated range (nominal severe point);
+ η=1.3 beyond validated range (extrapolated stress test)]
+ ...
+ \end{table}

  The mapping from $\eta$ to a specific named weather severity...
```

**Why:** RTC comment 17 — include figures/tables shown in the defense but missing from the manuscript. Reviewed all 58 slides of the group's defense deck against the manuscript; most slide content duplicated existing prose/figures. These two were genuinely new: the corridor map (matches the RTC letter's own example of what might be missing) and the η-basis table (existing prose converted to table form, prose kept unchanged). See TRACKER.md for full reasoning on what was judged out of scope (Work Plan Gantt charts, software/tools appendix).

**Process note:** the corridor map image was extracted from slide 47 of `B3-Final-Defense.pdf` (rendered at 3x resolution via PyMuPDF, cropped to the map graphic, saved as `Figures/bg_fig3_edsa_corridor_map.pdf`). This repo has no `Figures/` directory otherwise — existing `\includegraphics` calls reference images that live only on Overleaf. The user needs to upload this new file to Overleaf's Figures folder for the manuscript to compile there.

---

## 2026-08-06 — N1 (self-identified, not RTC) — methods.tex, Section 3.2.7
**Commit:** not yet committed

```diff
  ...This study defines the reward \textit{structure} for the hybrid action space, the three component terms above, and treats their relative weighting, plus a sensitivity analysis over those weights, as the implementation-phase deliverable (EO 2.1). The component structure is fixed; the coefficients are not yet finalized.
+
+ The reward is computed individually for each agent at every control event, not as a shared team-level signal: $r_{i,t}$ is agent $i$'s own entry in the transition $(s_{i,t}, a_{i,t}, r_{i,t}, s_{i,t'})$ written to the shared replay buffer (Training and Execution Protocol, step 4), so each bus is scored on the consequences of its own action even though all agents update the same shared network. Locally-observable quantities already in $s_{i,t}$, principally the forward and backward headway components $h^-$ and $\hat{h}^+$, let this individual signal still reflect corridor-wide regularity without requiring a centralized reward computation at execution time. The three priorities combine additively as a weighted sum of per-event penalty terms,
+
+ \begin{equation}
+ r_{i,t+k} = -w_1 \cdot (\text{headway-irregularity term}) - w_2 \cdot (\text{waiting-time term}) - w_3 \cdot (\text{skip-degeneracy term}),
+ \label{eq:reward-form}
+ \end{equation}
+
+ with weights $w_1, w_2, w_3$ \%TODO-VAL: to be tuned as the Expected Output 2.1 sensitivity analysis. Each term is expressed as a non-positive penalty, so the agent maximizes its expected return in Eq.~\eqref{eq:bellman} by simultaneously minimizing headway irregularity, passenger waiting, and degenerate skipping; this sign convention, not the specific per-term formulas or their relative weights, is what this chapter fixes ahead of implementation.
```

**Why:** self-identified gap (user notice, not an RTC comment) — the existing text defined the reward's *priorities* and deferred *weighting* to EO 2.1, but never explained the reward's *mechanics*: whether it's individual or shared, how the three priorities combine into a scalar, or the sign convention. Added those three things without touching the existing structure/weighting distinction or specifying any coefficient value.

---

## 2026-08-06 — N2 — problem.tex, Section 2.4 (Significance)
**Commit:** not yet committed

```diff
  \section{Significance of the Study}
- This study contributes both practical and scientific significance.
+ This study contributes both practical and scientific significance. MARL is the control method under evaluation in this study; the corridor's service reliability under disturbance is the object of study it is applied to measure, which is why practical significance is discussed first.

  \textbf{Practical significance.} The EDSA Carousel carries on the order of $1.8\times10^5$ passengers daily...
```

**Why:** self-identified, prompted by the user's recollection that a panelist questioned during Q&A whether the study reads as more focused on MARL than bus scheduling. States the thesis's own positioning explicitly rather than leaving it implicit in section ordering.

---

## 2026-08-06 — N2 — problem.tex, Section 2.2 (Research Gap)
**Commit:** not yet committed

```diff
  Without this characterization, it cannot be determined whether reported MARL gains persist, degrade gracefully, or collapse under realistic operating disturbances, which in turn blocks the transition of MARL bus scheduling from simulation to real urban transit deployment.
+ This joint-disturbance framing reflects two independently-documented, concurrent operational realities of the same corridor rather than only a gap in existing comparison tables: EDSA experiences both weather-driven service disruptions \cite{PhilstarTyphoon2024, PIA_Emergency2023} and chronic mechanical-failure risk \cite{Chua2026} as ongoing features of its operating environment, so a controller validated against each in isolation provides no evidence of how it behaves when a transit operator's actual risk exposure includes both at once. The disturbance generators remain independently sampled within the simulation (Section~3.2.6); this operational context motivates evaluating their union, not a claim that the two are causally or temporally linked.

  The weather-disturbance class (W) in particular was identified through the literature survey conducted earlier in this study...
```

**Why:** self-identified. Grounds the "combined disturbance" framing in an EDSA-specific operational fact rather than presenting it as only a gap in existing MARL comparison tables (Table~\ref{tab:marl_performance}), while explicitly preserving the existing independence statement in Section~3.2.6 so the two additions don't contradict each other.

---

## 2026-08-06 — N1 rewrite (user-provided prose) — methods.tex, Section 3.2.7
**Commit:** not yet committed

```diff
  ...Existing MARL bus-control reward formulations span a range of trade-offs among these priorities, from headway-coefficient-of-variation forms for holding-only action spaces \cite{Wangsun,Wang2023MultiObj} to passenger-time forms for combined holding-and-skipping action spaces \cite{Rodriguez2023Cooperative}.
- This study defines the reward \textit{structure} for the hybrid action space, the three component terms above, and treats their relative weighting, plus a sensitivity analysis over those weights, as the implementation-phase deliverable (EO 2.1). The component structure is fixed; the coefficients are not yet finalized.
-
- The reward is computed individually for each agent at every control event, not as a shared team-level signal: $r_{i,t}$ is agent $i$'s own entry in the transition $(s_{i,t}, a_{i,t}, r_{i,t}, s_{i,t'})$ written to the shared replay buffer (Training and Execution Protocol, step 4), so each bus is scored on the consequences of its own action even though all agents update the same shared network. Locally-observable quantities already in $s_{i,t}$, principally the forward and backward headway components $h^-$ and $\hat{h}^+$, let this individual signal still reflect corridor-wide regularity without requiring a centralized reward computation at execution time. The three priorities combine additively as a weighted sum of per-event penalty terms,
+ This study establishes the overall reward structure for the hybrid action space by defining the three reward components and their additive formulation, while treating the corresponding weighting coefficients, together with their sensitivity analysis, as the implementation-phase deliverable under Expected Output 2.1. Although the component structure is fixed at this stage, the coefficients remain as placeholders to be determined during implementation through experimental evaluation.
+
+ The reward is computed independently for each agent at every control event rather than as a shared team-level objective. Accordingly, $r_{i,t}$ represents the reward assigned to agent $i$ and is stored as that agent's transition in the shared replay buffer (Training and Execution Protocol, step 4). Each bus is therefore evaluated based on the consequences of its own action, even though all agents learn from a common shared network. Since the reward is derived from locally observable quantities already contained in the agent's observation, particularly the forward and backward headway measurements, the resulting signal remains aligned with corridor-wide service regularity without requiring a centralized reward computation during execution.
+
+ The overall reward function is expressed as the weighted sum of three penalty terms:

  \begin{equation}
  r_{i,t+k} = -w_1 \cdot (\text{headway-irregularity term}) - w_2 \cdot (\text{waiting-time term}) - w_3 \cdot (\text{skip-degeneracy term}),
  \label{eq:reward-form}
  \end{equation}

- with weights $w_1, w_2, w_3$ \%TODO-VAL: to be tuned as the Expected Output 2.1 sensitivity analysis. Each term is expressed as a non-positive penalty, so the agent maximizes its expected return in Eq.~\eqref{eq:bellman} by simultaneously minimizing headway irregularity, passenger waiting, and degenerate skipping; this sign convention, not the specific per-term formulas or their relative weights, is what this chapter fixes ahead of implementation.
+ where $w_1$, $w_2$, and $w_3$ denote the weighting coefficients (\%TODO-VAL) to be determined through the Expected Output 2.1 sensitivity analysis. Each component is formulated as a non-positive penalty, allowing the agent to maximize its cumulative return in Eq.~\eqref{eq:bellman} by minimizing headway irregularity, passenger waiting time, and unnecessary stop-skipping behavior. Consequently, this chapter establishes the reward formulation and its optimization objective, while the specific mathematical expressions and coefficient values are reserved for the implementation and evaluation phase.
```

**Why:** the user supplied polished replacement prose for N1's content and asked that it be applied. The equation itself (Eq. eq:reward-form) is unchanged; the surrounding prose was rewritten for tone/flow, folding "additive formulation" language earlier into the structure paragraph and restating the mechanics/sign-convention paragraph in the user's own wording. Kept the `%TODO-VAL` placeholder tag on the weighting coefficients (the user's text didn't include it, but CLAUDE.md's placeholder convention requires it for greppability) and the existing citations/priority list in the untouched first half of the structure paragraph.

---

## 2026-08-23 — Repository audit maintenance — problem.tex Section 2.1; methods.tex Sections 3.2.4 and 3.2.5
**Commit:** `7680bd0`

```diff
  This study develops and evaluates a MARL-based bus scheduling model on a calibrated stochastic simulation of the EDSA Carousel corridor, with non-ideal conditions operationalized as the simultaneous and independent injection of passenger demand surges, severe-weather travel-time skew, and Poisson-distributed bus breakdowns.
- TThe objective is to quantify how MARL performance degrades from its ideal-condition baseline as disturbance intensity rises, producing the first integrated robustness characterization for MARL bus scheduling under this specific combination of disturbances.
+ The objective is to quantify how MARL performance degrades from its ideal-condition baseline as disturbance intensity rises, producing the first integrated robustness characterization for MARL bus scheduling under this specific combination of disturbances.

- The Python environment still injects normal day-to-day variability through the calibrated per-segment distributions, so the ideal condition is \textit{stochastic but not disturbed} which comparable to a normal weekday with no incidents, severe weather, or surge events.
+ The Python environment still injects normal day-to-day variability through the calibrated per-segment distributions, so the ideal condition is \textit{stochastic but not disturbed}, which is comparable to a normal weekday with no incidents, severe weather, or surge events.

- The baseline operating point for this study is established from a crowdsourced operational record collected from the EDSA Busway during July 2023 through the SafeTravelPH mobile application.
+ The baseline operating point will be established only after the intended July 2023 SafeTravelPH EDSA Busway record has been acquired and its schema and coverage verified; no calibration or dataset-specific statistics are claimed at this stage.
```

**Why:** repository audit maintenance requested by the user. Corrected two
non-substantive language defects and removed a premature claim that the unseen
EDSA dataset had already established the calibration baseline. No dataset was
selected, characterized, or processed.

---

## 2026-08-23 — Texas CapMetro full case-study pivot — main.tex; introduction.tex; problem.tex; methods.tex; thesis_refs.bib
**Branch:** `dataset/texas-capmetro-801`

```diff
- \title{An Evaluation of Multi-Agent Reinforcement Learning for Dynamic Bus Scheduling Under Non-Ideal Conditions}
+ \title{An Evaluation of Multi-Agent Reinforcement Learning for Dynamic Bus Scheduling Under Non-Ideal Conditions: A CapMetro Rapid Case Study}

- [Active EDSA background, EDSA ridership/map/rain figures, and EDSA-specific empirical rationale]
+ [Active CapMetro Route 801 background, reproduced Route 801/803 coverage table,
+  229,421-row direction-code 6 subset description, and verified NOAA join]
+ % Superseded EDSA-specific background retained temporarily in source history only.
+ \iffalse
+ [prior EDSA background]
+ \fi

- To investigate ... a calibrated simulation of the EDSA Carousel corridor.
+ To evaluate ... a public-data-calibrated simulation of CapMetro Rapid Route 801 direction code 6.

- Stage A/Stage B prose used conflicting S/T/W activation rules and let W replace T.
+ \caption{Authoritative disturbance-activation matrix.}
+ Training: D+T on; S/W/B randomized.
+ Stage A: D+T on; S/W/B off.
+ Stage B: D+T+S+W+B on.
+ Ablations: D+T plus S, W, or B individually.

- Total stop count ... 24; fleet size approximately 12--30; sigma cells displayed clip bounds.
+ Total distinct stop IDs ... 29; fleet size TODO-DATA; sigma values separated
+ from the [1,3] and [0.8,1.2] clip supports.

- Weather lognormal replaced the traffic-speed generator and drew T directly
- from LogNormal(mu_ln, sigma_ln).
+ T_W = T_0 m_{s,b,d}(w) F_W
+ [Observed ordinary-rain multiplier is estimated within segment/time/day strata;
+  F_W is a unit-mean, labeled synthetic out-of-support stress factor.]

- CTDE caption/prose: shared reward and joint-state training.
+ CTDE caption/prose: per-agent rewards and local transitions feed a shared replay
+ buffer and shared DDQN learner; no joint-state actor input or team reward.

- SafeTravelPH requirements-only data description.
+ Verified CapMetro APC, NOAA LCDv2, and historical-GTFS/fleet-source gate;
+ absent passenger-arrival, capacity, breakdown, and continuous-trajectory fields
+ are stated explicitly.
```

**Why:** the user approved a full Texas case-study branch after the public-data
audit. Every numeric dataset statement above is reproduced by the committed
pipeline evidence. No SUMO calibration, MARL result, causal rain multiplier,
historical direction label, capacity, or observed breakdown was invented.

---

## 2026-08-23 — Texas branch final re-audit corrections — scripts/texas_capmetro_pipeline.py; methods.tex; progress/audit reports

```diff
- Route 801 provides the larger clean stop-event, boarding, trip-day, and usable-segment sample.
+ Route 801 provides larger clean stop-event, boarding, and usable-segment
+ samples despite fewer distinct trip-day pairs.

- The full evaluation suite of approximately 960 runs is expected to require
- single-digit hours ... approximately 30 hours of T4-class GPU time.
+ The declared minimum evaluation suite contains 1,080 runs.
+ No wall-clock duration is claimed before representative Route 801 episodes
+ are profiled on the actual implementation.
```

**Why:** the first sentence overstated one route-selection metric: Route 803 has
more distinct trip-day pairs, although Route 801 retains the larger event,
boarding, and usable-segment samples. The runtime paragraph also conflicted with
the explicit 1,080-run arithmetic and projected performance without a benchmark.
The correction preserves feasibility as a testable plan rather than inventing
runtime evidence. `PROGRESS.md` and the re-audit also record that nine active
graphics are absent from this checkout and must be synchronized from Overleaf.
The same static pass removed an incomplete `\includeonly[` command from
`main.tex`; chapters are already loaded with `\input`.

---

*Nothing follows.*
