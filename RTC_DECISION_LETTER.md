# RTC Decision Letter — Proposal Oral Examination
# Group B3 | Received: 2026-08-06 (approx.) | Sender: Cristine
# cc: ECE 21126 course instructors, and thesis adviser

**Status: ACCEPTED with major revisions.** No further oral examination required.
Group must comply with/clarify the recommendations below.

This file is the verbatim, authoritative record of the RTC's decision email.
`README.md` in this repo is an elaborated/annotated version of these same
comments (with suggested concrete actions per item) — if the two ever seem
to disagree, THIS file is the source of truth; treat `README.md`'s wording
as interpretation, not the original ask.

**Deadline:** Submit revised proposal manuscript + signed conformity of
revisions by August 8, 2026 (ECE 21131, Project Design 1 course site).

---

## Examiner 1
- Update the manuscript with the proposed setup and discussion of dataset
- Provide mapping of dataset to proposed features of the study
- Research gap should include how you arrived at the column of sudden weather disturbance

## Examiner 2
- Include study that considers severe weather conditions in your comparison
- Explain what the dataset looks like
- Expound on how traditional, non-AI scheduling systems perform under the conditions you have specified (bus bunching, severe weather, etc.)
- Can you describe what a successful performance will look like?

## Examiner 3 — RRW
- Define each 'disturbance' explicitly. Do they have dependencies? For example, traffic congestion may be caused by the breakdown, etc. What's the difference between stochastic demand and demand surge?
- Consider adding a ML/SARL VSP table showing the disturbance column (STWB).
- In the MARL VSP table (table 1.2), there is only 1 paper that has B disturbance. But in the presentation, there were two. Make sure to update the manuscript to the accurate information.
- Some figures do not have citations. For instance, in Figure 1.3, the comparison between SARL and MARL.
- Explain the concepts in Figure 1.3, like the bus states and actions.

## Examiner 3 — Methodology
- Reference 10 is not quite new and simulates a different corridor. Will you adopt the same information or tune for EDSA northbound?
- Explain the justification why the minor roads leading to the corridor are no longer considered.
- Summarize the different fixed and variable simulation parameters. Include the target value per fixed parameter. Include the target values per simulation parameter.

## Examiner 3 — Other
- When putting figures and tables, they should also be called and discussed in the paragraphs.
- Include other figures/tables in the presentation that should also be in the manuscript.
- Consider using 1.5 line spacing for easier readability.
- Consider putting line numbers for non-final manuscript versions.

## Comments on the oral exam (NOT in the manuscript — no .tex edit required)
- All proponents should have significant participation in the Q&A period.
  This is feedback about the group's defense performance, not a manuscript
  revision. See "Team Notes" in CLAUDE.md.

## Examiner 4
- Explain in detail the different scenarios, and how to simulate this data (traffic congestion, etc.)
- Include the details on the metrics and description of features.
- What are the contents of the dataset? Not described in the manuscript.
