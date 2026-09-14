# `data/shared/` — the cleaned datasets

So anyone can run the simulator without downloading the 3.7 GB raw snapshot.

```bash
python scripts/unpack_shared_data.py      # from the repo root; puts each file where the scripts expect it
```

| File | Unpacks to | Rows | SHA-256 of the unpacked file |
|---|---|---|---|
| `route_801_direction_6_clean.zip` (12 MB) | `data/raw/capmetro/route_801_direction_6_clean.csv` (70 MB) | 229,421 | `8368412e47df32ff8a3c2837048797664315c0e7ae51c44676766b5af7f23e21` |
| `route_801_clean_both_directions.zip` (24 MB) | `data/raw/capmetro/route_801_clean_both_directions.csv` (139 MB) | 455,654 | `24bf354b4f249a62fd264bafdbb09b61e0ac32f419adca2f8b4a95436d4d32fc` |
| `weather_camp_mabry_2021_jul_dec.csv` | `data/processed/texas_capmetro/` | 6,484 | `1d6e9ba87121888f8e23db1954d6f2dde4a8551ee4e207d7f01fa0db9429eb8c` |
| `weather_bergstrom_2021_jul_dec.csv` | `data/processed/texas_capmetro/` | 5,472 | `4129e60c580acb1d3a2b50b6c80019b13c6cabcd44cd306f62d2f6e292b551ff` |

**What each one is**

- **`route_801_direction_6_clean`** — **the study set.** Every APC stop event on Route 801,
  direction code 6 (southbound), July–December 2021, after the six cleaning rules. 47 columns,
  as in the source. The row count and checksum match `data/audit/texas_capmetro/primary_subset_manifest.json`.
- **`route_801_clean_both_directions`** — the same rules, both directions (6: 229,421 rows;
  4: 226,233 rows). For replicating on the other direction.
- **`weather_*`** — NOAA Local Climatological Data for Camp Mabry (primary) and Austin-Bergstrom
  (cross-check), converted to Austin time, July–December 2021.

**What needs them**

| Script | Needs |
|---|---|
| `starter/scripts/fit_variability.py` | direction 6 + Camp Mabry weather |
| `starter/scripts/validate_simulator.py` | direction 6 |
| Everything else under `starter/` | nothing (its inputs are already committed) |
| `scripts/pipeline/` (rebuilding these files) | the full raw snapshot, see main `README.md` §9 |

**Sources and credit**

- APC data: Capital Metropolitan Transportation Authority, *APC Raw July 2021–December 2021*, Texas Open
  Data Portal, dataset `im6q-3pc9` (<https://data.texas.gov/dataset/APC-Raw-July-2021-December-2021/im6q-3pc9>).
  Published under the portal's terms of use. These files are a filtered subset: rows were selected, and all 47 source columns kept.
- Weather: NOAA National Centers for Environmental Information, Local Climatological Data v2, stations
  USW00013958 and USW00013904.
