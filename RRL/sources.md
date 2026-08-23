# RRL Source Index — bib key ↔ local PDF
# Maps thesis_refs.bib citation keys to the PDF filenames in this folder,
# so specific factual/numeric claims attributed to a source can be checked
# against the actual paper instead of trusted from the .bib title alone.
# This folder (RRL/) is NOT pushed to GitHub — see .gitignore. This index
# file is the only RRL-related thing that should be tracked in git, since
# it contains no copyrighted content, only a mapping.
#
# Confidence: CONFIRMED = filename matches bib title closely, high confidence.
#             TENTATIVE = plausible match, not yet opened/verified.
#             NO PDF    = cited but no corresponding file found in RRL/.
# Update this file if you add/remove PDFs from RRL/.
#
# "Filename CONFIRMED" is not the same as "manuscript claims checked" — see
# CONTENT-VERIFIED list below for which sources have actually had their
# specific numeric/methodological claims checked against the PDF text.

| Bib key | Title (from thesis_refs.bib) | RRL filename | Confidence |
|---|---|---|---|
| Patil2025Conformal | Travel Time and Weather-Aware Traffic Forecasting in a Conformal Graph Neural Network Framework | Travel_Time_and_Weather-Aware_Traffic_Forecasting_in_a_Conformal_Graph_Neural_Network_Framework.pdf | CONFIRMED |
| Rodriguez2023Cooperative | Cooperative bus holding and stop-skipping: A deep reinforcement learning framework | Cooperative bus holding and stop-skipping- A deep reinforcement.pdf | CONFIRMED |
| Wangsun | Robust Dynamic Bus Control: A Distributional Multi-Agent Reinforcement Learning Approach | Robust_Dynamic_Bus_Control_a_Distributional_Multi-Agent_Reinforcement_Learning_Approach.pdf | CONFIRMED |
| Zuo2026AGV | A Reinforcement Learning Method for AGV Dispatching and Path Planning... | A Reinforcement Learning Method for Automated Guided Vehicle Dispatching and Path Planning Considering Charging and Path Conflicts at an Automated Container Terminal.pdf | CONFIRMED |
| Katzilieris2026MARL | A multi-agent reinforcement learning framework for integrated traffic signal control and dynamic bus lane access management | A multi-agent reinforcement learning framework for integrated.pdf | CONFIRMED |
| Wang2024MultiAGV | A Multi-Agent Deep RL Approach for Multiple AGVs Scheduling in Automated Container Terminals | A_Multi-Agent_Deep_Reinforcement_Learning_Approach_for_Multiple_AGVs_Scheduling_in_Automated_Container_Terminals.pdf | CONFIRMED |
| Zhao2023AGV | An AGV Task Scheduling Method Based on Multi-Agent Reinforcement Learning | An_AGV_Task_Scheduling_Method_Based_on_Multi-Agent_Reinforcement_Learning.pdf | CONFIRMED |
| Nie2025CMRM | CMRM: Collaborative Multi-Agent Reinforcement Learning for Multi-Objective Traffic Signal Control | CMRM_Collaborative_Multi-Agent_Reinforcement_Learning_for_Multi-Objective_Traffic_Signal_Control.pdf | CONFIRMED |
| Li2023Departure | Departure Scheduling for Multi-airport System using Multi-agent Reinforcement Learning | Departure_Scheduling_for_Multi-airport_System_using_Multi-agent_Reinforcement_Learning.pdf | CONFIRMED |
| FEMbusbunching | An overview of solutions to the bus bunching problem in urban bus systems | FEM-Anoverviewofsolutionstothebusbunchingprobleminurbanbussystems.pdf | CONFIRMED |
| Sun2024Graph | Graph Attention Network-Based Deep RL Scheduling Framework for in-Vehicle Time-Sensitive Networking | Graph_Attention_NetworkBased_Deep_Reinforcement_Learning_Scheduling_Framework_for_in-Vehicle_Time-Sensitive_Networking.pdf | CONFIRMED |
| Xu2026Hierarchical | Hierarchical multi-agent reinforcement learning algorithm for multi-UAV roundup strategy | Hierarchical multi-agent reinforcement learning algorithm for multi-UAV roundup strategy.pdf | CONFIRMED |
| Momenikorbekandi2023Intelligent | Intelligent Scheduling Based on RL Approaches... Job Shop Scheduling Problems | Intelligent Scheduling Based on Reinforcement Learning Approaches...Job Shop Scheduling Proble.pdf | CONFIRMED |
| Huang2025Joint | Joint autonomous decision-making of conflict resolution and aircraft scheduling... | Joint autonomous decision-making of conflict resolution and aircraft.pdf | CONFIRMED |
| Ju2023Joint | Joint Secure Offloading and Resource Allocation for Vehicular Edge Computing Network | Joint_Secure_Offloading_and_Resource_Allocation_for_Vehicular_Edge_Computing_Network_A_Multi-Agent_Deep_Reinforcement_Learning_Approach.pdf | CONFIRMED |
| Usman2025ML | Machine Learning Approaches for Real-Time Traffic Density Estimation and Public Transport Optimization | Machine Learning Approaches for Real-Time Traffic Density Estimation and Public Transport Optimization.pdf | CONFIRMED |
| Che2024Recharging | Multi-Agent Deep RL for Recharging-Considered Vehicle Scheduling Problem in Container Terminals | Multi-Agent_Deep_Reinforcement_Learning_for_Recharging-Considered_Vehicle_Scheduling_Problem_in_Container_Terminals.pdf | CONFIRMED |
| Bokade2023MARL | Multi-Agent Reinforcement Learning Based on Representational Communication for Large-Scale Traffic Signal Control | Multi-Agent_Reinforcement_Learning_Based_on_Representational_Communication_for_Large-Scale_Traffic_Signal_Control.pdf | CONFIRMED |
| Wang2023MultiObj | Multi-objective multi-agent deep RL to reduce bus bunching for multiline services with a shared corridor | Multi-objective multi-agent deep reinforcement learning to reduce bus bunching for multiline services with a shared corridor.pdf | CONFIRMED |
| Cai2024Multiairport | Multiairport Departure Scheduling via Multiagent Reinforcement Learning | Multiairport_Departure_Scheduling_via_Multiagent_Reinforcement_Learning.pdf | CONFIRMED |
| Barrera2025Optimization | Optimization of Bus Dispatching in Public Transportation Through a Heuristic Approach Based on Passenger Demand Forecasting | Optimization of Bus Dispatching in Public Transportation Through a Heuristic Approach Based on Passenger Demand Forecasting.pdf | CONFIRMED |
| Cao2022Train | Train rescheduling method based on multi-agent reinforcement learning | Train_rescheduling_method_based_on_multi-agent_reinforcement_learning.pdf | CONFIRMED |
| Ranpura2025Calibration | Development of Mixed Traffic Microsimulation Model Calibration for Signalized Intersections | 1-s2.0-S2352146524005258-main.pdf | **CONFIRMED (2026-08-06)** — opened and verified: Ranpura, Gujar, Singh, *Transportation Research Procedia* 82 (2025) 2898-2910, WCTR 2023 Montreal, VISSIM calibration of two Ahmedabad intersections via GEH/RMSPE. Matches bib title exactly. This corrects the earlier TENTATIVE guess below — `ijgi-13-00050-v2.pdf` is NOT this paper. |
| Spatio2026 | Spatiotemporal analysis of traffic accidents...Waze Traffic Data | TSSP2024-04-Revised-Paper.pdf | TENTATIVE (TSSP-conference-style filename, plausible venue, not opened to confirm) |
| Tiglao2025 or EDSApolicy2023 | (EDSA busway policy papers) | sustainability-15-15018.pdf | TENTATIVE (MDPI Sustainability-style filename, not opened to confirm which key) |
| Wang2020Holding | Dynamic Holding Control to Avoid Bus Bunching: A MARL Framework | Reducing bus bunching with asynchronous multiagent.pdf | **MISMATCHED (confirmed 2026-08-06)** — this PDF is actually Wang & Sun's *"Reducing Bus Bunching with Asynchronous Multi-Agent Reinforcement Learning"* (IJCAI-21, the CAAC paper), a different paper by the same authors. It is reference [9] cited *inside* the Wangsun/IQNC-M paper, not the TR-C 2020 paper this bib key names. Confirmed by reading the PDF's own title page and its reference list, which separately cites "Wang and Sun, 2020, ... Transportation Research Part C ..., 116:102661" as distinct prior work — matching the bib entry exactly (journal/vol/page/year/DOI all confirmed), meaning the *bib entry* is correctly specified but the *cached PDF* is the wrong file. No PDF of the actual TR-C 2020 paper is currently in this folder. |
| N/A — not cited | Scalable and reliable multi-agent reinforcement learning for traffic assignment (Wang, Duan, Lyu, et al.) | 1-s2.0-S2772424725000654-main.pdf | **IDENTIFIED, not in thesis_refs.bib (2026-08-06)** — Communications in Transportation Research 5 (2025) 100225. MARL for network-wide traffic *assignment* (OD-pair routing), not bus scheduling/holding; no weather modeling. Appears to be background reading, not an actual citation in the manuscript. |
| SunRain2025 | Analysis and Dynamic Prediction of Bus Dwell Time Under Rainfall Conditions (Sun, Yang, Dong, Lu, Wang) | 7_593-Sun_Final.pdf | **CONTENT-VERIFIED AND CITED (2026-08-23)** — *Promet – Traffic&Transportation* 37(1):105-121, 2025, DOI 10.7307/ptt.v37i1.593. Empirical Shenyang study of bus dwell time under measured rainfall using SVM, KNN, BP, and GA-BP prediction. Used only as adjacent W evidence; it is not RL or a bus-control baseline. |
| ??? | ??? | A deep reinforcement learning model for dynamic job-shop scheduling.pdf | UNMATCHED — no corresponding bib title found; may be background reading not cited in the manuscript |
| ??? | ??? | An Approach to Model a Traffic Environment by Addressing Sparsity in VehicleCount Data.pdf | UNMATCHED — not cited in the manuscript as far as identified |
| ??? | ??? | Enhancing SUMO simulator for simulation based testing and validation of autonomous vehicles.pdf | UNMATCHED — not cited in the manuscript as far as identified |
| ??? | ??? | Joint_Optimization_of_Multi-UAV_Target_Assignment_and_Path_Planning_Based_on_Multi-Agent_Reinforcement_Learning.pdf | UNMATCHED — not cited in the manuscript as far as identified |
| ??? | ??? | Leveraging_Multiagent_Learning_for_Automated_Vehicles_Scheduling_at_Nonsignalized_Intersections.pdf | UNMATCHED — not cited in the manuscript as far as identified |
| ??? | ??? | Multi-agent reinforcement learning framework for autonomous traffic signal control in smart cities.pdf | UNMATCHED — not cited in the manuscript as far as identified |

