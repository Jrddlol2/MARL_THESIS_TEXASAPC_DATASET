# Figure captions (LaTeX-ready)

Titles are no longer baked into the figures — use these as the `\caption{...}` in the manuscript. Every
figure is written as a vector **`.pdf`** (for `\includegraphics`) and a 300-dpi **`.png`** (for slides).
Data-cleaning figures: `starter/results/figures/datacleaning/`. Results/MARL figures:
`starter/results/figures/`.

## Data-cleaning figures

**fig_funnel** — Data-cleaning funnel for the CapMetro APC dataset. Six sequential rules reduce the
9{,}197{,}694 raw stop-event records to the 229{,}421 belonging to Route~801, direction~6: route
selection, operating-route matching, the two import-error gates, a valid stop identifier, and the
direction filter. Parenthesised values are the records removed at each step.

**fig_route_selection** — Route and direction selection. (Left) total boardings by route; Route~801
(orange) is the highest-ridership Rapid corridor. (Right) Route~801 boardings by direction; direction~6
(orange) is the study direction, contributing the 229{,}421 clean stop-events analysed here.

**fig_distributions** — Distributions of dwell time, segment revenue time, and boardings for the raw
Route~801 records (grey) versus the cleaned direction-6 subset (blue), each clipped at the axis maximum.
The pronounced right tails motivate both the cleaning filters and the use of the median (dashed line)
rather than the mean for the dwell, running-time, and distance parameters.

**fig_demand_profile** — Per-stop demand profile along the 26-stop corridor in travel order: mean
boardings (bars) and mean alightings (line). The five designated control stops are highlighted in
orange; demand concentrates at the onset of high-ridership segments, which the §3.2.2 control-stop
criteria target.

**fig_corridor_map** — Geographic layout of the 26 direction-6 stops (longitude, latitude), connected in
travel order; marker area is proportional to mean boardings and the five control stops are shown in
orange.

**fig_exclusions** — Composition of the records removed within Route~801, by cleaning rule: operating
route not equal to the scheduled route, import errors, trip-import errors, unknown stop identifier
(\texttt{bs\_id}$=0$), and the wrong travel direction.

**fig_temporal** — Temporal coverage of the cleaned direction-6 subset: stop-events per month across the
July--December 2021 window (184 service days).

## Results and MARL figures

**calibration_validation** — Corridor calibration. Simulated (SUMO) versus observed (APC) segment
running times for the 25 corridor segments; points lie on the identity line (dashed). Calibration meets
GEH $<5$ on all segments at a travel-time RMSPE of $0.75\%$.

**mc_headway_cv** — Headway coefficient of variation (bunching) by scenario for No-Control (NC),
Forward-Headway (FH), and Even-Headway (EH), over $N=30$ matched-seed replications; error bars are
$95\%$ bootstrap confidence intervals. Both controllers reduce irregularity under mild disturbance, but
the advantage vanishes under the combined Stage-B regime.

**mc_wait** — Mean passenger waiting time by scenario for NC / FH / EH ($N=30$ matched seeds; $95\%$
bootstrap CIs), computed as the expected wait under random passenger arrivals given the realised bus
headways.

**marey_diagram** — Time--space (Marey) trajectories of the fleet over the corridor for No-Control and
Even-Headway under Stage~A (D+T) and Weather (D+T+W), one representative seed; horizontal lines mark the
control stops. Converging trajectories indicate bunching, which holding acts to re-space.

**degradation_curve** — Degradation of headway control with weather severity. Mean headway CV for
NC / FH / EH as the weather-intensity parameter $\eta$ (the coefficient of variation of the lognormal
speed factor) increases; error bars are standard errors over $N=12$ seeds per point. The control
advantage narrows as $\eta$ grows.

**gate1_convergence** — MARL fail-fast gate convergence over training episodes: (left) per-agent episode
return and (right) per-episode headway CV, each with a 15-episode running mean. Dashed lines mark the
No-Control and Forward-Headway baselines.

**gate1_curve** — MARL learning curve for the fail-fast gate: exploring per-episode training CV and
greedy evaluation CV against the No-Control and Forward-Headway baselines; the right axis shows the
exploration rate $\varepsilon$.
