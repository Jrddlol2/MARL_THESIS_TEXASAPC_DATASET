# Figure Asset Provenance

**Imported:** 2026-08-23

**Visual/source repository:**
[`Jrddlol2/Group-B3---Manuscript-Draft-V3`](https://github.com/Jrddlol2/Group-B3---Manuscript-Draft-V3/tree/main/Figures)
at commit `9de47c5e3be001fdea0819149f506f6573996686`.

## Exact V3 Copies

These files are byte-for-byte copies from the V3 repository:

- `UST_logo.jpg`
- `ustenglogo.png`
- `bg_fig1_ridership.pdf`
- `bg_fig2_rainfall_traffic.pdf`
- `rrl_fig1_sarl_vs_marl (3).pdf`
- `fig_3_2_aec_training.pdf`

`bg_fig3_edsa_corridor_map.pdf` was already tracked for the preserved inactive
EDSA source-history block; it is not part of the active Texas manuscript.

## V3-Styled Texas Adaptations

The following V3 figures were redrawn in the same monochrome manuscript style
because the original labels or example values contradicted the approved Texas
revision:

- `fig_3_1_pipeline (2).pdf` — EDSA/ideal-condition labels replaced with the
  CapMetro Route 801 calibration gates and the D/T/S/W/B activation rules.
- `rrl_fig2_ctde (2).pdf` — shared team reward/joint-state language replaced
  with local transitions, per-agent rewards, one shared replay buffer, and a
  shared DDQN learner.
- `meth_fig_eo1_1_calibration (2).pdf` — continuous-speed comparison replaced
  with stop-event-count GEH and held-out `rev_seconds` RMSE templates; all
  plotted points are explicitly labeled schematic.
- `meth_fig_eo3_1_ideal_results.pdf` — example numerical results removed and
  replaced with visibly empty Stage A reporting placeholders.
- `fig_3_2b_aec_evaluation.pdf` — “ideal, eta=0” wording replaced with the D+T
  Stage A baseline and D+T+S+W+B Stage B condition.

No adapted figure reports calibration, training, or controller-performance
results. The final PDFs were rendered and visually inspected before commit.

## Formatting Comparison

The V3 `title.tex` is identical to the Texas copy. The V3 and Texas `main.tex`
files also share the same document class, margins, title formatting, package
structure, and chapter-loading layout. The Texas copy intentionally retains
only these differences: the CapMetro case-study title, RTC-required 1.5 line
spacing and line numbers, the supporting `setspace` package, and removal of the
incomplete `\includeonly[` line that prevented a clean preamble. Overwriting
`main.tex` with V3 would therefore reintroduce an error and undo RTC formatting;
no format reset was performed.

## Final SHA-256 Values

| File | SHA-256 |
|---|---|
| `bg_fig1_ridership.pdf` | `D69301AE8C511D66E54AE72947587CDCB2C15C5BE55F8230E55BA1A3D8388634` |
| `bg_fig2_rainfall_traffic.pdf` | `9928EDF457FB429392DCA081464623383A6F792C5BB7C061E2F857235CBA2E79` |
| `bg_fig3_edsa_corridor_map.pdf` | `9247119B118A69FB91C94ADDABAD1B592AED21E2E0F16E74B506477C79E64ED0` |
| `fig_3_1_pipeline (2).pdf` | `D7CD506C33882B6AE4404654036ECA15A24B6C16AC038809A27F1647DCF6F653` |
| `fig_3_2_aec_training.pdf` | `80A4FDE5279B45914E94AF9FAA2115129A159A022AD7CB42730C3A92C579B3F9` |
| `fig_3_2b_aec_evaluation.pdf` | `27952DE36449D6E23D77FF97FDB162EC1E8E186A28EEC65B1EA514AF19F8B3E3` |
| `meth_fig_eo1_1_calibration (2).pdf` | `6CB02BCB40057CBF6566EEF628776CCC11646B6AA87C7151ED77C36CAF8503B5` |
| `meth_fig_eo3_1_ideal_results.pdf` | `4479A463CFB1DB6C074F28FD05F67D58A612D4C0C08A2D8CFA313884C913EB18` |
| `rrl_fig1_sarl_vs_marl (3).pdf` | `C76A7F03423E6CE67A10F883E5CD82820D6BB7DB72A15B342E0948A654134BB3` |
| `rrl_fig2_ctde (2).pdf` | `DE5EDF780C0ACEACB46EA11EEEB394C3394582A1DA305921E8A7E56C669E8089` |
| `UST_logo.jpg` | `14E1A2B91E9755C6993B6F216AC25337350386BA1DF48F3C110EBCD95F0AD5F2` |
| `ustenglogo.png` | `E84F5778E1B1A0E38BC8C919755EC46D759139AD9D5925F9193A2E0D12B0A93B` |
