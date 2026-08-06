# AUDIT TRAIL — Group B3 Thesis Manuscript Changes
# Before/after log of the ACTUAL .tex CONTENT ONLY. Not a task tracker
# (see REVISION_QUEUE.md) and not a process log (see TRACKER.md / git log) —
# this file is strictly "what did the LaTeX look like before, what does it
# look like now." Append a new entry per task that touches manuscript .tex.

---

## 2026-08-06 — E3C8 — methods.tex, Section 3.2.6
**Commit:** `01c49bf`

**Before:**
```latex
\subsection{Stochastic Disturbance Generators}
\label{subsec:stochastic-vars}

Four stochastic generators inject variability into the Python environment. Generators (i) and (ii) follow the perturbation framework of Wang and Sun~\cite{Wangsun}; the weather generator's heavy-tailed lognormal formulation follows Patil et al.~\cite{Patil2025Conformal}; the breakdown generator follows the rescheduling formulation of Cao et al.~\cite{Cao2022Train}. Table~\ref{tab:notation} collects the symbols used across this section and the MARL formulation that follows.
```

**After:**
```latex
\subsection{Stochastic Disturbance Generators}
\label{subsec:stochastic-vars}

\paragraph{Disturbance Classes and Independence}

This study distinguishes five disturbance classes, denoted D, S, T, W, and B:

\begin{itemize}
\item \textbf{Stochastic demand (D):} the baseline, always-present day-to-day randomness in passenger arrivals, drawn from the calibrated per-(stop, time-of-day) demand distributions (Section~\ref{subsec:data-pipeline}). D is not a disturbance layered on top of a deterministic baseline; it \textit{is} the baseline stochastic environment, present in every run regardless of which other generators are active.
\item \textbf{Demand surge (S):} an episode-level multiplicative scaling factor, with standard deviation $\sigma_d$ (Table~\ref{tab:notation}), that amplifies baseline boarding rates above their empirical mean. S is the controlled experimental variable; D is always present, and S is what is added on top of it. Setting $\sigma_d = 0$ removes the surge and leaves only baseline demand variability (D).
\item \textbf{Traffic-speed perturbation (T):} an episode-level scaling of corridor cruising speed, with standard deviation $\sigma_s$, representing everyday congestion friction. T governs inter-stop travel-time variability under ideal conditions.
\item \textbf{Weather-induced delay (W):} a per-segment travel-time distribution with coefficient of variation $\eta$, drawn from a right-skewed lognormal rather than the Gaussian-based scaling used by T. W replaces T as the source of travel-time stochasticity once $\eta > 0$ (Section~\ref{subsec:stochastic-vars}).
\item \textbf{Discrete bus breakdown (B):} a Poisson-distributed discrete event, with rate $\lambda$, that permanently removes one bus from the active agent set for the remainder of the simulated day.
\end{itemize}

The four generators that produce S, T, W, and B are injected independently: no causal chain links them within the simulation. A breakdown event (B) does not trigger a demand surge (S) or a weather delay (W), and a weather event does not induce a mechanical failure. In practice, some real-world disturbances co-occur causally --- for example, heavy rain may both slow buses (W) and concentrate passengers at covered stops (S) --- but this study treats each generator as an independent factor. This design choice isolates the individual and combined effect of each disturbance class on controller performance and allows the single-disturbance ablation (Section~\ref{subsec:evaluation}) to attribute degradation unambiguously to a specific class.

Four stochastic generators inject variability into the Python environment. Generators (i) and (ii) follow the perturbation framework of Wang and Sun~\cite{Wangsun}; the weather generator's heavy-tailed lognormal formulation follows Patil et al.~\cite{Patil2025Conformal}; the breakdown generator follows the rescheduling formulation of Cao et al.~\cite{Cao2022Train}. Table~\ref{tab:notation} collects the symbols used across this section and the MARL formulation that follows.
```

**Why:** RTC comment 8 — define each disturbance explicitly, clarify independence, distinguish stochastic demand from demand surge.

---

## 2026-08-06 — E3C15 — methods.tex, Section 3.2.4 (end)
**Commit:** `01c49bf`

