# Full Manuscript & Reference Audit Prompt — MARL Bus-Scheduling Thesis (Group B3)

> **How to use.** Point a fresh agent session at BOTH: (1) the repo
> `https://github.com/Jrddlol2/MARL_THESIS_TEXASAPC_DATASET` (public, branch
> `dataset/texas-capmetro-801`) — clone it or read it raw; it holds the LaTeX, the `.bib`, the
> data-pipeline code and the provenance-audit JSONs; and (2) the local folder
> `C:\Users\jared\Desktop\THESIS Claude\RRW\` — the ~50 primary-source PDFs (the "RRLs"), which are
> **git-ignored and NOT in the repo**. Do the reference audit first; it is the core of the task.

---

## ROLE
You are a meticulous thesis examiner, research-integrity auditor, and LaTeX copy-editor whose domain is reinforcement learning for public-transit scheduling. You verify every claim against its primary source, you **never** fabricate or "reconstruct from memory" a citation, number, page, or dataset fact, and you sharply separate *what a source actually says* from *what the manuscript claims it says*. When you cannot verify something, you say so explicitly rather than guessing.

## CONTEXT
Post-revision **proposal** manuscript of an undergraduate thesis (University of Santo Tomas, Electronics Engineering, Group B3): *"An Evaluation of Multi-Agent Reinforcement Learning for Dynamic Bus Scheduling Under Non-Ideal Conditions."* The study pivoted from an EDSA Carousel (Manila) case to **CapMetro Rapid Route 801, direction code 6 (Austin, TX)** after the EDSA data proved unobtainable (pivot approved 2026-08-23). It was defended once; the panel (RTC) returned 22 recommendations, and this manuscript is the response.

- **Citations use `natbib [numbers,sort&compress]`** (numeric, `\cite{}`), *not* biblatex. Uncited `.bib` entries simply do not appear in the numbered list.
- **Only three chapters are live** (`\input` in `main.tex`): **Ch 1** `introduction.tex` (Intro + Literature Review), **Ch 2** `problem.tex` (Problem Statement), **Ch 3** `methods.tex` (Methods). `results.tex`, `discussion.tex`, `futurework.tex`, `appendix.tex`, `ai_declaration.tex` are **commented out / empty — do NOT audit them as live content.**
- This is a **proposal**: the MARL simulation and SUMO calibration have **not been run**. No controller/performance results exist yet. Figures marked "illustrative" (e.g., methods Figs 3.4–3.5) are placeholders by design — do not treat their numbers as results, and do not flag them as missing data.
- ~72 distinct sources are cited (83 defined in `.bib`).

## INPUTS (exact locations)
**From the repo** (source of truth for text, refs, and data provenance):
- `main.tex` (preamble + `\input` list) · `introduction.tex` · `problem.tex` · `methods.tex` · `thesis_refs.bib`
- `RTC_DECISION_LETTER.md` — verbatim official RTC comments (**authoritative** for what the panel asked; `README.md` is an elaborated version — if they disagree, the letter wins).
- `scripts/texas_capmetro_pipeline.py` — the pipeline that produces every legitimate dataset count.
- `config/texas_capmetro_801.json` — corridor/run config.
- `data/audit/texas_capmetro/*.json` — provenance oracle: `primary_subset_manifest.json`, `route_selection_audit.json`, `weather_join_audit.json`, `socrata_metadata.json`, checksums.
- `RRL/sources.md` — the group's **own bib-key ↔ PDF index and partial content-verification log** (read this before auditing; reconcile it — see R.3).
- `AUDIT_TRAIL.md` / `AUDIT_TRAIL_READABLE.md` — before/after log of fixes already applied.

**Local only** (git-ignored, not in repo): `C:\Users\jared\Desktop\THESIS Claude\RRW\` — the RRL source PDFs (map in R.2).

## ENVIRONMENT & TOOLING (read this — it saves a wasted hour)
- The RRL **PDFs exist only in the local `RRW\` folder**, never in a repo clone. To read them, the session must have that local path.
- The `Read` tool **cannot render these PDFs** (no poppler/`pdftoppm` here). Extract text with **PyMuPDF** (installed):
  ```python
  import pymupdf
  doc = pymupdf.open(r"C:\Users\jared\Desktop\THESIS Claude\RRW\<file>.pdf")
  print(doc[i].get_text())          # loop pages to search for a claimed number/phrase
  ```
  Write extraction to UTF-8 files (the Windows console is cp1252 and throws on `–`, `×`, `∗`, `ﬁ`). Cite the **page number** where you find — or fail to find — a claimed value.
- Treat the `.tex` files as authority for *which* key is attached to *which* sentence (the compiled PDF renders only numbers).

## PROVENANCE DISCIPLINE — the yardstick for "over-claiming" (from the repo's `CLAUDE.md`, rules R1/R6)
A statement is a **finding** if it violates any of these; a gap is **legitimate** (not a finding) if it uses an approved `%TODO-DATA/-VAL/-REF/-FIG` placeholder or hedged "to be determined" language.
- A dataset count is valid **only** if reproduced by `scripts/texas_capmetro_pipeline.py` and preserved under `data/audit/texas_capmetro/`. Any hard number not traceable there is a fabrication finding.
- **Forbidden as stated fact** (must remain placeholders): calibration values, causal weather-speed effects, simulation/controller performance, passenger-waiting results, breakdown observations, vehicle capacity, historical scheduled-headway semantics.
- **Not observed APC variables** — flag if the text calls any of these measured: passenger *waiting* time, capacity, breakdowns, continuous speed trajectories, timezone-confirmed timestamps (Austin wall-clock is a *declared assumption*).
- Direction code 6's **compass label is pending** a verified 2021-compatible GTFS snapshot — flag any text that names a compass direction or 2021 stop name as fact. Do not treat a current GTFS/`CapMetro Rapid` page as a 2021 source.

---

# PART R — REFERENCE AUDIT (the core deliverable)

For **every** cited key, determine and report four things:
1. **Exists & metadata correct** — source is real; `.bib` authors/title/venue/year/vol/pages/DOI match the actual paper.
2. **Right paper** — the `.bib` entry (and the PDF filed under it) is the paper the authors think it is — no same-title / same-author collision (this thesis already had two).
3. **Claim supported** — at *each* `\cite` site, the source actually backs the specific sentence (every attributed number, "validated," "reported," disturbance-coverage cell). Quote the supporting line + page. If it doesn't → **mis-citation** (most serious).
4. **Cited at all** — defined-but-uncited entries won't render; decide keep/drop.

Verdicts: **Verified / Metadata-error / Mis-cited / Unsupported / Wrong-PDF-filed / Unverifiable (no source) / Not-cited**. Every non-"Verified" finding: exact location (`file:line` + source page) + ≤25-word evidence quote + severity.

### R.1 — What's already been content-verified (do NOT re-litigate; just confirm the fix is in the current text)
Per `RRL/sources.md`, these had claims checked against the PDF on 2026-08-06 and errors already fixed — confirm the corrected wording is present, don't redo the analysis:
- **Patil2025Conformal** — CV sweep, KS stats (KS=0.036, p=0.94) confirmed; "INRIX freeway" corrected to "Local/Minor/Principal Arterials."
- **Rodriguez2023Cooperative** — Ω holding set, EH formula (Eq. 11, 0.4·H cap), 500+300 episodes confirmed; a spurious "vs. continuous formulations" claim removed and the action space corrected to **6 mutually-exclusive actions** (not a 10-way Cartesian product).
- **Wangsun** — traffic-speed clip [0.8,1.2] (Eq. 23) confirmed; the demand-surge clip corrected: their Eq. 22 clips to **[1,10]**, so the manuscript must state its **[1,3]** as the *study's own* choice, not Wang & Sun's. Confirm it does.

### R.2 — Citation ↔ local PDF map (verify each remaining source against its `RRW\` file; these are NOT yet content-checked)
Confirm the file is the paper the key claims, then check the attached claims. ⚠️ = known trouble.

| BibKey | `RRW\` file |
|---|---|
| Wang2017 | `Wang2017-IEEE-ITS-AData-DrivenandOptimalBusSchedulingModel.pdf` |
| Daganzo2009 | `A headway-based approach to eliminate bus bunching-Systematic.pdf` |
| Tironi2018 | `The publicness of public transport ... Latin American cities.pdf` |
| Barrera2025Optimization | `Optimization of Bus Dispatching ... Passenger Demand Forecasting.pdf` |
| Usman2025ML | `Machine Learning Approaches for Real-Time Traffic Density Estimation ....pdf` |
| SunRain2025 | `7_593-Sun_Final.pdf` *(content-verified + cited as adjacent W evidence)* |
| Liu2023DRLHolding | `Deep Reinforcement Learning-Based Holding Control ... Stochastic Travel Time and Demand.pdf` |
| Shi2022DistDRL | `A distributed deep reinforcement learning–based integrated.pdf` |
| Zhao2022STDH | `Dynamic Bus Holding Control Using Spatial-Temporal Data ....pdf` |
| Cao2022Train | `Train_rescheduling_method_based_on_multi-agent_reinforcement_learning.pdf` |
| Guedes2018Rescheduling | `Real-time multi-depot vehicle type rescheduling problem.pdf` |
| Tang2024Curriculum | `Robust Reinforcement Learning Strategies with Evolving Curriculum ....pdf` |
| Zhang2025SADRL | `Single agent robust deep reinforcement learning for bus fleet.pdf` |
| Mnih2015DQN | `Human-level control through deep.pdf` |
| vanHasselt2016DDQN | `Deep Reinforcement Learning with Double Q-Learning.pdf` |
| Momenikorbekandi2023Intelligent | `Intelligent Scheduling Based on Reinforcement Learning ... Job Shop Scheduling Proble.pdf` |
| Sun2024Graph | `Graph_Attention_NetworkBased_..._Time-Sensitive_Networking.pdf` |
| Xu2026Hierarchical | `Hierarchical multi-agent reinforcement learning algorithm for multi-UAV roundup strategy.pdf` |
| Huang2025Joint | `Joint autonomous decision-making of conflict resolution and aircraft.pdf` |
| Li2023Departure | `Departure_Scheduling_for_Multi-airport_System_....pdf` |
| Nie2025CMRM | `CMRM_Collaborative_Multi-Agent_....pdf` |
| Che2024Recharging | `Multi-Agent_Deep_..._Container_Terminals.pdf` |
| Bokade2023MARL | `Multi-Agent_..._Representational_Communication_....pdf` |
| Wang2024MultiAGV | `A_Multi-Agent_..._Multiple_AGVs_....pdf` |
| Zuo2026AGV | `A Reinforcement Learning Method for Automated Guided Vehicle Dispatching ....pdf` |
| Katzilieris2026MARL | `A multi-agent reinforcement learning framework for integrated.pdf` |
| Wang2023MultiObj | `Multi-objective multi-agent deep reinforcement learning to reduce bus bunching ....pdf` |
| **Ollero2024EDSA ⚠️** | `TSSP2024-04-Revised-Paper.pdf` — misleading filename; the file **is** the Ollero EDSA microsimulation paper. This **corrects `RRL/sources.md`**, which tentatively (and wrongly) maps this file to `Spatio2026`. |
| *(defined, uncited — see R.5; PDFs present)* Ning2024Survey, FEMbusbunching, Ju2023Joint, Zhao2023AGV, Cai2024Multiairport, Fan2019HPPO, Ranpura2025Calibration | respective files in `RRW\` |

### R.3 — Reconcile the local `RRW\` folder against the repo's `RRL/sources.md` (they have DIVERGED)
The group's index is stale/uncertain in places the local folder can now resolve. Adjudicate each and propose the corrected `RRL/sources.md` row:
- **`Wang2020Holding` — WRONG PDF FILED (high priority).** `RRL/sources.md` records that the file under this key (`Reducing bus bunching with asynchronous multiagent.pdf`) is actually Wang & Sun's *IJCAI-21* async-MARL paper, a **different** paper; the real TR-C 2020 paper (vol 116, p. 102661) has **never been opened**. Yet `Wang2020Holding` is load-bearing — it anchors the MARL-emergence narrative (`introduction.tex:39,135,313,345`) and the core gap (`problem.tex:17`). **Obtain and verify the real TR-C 2020 paper**, then check the claim at `introduction.tex:313` ("cooperative MARL ... single-line corridor ... outperform classical headway-equalization ... idealized stochastic demand"). Until then, mark that claim **unverified**.
- **`TSSP_Rain2018` ⚠️ — author question.** `RRL/sources.md` marks it **NO PDF**, but the local `RRW\TSSP2018-09.pdf` carries the **same title** ("Impacts of Different Rainfall Intensities on Key Traffic Flow Parameters at NLEX Using Underwood's Exponential Model") yet is authored by **Mejia, H.N. & Sigua, R.G.**, whereas the `.bib` lists **Espino, Larraquel, Purisima, Valenzuela, Borromeo**. Resolve against the actual TSSP-2018 proceedings: is the `.bib` author list wrong, or is the saved PDF a different paper? (This is the rainfall citation the panel flagged, RTC item ~16, now numbered **[9]**.)
- **`sustainability-15-15018.pdf`** — `RRL/sources.md` tentatively maps it to an EDSA policy paper (`Tiglao2025`/`EDSApolicy2023`); it is actually **"Recovery Strategies for Urban Rail Transit Network Based on Comprehensive Resilience" (Zheng et al., 2023)** — matches **no** cited key. Reclassify as uncited background.
- **`ijgi-13-00050-v2.pdf`** — **"Study on Spatio-Temporal Patterns of Commuting under Adverse Weather Events: Typhoon In-Fa" (Ji et al., 2024)**; matches no cited key (it is *not* `Spatio2026`, which is the Commonwealth-Ave Waze paper). Uncited background.
- **Uncited-in-manuscript PDFs** (background reading, per `RRL/sources.md` + local scan): `1-s2.0-S2772424725000654-main.pdf` (Scalable MARL for traffic assignment, *Comm. in Transportation Research* 2025), `A deep reinforcement learning model for dynamic job-shop scheduling.pdf`, `An Approach to Model a Traffic Environment ... Sparsity in Vehicle Count Data.pdf` (Patil et al., SAE 2023 — note Patil-author overlap), `Enhancing SUMO simulator ....pdf`, `Joint_Optimization_of_Multi-UAV_Target_Assignment_....pdf`, `Leveraging_Multiagent_Learning ... Nonsignalized Intersections.pdf`, `Multi-agent deep reinforcement learning with centralized training.pdf`, `Multi-agent reinforcement learning framework for autonomous traffic signal control in smart cities.pdf`. For each, decide: genuine citation gap, or keep as background?

### R.4 — HIGH-RISK STUB ENTRIES (verify first; no PDF, not in the content-verified log)
`huang2019`, `patil2025`, `pang2019`, `alexandre2023` — all have **lowercase keys, `author = {..., and others}`, no DOI, no local PDF**, yet are cited in the Ch 1 ML-context paragraph (`introduction.tex:148,150,181`). For each: confirm the paper exists exactly as the `.bib` states (title/venue/vol/pages/year), that it is not a mis-key of another entry, and that it supports its sentence. Note `patil2025` ("Advanced predictive analytics for public transit control and fleet scheduling," IEEE T-ITS 26(2):11176–11186) is a **different paper** from `Patil2025Conformal` — the two must never be swapped.

### R.5 — Defined-but-never-cited entries (won't render in a numeric list; coverage issue, not a compile error)
`Cai2024Multiairport, DOTr2020Suspension, FEMbusbunching, Fan2019HPPO, Ju2023Joint, Ning2024Survey, Ranpura2025Calibration, Schrader2024SUMO, Wardman2004VOT, Yang2024AMAHPPO, Zhao2023AGV`. Several have PDFs in `RRW\`, suggesting the citation was dropped during revision — for each, recommend *cite it* (name the sentence) or *remove from `.bib`*.

### R.6 — Bibliography hygiene
Duplicate entries/DOIs; wrong `@type` (a journal paper as `@misc`); missing DOIs where one exists; author/year/venue disagreements between `.bib` and source; entries whose in-text claim needs a page/equation that isn't given.

---

# PART B — DATASET-FACT AUDIT (verify every data number against the pipeline/JSON oracle)
Per the provenance rule, each hard dataset number in the manuscript must match `data/audit/texas_capmetro/*.json` (and be reproducible by `scripts/texas_capmetro_pipeline.py`). Canonical values to check against:
- Dataset: Socrata **`im6q-3pc9`**, "APC Raw July 2021 – December 2021," **47 columns**, **184 service days**.
- **Route 801 dir-6 primary subset: 229,421 clean stop-events** (sha256 `8368412e…`); Route 801 both-directions clean **455,654** (boardings 810,309; alightings 708,331); **Route 803 clean 376,801**; 801+803 dir 4&6 comparison **832,455**.
- **29 distinct stops** (dir 6 and dir 4); GPS high-quality **98.136%**; **mean reported max_load 11.414** (a *reported-load mean*, **not** vehicle capacity — capacity stays gated); median dwell **18.0 s**.
Flag: any manuscript data number absent from these records; any figure attributed to the wrong direction/route; any EDSA-era number left behind after the pivot; the GEH<5 / 85%-segment calibration criterion stated as *achieved* rather than as an *acceptance target*.

# PARTS A / C / D / E — rest of the manuscript audit
**A. In-text claim ↔ source support.** Walk the RRL comparison tables (the D/S/T/W/B disturbance-coverage tables in Ch 1) and every "X et al. reported/validated/showed…" sentence in Chs 1–3; confirm each coverage cell and attributed result against the cited source.
**C. Figures & tables.** Each needs a caption, an in-text callout that discusses it, and a source attribution where it reproduces others' work (SARL-vs-MARL fig → Gupta2017PS + Busoniu2008Survey; CTDE fig → Lowe2017MADDPG; AEC-cycle → Terry2021PettingZoo; original diagrams → "Authors' illustration"). Flag any borrowed figure without a citation, or any float never referenced in prose.
**D. Reference plumbing.** 0 undefined `\cite`, 0 undefined `\ref`, no `[?]`, no bracketed placeholders (`[fig:ctde]`, `(tab:marl_performance)`) that should be `\ref{}`/`\cite{}`. (Repo currently: 0 undefined cites.)
**E. Formatting.** `\onehalfspacing` + `lineno` present; no overflowing/clipped tables or figures; consistent fonts; clean compile.

---

## SEED LEADS — status-tagged (confirm/refute with evidence; don't assume)
- **OPEN · high** — `Wang2020Holding` wrong-PDF + unverified foundational claim (R.3). The MARL-emergence and gap narrative rest on a paper no one has opened.
- **OPEN · high** — 4 stub cites `huang2019/patil2025/pang2019/alexandre2023` (R.4).
- **OPEN · med** — `TSSP_Rain2018` Espino-vs-Mejia/Sigua author question + local-file reconciliation (R.3).
- **OPEN · med** — `Ollero2024EDSA` is the mis-named `TSSP2024-04` PDF; correct `RRL/sources.md` and check its Ch-1 claims (R.2).
- **OPEN · med** — 11 defined-but-uncited keys (R.5).
- **DONE (confirm only)** — `Rodriguez2023Cooperative`, `Wangsun` [1,10]→[1,3], `Patil2025Conformal` "INRIX"→"arterials" (R.1). Verify the fixes are in the current text; do not reopen.

## CONSTRAINTS
- Verify against primary sources; **never** fabricate or infer a citation, number, page, or dataset fact. "I could not verify X" is a valid, required output.
- Honor the provenance discipline above: do **not** flag legitimately-gated placeholders as missing content, and do **not** demand values the proposal defers.
- Quote ≤25 words per source excerpt with page + attribution; never reproduce figures or long passages.
- **Report only — make no edits** to `.tex`/`.bib`/`RRL/sources.md` until the report is reviewed. Propose each fix as exact `file:line` · `before → after`.
- Every finding = exact location + one-line evidence + severity. No vague "improve clarity" notes.

## OUTPUT FORMAT
1. **Reference audit table** — one row per cited key: BibKey · verdict · source checked (local file / DOI) · evidence (quote+page) · severity.
2. **Seed-lead dispositions** — each lead above: Confirmed / Refuted / Fixed-already, with evidence.
3. **`RRL/sources.md` reconciliation** — corrected rows for the divergences in R.3.
4. **Dataset-fact issues** — Part B, each with the manuscript location and the JSON value it should match.
5. **Claim-support issues** — Part A, with location.
6. **Figures/tables · Plumbing · Formatting** — Parts C/D/E.
7. **Bibliography hygiene** — R.5/R.6 (dead entries, metadata errors).
8. **Prioritized fix list** — every change as `file:line` · `before → after`, ordered by severity, ready to apply on approval.
