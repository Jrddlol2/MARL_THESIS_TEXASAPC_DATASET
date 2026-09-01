# Reference & Manuscript Audit Report — Group B3 MARL Thesis
**Date:** 2026-09-01 · **Target:** repo `Jrddlol2/MARL_THESIS_TEXASAPC_DATASET` @ `dataset/texas-capmetro-801` (live chapters `introduction.tex`, `problem.tex`, `methods.tex` + `thesis_refs.bib`) cross-checked against local `RRW\` PDFs and `data/audit/texas_capmetro/*.json`.
**Method:** PDFs opened with PyMuPDF; dataset numbers checked against the pipeline provenance JSONs; citation existence checked against the source PDFs, Crossref, and web search. No `.tex`/`.bib` edited — report only.

**Verdict in one line:** the data-provenance and figure-attribution work is solid and the numbers reconcile exactly, but there are **3 unverifiable "stub" citations**, **1 load-bearing citation resting on an unopened / wrong-filed source**, **1 wrong author list**, and **1 half-applied fix** — all concrete and fixable.

---

## 1. Findings by severity

### HIGH-1 — Three cited papers cannot be verified to exist as cited (possible fabrication/garbled metadata)
Four "stub" entries (lowercase keys, `author = {…, and others}`, no DOI, no local PDF) are cited in §1.1 to support real claims. Checked against Crossref + web:

| Key | `.bib` claims | Result |
|---|---|---|
| `alexandre2023` | *Machine learning applied to public transportation by bus: A systematic literature review*, TRR 2677(7):639–660, 2023 | ✅ **VERIFIED** — exact match (SAGE, DOI 10.1177/03611981231155189). Metadata correct. |
| `huang2019` | *Bus arrival time prediction using machine learning techniques in uncertain environments*, IEEE Access 7:93224–93235, 2019 | ❌ **UNVERIFIABLE** — no paper with this title in Crossref/web. A *different* Huang 2019 IEEE Access paper exists (different title & pages). |
| `pang2019` | *A predictive holding control strategy for bus transit reliability using real-time information*, IEEE T-ITS 20(10):3874–3884, 2019 | ❌ **UNVERIFIABLE** — title not found. Nearest real Pang T-ITS paper is *arrival-time prediction* (20(9):3283–3293), a different topic — so even the nearest match wouldn't support a "holding control" claim. |
| `patil2025` | *Advanced predictive analytics for public transit control and fleet scheduling*, IEEE T-ITS 26(2):11176–11186, 2025 | ❌ **UNVERIFIABLE** — title not found; page range 11176–11186 is implausible for issue 2 (another red flag). Distinct from `Patil2025Conformal`. |

**Where cited:** `introduction.tex:148` (`huang2019,patil2025`), `:150` (`alexandre2023`), `:150`+`:181` (`pang2019`). These sentences claim ML "emerged as important tools… demand estimation, traffic forecasting" and that ML frameworks "rely on manually specified holding rules." IEEE Access and IEEE T-ITS are exhaustively indexed in Crossref, so absence there is strong (not absolute) evidence the metadata is wrong or the papers don't exist as written.
**Action:** for each of `huang2019`, `pang2019`, `patil2025`, produce the actual paper + DOI and correct the `.bib`, **or** replace with a verified source, **or** remove the cite and rephrase. Do not submit with these unresolved.

### HIGH-2 — `Wang2020Holding`: load-bearing citation, wrong PDF filed, claim never verified
`Wang2020Holding` (*Dynamic Holding Control to Avoid Bus Bunching: A MARL Framework*, TR-C 116:102661, 2020) anchors the MARL-emergence narrative (`introduction.tex:39, 135, 313, 345`) **and** the core research gap (`problem.tex:17`). Its `.bib` metadata is **correct** (confirmed against the DOI). But:
- The PDF filed under it in `RRW\` — `Reducing bus bunching with asynchronous multiagent.pdf` — is a **different paper**: Wang & Sun, *Reducing Bus Bunching with Asynchronous MARL* (IJCAI-21). Confirmed by opening it (title page + abstract). The real TR-C 2020 paper is **not in the folder and has never been opened.**
- Therefore the specific claim at `introduction.tex:313` ("a cooperative MARL framework could learn an effective bus-holding policy on a single-line corridor and **outperform classical headway-equalization rules under idealized stochastic demand**") is **UNVERIFIED against its source.**
**Action:** obtain the real TR-C 2020 PDF, verify the `:313` claim (and the `problem.tex:17` "stationary arrivals / symmetric Gaussian / failure-free" characterization), and re-file the correct PDF. Metadata needs no change.

### MED-3 — `TSSP_Rain2018` has the wrong authors
The `.bib` attributes ref **[9]** to *Espino, Larraquel, Purisima, Valenzuela, Borromeo*. The actual paper — same title verbatim, and the `.bib`'s own `url` (`…/TSSP2018-09.pdf`) points to it — is authored by **Hanzel N. Mejia & Ricardo G. Sigua** (opened and confirmed). Corroboration: Figure 1.2's numbers (−17.4% capacity, −7.4% speed) and the `introduction.tex:35` sentence (5.34/6.3/7.4% speed; 3.67/7.6/17.44% capacity) match the Mejia & Sigua abstract exactly — so the source used *is* Mejia & Sigua; only the author field is wrong. This is the rainfall citation the panel flagged (RTC item 16).
**Action:** correct the `author` field (fix in §3).

### MED-4 — Half-applied fix: Patil "freeway" vs "arterial" (internal contradiction)
Per the group's own `RRL/sources.md` (2026-08-06), the manuscript mischaracterized Patil2025Conformal's data as freeway and was corrected to arterials — but the fix landed in only one place:
- `methods.tex:438`: "…validate a CV-driven lognormal travel-time form against **SUMO/INRIX-based urban arterial** scenarios" ✅ corrected.
- `introduction.tex:443`: "…validated against **INRIX freeway data** via the Kolmogorov-Smirnov test" ❌ still the old, wrong wording.
The two live sentences now describe the same validation as both "freeway" and "arterial." **Action:** align `:443` to "urban arterial" (fix in §3).

### MED-5 — `RRL/sources.md` index is stale/wrong in 4 rows (your local `RRW\` can now resolve them)
| PDF in `RRW\` | `RRL/sources.md` says | Actually is (opened/confirmed) |
|---|---|---|
| `TSSP2024-04-Revised-Paper.pdf` | TENTATIVE → `Spatio2026` | **`Ollero2024EDSA`** — *A Microsimulation Model of An Exclusive Bus Lane: The Case of EDSA Busway* (Ollero, Vergel, Tiglao). So `Ollero2024EDSA` **does** have a local PDF. |
| `sustainability-15-15018.pdf` | TENTATIVE → `Tiglao2025`/`EDSApolicy2023` | *Recovery Strategies for Urban Rail Transit Network… Resilience* (Zheng et al., 2023) — **matches no cited key**; uncited background. |
| `ijgi-13-00050-v2.pdf` | (already de-linked from Ranpura) | *Commuting under Adverse Weather: Typhoon In-Fa* (Ji et al., 2024) — **matches no cited key**; uncited background (it is **not** `Spatio2026`, the Commonwealth-Ave Waze paper). |
| `Reducing bus bunching with asynchronous multiagent.pdf` | MISMATCHED under `Wang2020Holding` | ✅ confirmed: IJCAI-21 async paper — see HIGH-2. |

### LOW/MED-6 — 11 references defined in `.bib` but never cited (won't render; coverage)
`Cai2024Multiairport, DOTr2020Suspension, FEMbusbunching, Fan2019HPPO, Ju2023Joint, Ning2024Survey, Ranpura2025Calibration, Schrader2024SUMO, Wardman2004VOT, Yang2024AMAHPPO, Zhao2023AGV`. Several (Ning2024Survey, FEMbusbunching, Ju2023Joint, Zhao2023AGV, Cai2024Multiairport, Fan2019HPPO, Ranpura2025Calibration) have PDFs in `RRW\` — collected then dropped. **Action:** for each, either re-cite it in the relevant sentence or delete the entry so the `.bib` reflects the real reference set.

### LOW-7 — Housekeeping (not blocking; several not compiled)
- `results.tex` contains leftover **NeuroSEE neuroscience template** text (motion artefacts, Neurofinder dataset). It is commented out of `main.tex`, so it does not compile — but must be replaced before Chapter 4 is written.
- `main.tex` loads `\usepackage{acro}` and `\usepackage[acronym]{glossaries}` **twice** (lines 101/107, 102/108). Harmless, but drop the duplicates.
- A large `\iffalse … \fi` "superseded EDSA background" block remains in `introduction.tex` (from ~line 89). Fine to keep as history; delete when convenient for a clean source.
- `main.tex:5` uses `inputenc[utf8x]` (deprecated in favor of `utf8`). Works; low priority.
- Copy-edit: `introduction.tex:43` "Because the EDSA operational record **were not be able to be obtained**" is ungrammatical → e.g. "could not be obtained."

---

## 2. What was verified and PASSES (report of clean items)
- **Dataset facts reconcile exactly** with `data/audit/texas_capmetro/*.json` (per provenance rule R1):
  - 229,421 dir-6 clean events; 184 service days; 29 stops (`problem.tex:9`, `introduction.tex:66,76`, `methods.tex:141`) ✅
  - Route-selection table (`introduction.tex:57–61`): 547,616 / 455,654 / 810,309 / 441,779 / 98.136% (801) and 468,689 / 376,801 / 532,063 / 361,852 / 97.479% (803) ✅ all match `route_selection_audit.json`.
  - Weather join (`introduction.tex:84`): 100% coverage of 229,421; 11,804 rain-exposed ✅ match `weather_join_audit.json`.
  - Ridership (`introduction.tex:11,17`): 63.02M→66.67M = 5.79%; 182,655 daily; 321,186 peak ✅ arithmetic and `DOTr2025Ridership` note consistent.
  - Gated correctly: compass label, stop names, capacity, scheduled headway all deferred with placeholder language (no fabrication found).
- **Figure source attributions present** (RTC item 11): SARL-vs-MARL → Gupta2017PS + Busoniu2008Survey (`:280`); CTDE → Lowe2017MADDPG (`:301`); AEC cycle → Terry2021PettingZoo (`methods:655`); rainfall → TSSP_Rain2018 (`:31`); corridor map → CapMetroRapid (`:77`); originals + illustrative figures marked "Authors' illustration" / "illustrative only." ✅
- **Formatting** (RTC items 18–19): `\onehalfspacing` (`main:145`), `lineno`+`\linenumbers` (`main:124,230`) ✅
- **Reference plumbing:** 72 cited keys, 0 undefined `\cite`, 0 undefined `\ref` ✅ (clean compile expected).
- **Already-content-verified fixes confirmed present:** Rodriguez2023 (6-action space, EH cap) and Wangsun demand clip stated as the study's own [1,3] ✅. **Exception:** the Patil "freeway→arterial" fix is only half-applied (see MED-4).

---

## 3. Prioritized fix list (`file:line` · before → after)

1. **HIGH — resolve 3 stub cites.** For `huang2019`, `pang2019`, `patil2025` in `thesis_refs.bib`: supply the real paper + DOI and correct each entry, or replace/remove. Until resolved, treat every sentence at `introduction.tex:148,150,181` as unsupported.

2. **HIGH — `Wang2020Holding`.** Obtain the real TR-C 2020 PDF (DOI 10.1016/j.trc.2020.102661), verify the claims at `introduction.tex:313` and `problem.tex:17`, and replace the wrong PDF filed in `RRW\`. No `.bib` change.

3. **MED — `thesis_refs.bib`, `TSSP_Rain2018`:**
   - before: `author = {J. M. B. Espino and R. G. L. Larraquel and A. S. R. L. Purisima and A. M. B. Valenzuela and M. N. Borromeo},`
   - after:  `author = {Hanzel N. Mejia and Ricardo G. Sigua},`
   (Verify the `booktitle` conference number against the PDF while you're there.)

4. **MED — `introduction.tex:443`:**
   - before: `…validated against INRIX freeway data via the Kolmogorov-Smirnov test,…`
   - after:  `…validated against urban arterial travel-time data via the Kolmogorov-Smirnov test,…`

5. **MED — update `RRL/sources.md`** with the 4 corrected rows in MED-5 (Ollero2024EDSA now has a PDF; sustainability/ijgi are uncited background; Wang2020Holding PDF mismatch noted).

6. **LOW/MED — the 11 uncited keys:** cite or delete each (§1.6).

7. **LOW — housekeeping:** replace `results.tex` NeuroSEE template; remove duplicate `\usepackage{acro}`/`{glossaries}`; fix `introduction.tex:43` grammar; optionally delete the `\iffalse` EDSA block.

---

## 4. Coverage & honesty note (what this pass did NOT do)
Per-sentence claim-support was deeply verified only for the flagged/load-bearing citations and all dataset numbers. The following ~30 references have their **filename/metadata confirmed** (the `RRW\` PDF is the right paper) but their **individual in-text claims were not re-checked** in this pass, and should be spot-checked before final submission: Wang2017, Daganzo2009, Tironi2018, Barrera2025Optimization, Usman2025ML, Liu2023DRLHolding, Shi2022DistDRL, Zhao2022STDH, Cao2022Train, Guedes2018Rescheduling, Tang2024Curriculum, Zhang2025SADRL, Mnih2015DQN, vanHasselt2016DDQN, Momenikorbekandi2023Intelligent, Sun2024Graph, Xu2026Hierarchical, Huang2025Joint, Li2023Departure, Nie2025CMRM, Che2024Recharging, Bokade2023MARL, Wang2024MultiAGV, Zuo2026AGV, Katzilieris2026MARL, Wang2023MultiObj, Ollero2024EDSA. Standard RL/stats/textbook cites with no local PDF (Bellman1957, Littman1994, Ceder2007, Kingman1993, Gupta2017PS, Busoniu2008Survey, Lowe2017MADDPG, Terry2021PettingZoo, Lopez2018SUMO, Towers2024Gymnasium, etc.) are canonical and lower-risk; metadata not exhaustively checked.