**Before:**
```latex
Throughout this chapter, \textit{ideal conditions} and \textit{non-ideal conditions} refer to these operating states of the simulated environment. \textit{Baseline controllers} refers separately to the three non-MARL control strategies (No Control, Forward Headway, Even Headway) against which the MARL policy is benchmarked. A condition is a state of the world; a controller is a choice of algorithm.

\subsection{Data Processing}
```

**After:**
```latex
Throughout this chapter, \textit{ideal conditions} and \textit{non-ideal conditions} refer to these operating states of the simulated environment. \textit{Baseline controllers} refers separately to the three non-MARL control strategies (No Control, Forward Headway, Even Headway) against which the MARL policy is benchmarked. A condition is a state of the world; a controller is a choice of algorithm.

\begin{table}[htbp]
\centering
\caption{Simulation parameter summary: fixed, swept/variable, and derived parameters.}
\label{tab:sim-parameters}
\small
\renewcommand{\arraystretch}{1.25}

\begin{tabularx}{\textwidth}{
>{\RaggedRight\arraybackslash}p{0.24\textwidth}
>{\RaggedRight\arraybackslash}p{0.09\textwidth}
X
>{\RaggedRight\arraybackslash}p{0.20\textwidth}
}

\toprule
\textbf{Parameter} & \textbf{Symbol} & \textbf{Value / Range} & \textbf{Source} \\
\midrule
\multicolumn{4}{l}{\textit{Fixed simulation parameters}} \\
\midrule

Simulation horizon & --- & Single simulated operating day (\%TODO-VAL: exact start/end hours) & Section~3.1 \\
Total stop count (sub-corridor) & $M$ & 24 & Introduction, Section~1.2.2 \\
Fleet size (active buses) & $N$ & $\approx 12$--$30$ & Introduction, Section~1.2.2 \\
Control stop count & --- & \%TODO-VAL: determined by criteria in Section~3.2.2 once dataset is processed & Section~3.2.2 \\
Scheduled headway & $H_0$ & \%TODO-VAL: from DOTr schedule records & DOTr records \\
Bus passenger capacity & --- & \%TODO-VAL: from DOTr fleet specification & DOTr records \\
Maximum holding duration & $\Delta T$ & \%TODO-VAL: to be set during implementation & Section~3.2.7 (Action Space) \\
Holding action bins & $\Omega$ & $\{0.0, 0.1, 0.2, 0.3, 0.4\}$ & Section~3.2.7 (Action Space) \\
Action space size per agent & $|A_i|$ & 10 (5 hold $\times$ 2 skip) & Section~3.2.7 (Action Space) \\
Monte Carlo runs per cell & $N_{\text{runs}}$ & $\geq 30$ & Section~3.1 \\
Discount / event-based discount & $\gamma$, $\beta$ & \%TODO-VAL: tuned during implementation & Section~3.2.7 \\

\midrule
\multicolumn{4}{l}{\textit{Swept / variable parameters}} \\
\midrule

Weather disturbance intensity & $\eta$ & $\{0.0, 0.3, 0.6, 1.0, 1.3\}$ & Section~3.2.6 \\
Demand scaling std.\ dev.\ (clip) & $\sigma_d$ & Clip $[1, 3]$ & Section~3.2.6 \\
Traffic-speed scaling std.\ dev.\ (clip) & $\sigma_s$ & Clip $[0.8, 1.2]$ & Section~3.2.6 \\
Breakdown rate & $\lambda$ & \%TODO-VAL: calibrated during implementation (events/hour) & Section~3.2.6 \\

\midrule
\multicolumn{4}{l}{\textit{Derived parameters (from SUMO calibration)}} \\
\midrule

Baseline inter-stop travel time & $\mu$ & Per-segment, per-time-of-day bin, \%TODO-DATA & SafeTravelPH dataset \\
Baseline travel-time std.\ dev.\ & $\sigma$ & Per-segment, per-time-of-day bin, \%TODO-DATA & SafeTravelPH dataset \\
Baseline coefficient of variation & $CV_0$ & $\sigma/\mu$ per segment, \%TODO-DATA & Computed from dataset \\
Lognormal shape parameter & $\sigma_{ln}$ & $\sqrt{\ln(\eta^2+1)}$ (Eq.~\ref{eq:sigma_ln}) & Method of moments \\
Lognormal location parameter & $\mu_{ln}$ & $\ln(\mu) - \sigma_{ln}^2/2$ (Eq.~\ref{eq:mu_ln}) & Method of moments \\

\bottomrule
\end{tabularx}
\end{table}

Parameters marked \%TODO-VAL are to be confirmed during the implementation phase upon receipt of the operational dataset and DOTr schedule records; parameters marked \%TODO-DATA will be computed during the SUMO calibration phase described in Section~3.2.3. The stop count ($M=24$) and fleet-size range ($N \approx 12$--$30$) are carried over from the state-space dimensionality discussion in Section~1.2.2 and are not new values introduced here.

\subsection{Data Processing}
```