## CONTENT-VERIFIED (specific claims checked against the actual PDF text)

- **Patil2025Conformal** — checked 2026-08-06. CV sweep values, KS/p statistics
  ($KS=0.036$, $p=0.94$ at $CV=1.0$), and method-of-moments equations all
  confirmed accurate. Found and fixed one error: manuscript called the source
  "INRIX freeway data" — actual route is "Local, Minor/Principal Arterials"
  per the paper's Table V. See AUDIT_TRAIL.md.
- **Rodriguez2023Cooperative** — checked 2026-08-06. $\Omega$ holding-strength
  set, EH formula (Eq. 11, incl. 0.4·H cap), and training episode budget
  (500+300) all confirmed exact matches. Found and fixed one error: manuscript
  attributed an unsupported "vs. continuous formulations" comparison to this
  paper (doesn't exist in it), and mischaracterized the paper's action space
  as a 10-way Cartesian product when it's actually 6 mutually-exclusive
  actions. See AUDIT_TRAIL.md.

- **Wangsun** — checked 2026-08-06. Traffic-speed scaling clip $[0.8,1.2]$
  (Eq. 23) confirmed exact match. Table 1.2 entries (S,T disturbance coverage,
  "real-world bus services" environment) confirmed reasonable. Found and
  fixed one error: manuscript attributed a $[1,3]$ demand-surge clip to Wang &
  Sun, but their Eq. 22 actually clips to $[1,10]$; the manuscript's specific
  bound and its justifying narrative weren't in the source. See AUDIT_TRAIL.md.

- **Wang2020Holding** — checked 2026-08-06, at user's request to re-verify a
  disputed weather-coverage claim. The bib entry itself is correct (TR-C 2020,
  vol 116, p. 102661 — confirmed against the DOI and against how the CAAC
  paper's own reference list cites it). However, the PDF filed under this key
  is the wrong paper (see MISMATCHED row above) — the actual TR-C 2020 paper
  has not been opened. The manuscript's characterization of Wang2020Holding
  at introduction.tex:229 ("cooperative MARL framework ... single-line
  corridor ... outperform classical headway-equalization rules under
  idealized stochastic demand") is therefore **still unverified against the
  real source**, though it is not contradicted by anything found so far.

All other CONFIRMED-filename sources below have NOT yet had their specific
manuscript claims checked — filename matching only establishes which PDF
corresponds to which key, not that every citation is accurate.

## Cited keys with NO PDF in this folder (verify against .bib metadata only)
TSSP_Rain2018, DOTr2020Suspension, DOTr2025Ridership, Daganzo2009,
Christianos2021PS, Ollero2024EDSA, Zhang2025SADRL, Zhao2022STDH, Shi2022DistDRL,
Guedes2018Rescheduling,
Chen2016MARLBus, and most background/methods citations (Bellman1957, Littman1994,
vanHasselt2016DDQN, Mnih2015DQN, etc. — standard RL/stats references, lower
verification priority than corridor- and disturbance-specific claims).