**Why:** RTC comment 15 — summarize fixed/variable simulation parameters with target values.

---

## 2026-08-06 — E4C20 — methods.tex, Section 3.2.6 (four generator subsections)
**Commit:** `01c49bf`

**Before (Passenger Demand):**
```latex
The baseline empirical transit demand is perturbed each episode by a scaling factor sampled from $\mathcal{N}(1, \sigma_d^2)$, clipped to $[1, 3]$, following Wang and Sun~\cite{Wangsun}. The asymmetric clip focuses the test on demand surges rather than symmetric variation, since demand drops produce lightly loaded conditions that do not stress-test the controller. The upper bound of 3 corresponds to roughly a tripling of baseline boarding rates, spanning the range observed during major event let-outs and severe-weather mode shifts. Sampling occurs at the start of each simulation run, producing varied demand profiles across episodes.
```

**After (Passenger Demand):**
```latex
The baseline empirical transit demand is perturbed each episode by a scaling factor sampled from $\mathcal{N}(1, \sigma_d^2)$, clipped to $[1, 3]$, following Wang and Sun~\cite{Wangsun}. The asymmetric clip focuses the test on demand surges rather than symmetric variation, since demand drops produce lightly loaded conditions that do not stress-test the controller. The upper bound of 3 corresponds to roughly a tripling of baseline boarding rates, spanning the range observed during major event let-outs and severe-weather mode shifts. Sampling occurs at the start of each simulation run, producing varied demand profiles across episodes. In implementation, the scaling factor $f_d \sim \mathcal{N}(1, \sigma_d^2)$ is sampled once per episode at initialization and applied uniformly to every per-stop, per-time-of-day arrival rate for the duration of that simulated operating day, so all stops experience the same proportional demand shift within a single run while the shift itself varies across runs.
```

**Before (Traffic Delays):**
```latex
Mean cruising speed between stops is adjusted dynamically using a scaling factor drawn from $\mathcal{N}(1, \sigma_s^2)$, clipped to $[0.8, 1.2]$, representing typical daily congestion friction \cite{Wangsun}. This generator provides the baseline stochastic variability in inter-stop travel time when the weather generator is inactive.
```

**After (Traffic Delays):**
```latex
Mean cruising speed between stops is adjusted dynamically using a scaling factor drawn from $\mathcal{N}(1, \sigma_s^2)$, clipped to $[0.8, 1.2]$, representing typical daily congestion friction \cite{Wangsun}. In implementation, the speed scaling factor $f_s \sim \mathcal{N}(1, \sigma_s^2)$ is sampled once per episode and applied to the bus's mean cruising speed on every inter-stop segment traversal during that day, producing a uniformly slower or faster corridor for that run without segment-level variation beyond the calibrated baseline. This generator provides the baseline stochastic variability in inter-stop travel time when the weather generator is inactive.
```

**Before (Weather-Induced Anomalies):**
```latex
The lognormal is chosen to model the shape that any such heavy-tailed disruption produces on per-segment travel time, regardless of its meteorological label. The disturbance intensity sweep is therefore read as a span of travel-time variability magnitudes, not as a sweep across named weather categories.
```

**After (Weather-Induced Anomalies):**
```latex
The lognormal is chosen to model the shape that any such heavy-tailed disruption produces on per-segment travel time, regardless of its meteorological label. In implementation, when $\eta > 0$ a fresh travel-time sample $T \sim \text{LogNormal}(\mu_{ln}, \sigma_{ln})$ is drawn independently for each bus at each inter-stop segment traversal during the episode, replacing the traffic-speed generator's output for that traversal; the lognormal parameters $\mu_{ln}$ and $\sigma_{ln}$ are computed from the segment's empirical mean $\mu$ and the swept $\eta$ via Equations~\eqref{eq:sigma_ln}--\eqref{eq:mu_ln}. The disturbance intensity sweep is therefore read as a span of travel-time variability magnitudes, not as a sweep across named weather categories.
```

**Before (Bus Breakdowns):**
```latex
Breakdowns are triggered at random times sampled from a Poisson process with a configurable rate $\lambda$ (Table~\ref{tab:notation}). When a breakdown occurs at bus $b_k$, $b_k$ is removed from the active agent set...
```

**After (Bus Breakdowns):**
```latex
Breakdowns are triggered at random times sampled from a Poisson process with a configurable rate $\lambda$ (Table~\ref{tab:notation}). In implementation, at each discrete simulation timestep of length $dt$, a Bernoulli trial with probability $\lambda \cdot dt$ is evaluated independently for each active bus; a success removes that bus from the active agent set for the remainder of the simulated day. When a breakdown occurs at bus $b_k$, $b_k$ is removed from the active agent set...
```

**Why:** RTC comment 20 — explain in detail how each disturbance scenario is simulated.

---

## 2026-08-06 — E4C21 — methods.tex, Sections 3.2.9 and 3.2.7
**Commit:** `01c49bf`

**Before (3.2.9 opening):**
```latex
\subsection{Data Analysis Methods}

For each (control strategy, disturbance level) cell, $N \geq 30$ independent Monte Carlo runs are executed using matched random seeds across strategies. Three response variables are logged per run: mean passenger waiting time, mean total travel time, and headway coefficient of variation.
```

**After (3.2.9 opening):**
```latex
\subsection{Data Analysis Methods}

The three response variables logged per run are defined as follows. \textbf{Mean passenger waiting time} ($\bar{W}$) is the average time elapsed from a passenger's arrival at a stop to their successful boarding, averaged across all passengers served and all stops over one simulated operating day:

\begin{equation}
\bar{W} = \frac{1}{P} \sum_{p=1}^{P} \left(t_p^{\text{board}} - t_p^{\text{arrive}}\right)
\label{eq:waiting_time}
\end{equation}

where $P$ is the total number of passengers served in the run and $t_p^{\text{board}}$, $t_p^{\text{arrive}}$ are the boarding and arrival times of passenger $p$. \textbf{Mean total travel time} ($\bar{T}$) is the average elapsed time from a bus's departure from the origin terminal to its arrival at the final stop of the sub-corridor, averaged across all bus trips completed during the simulated day. \textbf{Headway coefficient of variation} ($CV_h$) measures headway regularity:

\begin{equation}
CV_h = \frac{\sigma_h}{\mu_h}
\label{eq:headway_cv}
\end{equation}

where $\sigma_h$ and $\mu_h$ are the standard deviation and mean of observed inter-bus headways recorded at all stops over one simulated operating day. $CV_h = 0$ denotes perfectly regular headways; larger values indicate increasing bunching severity. This construction mirrors the baseline coefficient of variation $CV_0$ already defined for travel time (Table~\ref{tab:notation}), applied here to the headway distribution instead.

For each (control strategy, disturbance level) cell, $N \geq 30$ independent Monte Carlo runs are executed using matched random seeds across strategies. Three response variables are logged per run: mean passenger waiting time, mean total travel time, and headway coefficient of variation.
```

**Before (3.2.7 State Space, end of bullet list):**
```latex
\item \textbf{Environmental flags:} encoded indicators for the current disturbance intensity and any active downstream incident or breakdown.
\end{itemize}

\subsubsection{Action Space ($A_i$)}
```

**After (3.2.7 State Space, end of bullet list):**
```latex
\item \textbf{Environmental flags:} encoded indicators for the current disturbance intensity and any active downstream incident or breakdown.
\end{itemize}

\begin{table}[htbp]
\centering
\caption{Agent observation vector: features, symbols, and data sources.}
\label{tab:observation-features}
\small
\renewcommand{\arraystretch}{1.25}

\begin{tabularx}{\textwidth}{
>{\RaggedRight\arraybackslash}p{0.24\textwidth}
>{\RaggedRight\arraybackslash}p{0.11\textwidth}
>{\RaggedRight\arraybackslash}X
>{\RaggedRight\arraybackslash}X
}

\toprule
\textbf{Feature} & \textbf{Symbol} & \textbf{Deployment Source} & \textbf{Simulation Source} \\
\midrule

Control stop index & --- & Route map (static) & Hardcoded stop list \\
Forward headway & $h^-$ & AVL feed & Event-driven bus model \\
Estimated backward headway & $\hat{h}^+$ & AVL feed & Event-driven bus model \\
Onboard passenger count & --- & APC system & Running tally in bus model \\
Waiting passenger count at stop & --- & AFC terminal / platform sensors & Stop queue in bus model \\
Disturbance intensity flag & $\eta$ (encoded) & Weather API / public incident alert & Active generator parameter \\
Downstream incident / breakdown flag & $b$ (binary) & Incident management system & Breakdown generator output \\

\bottomrule
\end{tabularx}
\end{table}

In simulation, all observation features are generated synthetically by the Python environment at each control event by querying the analytical bus model and the active stochastic generators; no real sensor data is consumed during training or evaluation.

\subsubsection{Action Space ($A_i$)}
```

**Why:** RTC comment 21 — metric definitions and observation-feature descriptions.

---

## 2026-08-06 — E1C1+E2C5+E4C22 — REVERTED, no net change
**Commit:** `01c49bf` (added and reverted within the same uncommitted working state; the pushed commit contains no trace of this)

**Before / After (identical — net zero diff):**
```latex
\item \textbf{Corridor bus operational data.} A per-trip record of EDSA Carousel bus operation along the study sub-corridor, collected over a continuous observation window of at least two weeks. ...The baseline operating point for this study is established from a crowdsourced operational record collected from the EDSA Busway during July 2023 through the SafeTravelPH mobile application.

%A crowdsourced operational dataset of this form, for example, data collected from the EDSA Busway via the SafeTravelPH mobile application, provides a representative model of the required structure. Should bus-volume coverage prove insufficient for the GEH validation step, supplementary records may be requested from MMDA, DOTr, or the involved bus operators under the Freedom of Information process.

\end{itemize}

Severe-weather conditions are not estimated from operational data in this study but are injected as a controlled experimental variable, with disturbance magnitudes anchored to validated literature values rather than to a corridor-specific severe-weather sample.
```

**Why:** A "Dataset Description" paragraph + field table were drafted for this section, then reverted before commit — the group does not have dataset access yet, and the draft asserted qualitative claims about the dataset's structure that aren't yet warranted. Full detail on what was drafted and why it was pulled is in `TRACKER.md`.

---

## 2026-08-06 — Citation fix: Patil2025Conformal — methods.tex, Section 3.2.6
**Commit:** not yet committed

**Before:**
```latex
Travel time is drawn as $T \sim \text{LogNormal}(\mu_{ln}, \sigma_{ln})$. Patil et al.~\cite{Patil2025Conformal} validated this parameterization against INRIX freeway data via the Kolmogorov-Smirnov test, reporting a close fit at the highest variability level they tested ($KS = 0.036$, $p = 0.94$ at $CV = 1.0$).
```

**After:**
```latex
Travel time is drawn as $T \sim \text{LogNormal}(\mu_{ln}, \sigma_{ln})$. Patil et al.~\cite{Patil2025Conformal} tested this parameterization by generating SUMO-simulated travel times under the same CV-driven lognormal recipe --- with time windows and mean travel times anchored to INRIX historical data for an urban arterial corridor, not a freeway --- and confirming via the Kolmogorov-Smirnov test that the simulated distribution matches the assumed log-normal shape, reporting a close fit at the highest variability level they tested ($KS = 0.036$, $p = 0.94$ at $CV = 1.0$).
```

**Why:** Verified against the actual PDF (RRL/Travel_Time_and_Weather-Aware...pdf). The paper's Table V classifies its route as "Local, Minor/Principal Arterials," not freeway; the KS test checks the simulated distribution's shape, not a direct INRIX comparison. The numeric KS/p values were confirmed correct.

---

## 2026-08-06 — Citation fix: Rodriguez2023Cooperative — methods.tex, Section 3.2.7
**Commit:** not yet committed

**Before:**
```latex
The full action set is the Cartesian product of these two components: $|A_i| = 5 \times 2 = 10$ discrete actions per control event. A continuous holding parameter $\alpha \in [0, 1]$ was considered, following Wang and Sun~\cite{Wangsun}, but rejected for three reasons. First, continuous actions require actor-critic algorithms, whose training instability compounds across the swept-disturbance evaluation budget. Second, Rodriguez et al.~\cite{Rodriguez2023Cooperative} showed that a 5-bin discretization of $\alpha$ achieves combined holding-and-skipping control on a comparable corridor without measurable loss of performance versus continuous formulations. Third, real driver compliance with second-level holding instructions is itself coarse \cite{Rodriguez2023Cooperative}, so continuous precision in $\alpha$ is not meaningful at deployment.
```

**After:**
```latex
The full action set is the Cartesian product of these two components: $|A_i| = 5 \times 2 = 10$ discrete actions per control event, allowing the agent to select a holding strength and a skip decision independently at each control event. This is a broader action space than Rodriguez et al.~\cite{Rodriguez2023Cooperative}, whose combined holding-and-skipping controller (DDQN-HA) instead selects among six \textit{mutually exclusive} actions: five holding strengths $\Omega = \{0.0, 0.1, 0.2, 0.3, 0.4\}$ (with $\omega = 0$ already covering the no-holding case) plus a single skip action. The discretized holding-strength set $\Omega$ adopted here matches theirs exactly. A continuous holding parameter $\alpha \in [0, 1]$ was considered, following Wang and Sun~\cite{Wangsun}, but rejected for two reasons. First, continuous actions require actor-critic algorithms, whose training instability compounds across the swept-disturbance evaluation budget. Second, real driver compliance with holding instructions is itself imperfect: Rodriguez et al.~\cite{Rodriguez2023Cooperative} model non-compliant drivers as departing after only 60--80\% of the instructed holding time, so continuous precision in $\alpha$ is not meaningful at deployment.
```

**Why:** Verified against the actual PDF (RRL/Cooperative bus holding and stop-skipping...pdf). No continuous-vs-discrete comparison exists anywhere in the paper — that claim was unsupported. Rodriguez's actual action space is 6 mutually-exclusive actions, not this study's 10-action independent Cartesian space. Kept the thesis's own $|A_i|=10$ design unchanged (it's load-bearing elsewhere in the manuscript); only corrected what is attributed to Rodriguez.

---

## 2026-08-06 — Citation fix: Wangsun — methods.tex, Section 3.2.6
**Commit:** not yet committed

**Before:**
```latex
The baseline empirical transit demand is perturbed each episode by a scaling factor sampled from $\mathcal{N}(1, \sigma_d^2)$, clipped to $[1, 3]$, following Wang and Sun~\cite{Wangsun}. The asymmetric clip focuses the test on demand surges rather than symmetric variation, since demand drops produce lightly loaded conditions that do not stress-test the controller. The upper bound of 3 corresponds to roughly a tripling of baseline boarding rates, spanning the range observed during major event let-outs and severe-weather mode shifts. Sampling occurs...
```

**After:**
```latex
The baseline empirical transit demand is perturbed each episode by a scaling factor sampled from $\mathcal{N}(1, \sigma_d^2)$ and clipped to $[1, 3]$, following the general Gaussian-clipped demand-scaling mechanism of Wang and Sun~\cite{Wangsun}, though this study adopts a narrower clip than their $[1, 10]$ range. The asymmetric clip focuses the test on demand surges rather than symmetric variation, since demand drops produce lightly loaded conditions that do not stress-test the controller. The upper bound of 3, corresponding to roughly a tripling of baseline boarding rates, is this study's own choice (\%TODO-VAL: revisit against Wang and Sun's wider range during implementation) rather than a value drawn from prior work. Sampling occurs...
```

**Why:** Verified against the actual PDF (RRL/Robust_Dynamic_Bus_Control...pdf). Their Eq. 22 clips the demand scaling factor to $[1,10]$, not $[1,3]$ — the manuscript's specific bound and its "event let-outs" justification were not supported by the source.

---

*Nothing follows.*
