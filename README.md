# Student Completion Outcomes at Five Institutions Near UT Martin

What happens to entering first-time, full-time students at the University of Tennessee at Martin and
four neighbouring institutions, how that has changed across eight entering cohorts, and whether local
living expenses appear related to it.

**Stack:** Python (pandas) · MySQL · Excel · Power BI
**Data:** IPEDS Outcome Measures, Institutional Characteristics, and Directory files

---

## Research questions

1. Among selected institutions near UT Martin, what share of entering first-time, full-time
   freshmen complete their program — and is that changing?
2. Is there a relationship between local living expenses and that completion rate?

## Institutions

| Institution | UNITID | Sector | Location |
|---|---|---|---|
| The University of Tennessee-Martin | 221768 | 4-year public | Martin, TN |
| Murray State University | 157401 | 4-year public | Murray, KY |
| Dyersburg State Community College | 220057 | 2-year public | Dyersburg, TN |
| Jackson State Community College | 220400 | 2-year public | Jackson, TN |
| Arkansas Northeastern College | 107327 | 2-year public | Blytheville, AR |

Three of the five are two-year colleges, which shapes the entire interpretation — see
[Reading the sector difference](#reading-the-sector-difference).

---

## Question 1 — What share complete?

### The most recent cohort

Students entering between **July 1, 2015 and June 30, 2016**, with status recorded **August 31,
2023**, eight years later.

| Institution | Cohort | Completed | Transferred out | Still enrolled | Outcome unknown | **Completed or transferred** |
|---|---:|---:|---:|---:|---:|---:|
| Murray State | 1,507 | **57.1%** | 12.6% | 0.5% | 29.8% | 69.7% |
| UT Martin | 1,073 | 51.9% | **23.3%** | 0.5% | 24.3% | **75.2%** |
| Arkansas Northeastern | 215 | 43.7% | 14.4% | 1.9% | 40.0% | 58.1% |
| Dyersburg State | 587 | 31.2% | 17.4% | 0.9% | 50.6% | 48.6% |
| Jackson State | 1,122 | 29.6% | 17.8% | 1.2% | 51.3% | 47.4% |

![Eight-year outcomes](output/charts/1_outcomes.png)

**UT Martin has the highest transfer-out rate of the five, at 23.3%** — higher than any of the
community colleges, contradicting the common assumption that community colleges are the transfer
institutions. Because those students succeeded elsewhere rather than failing, UT Martin also has the
**highest completion-or-transfer rate in the group at 75.2%**, ahead of Murray State despite Murray
State's higher raw completion.

**More than half of each large community college cohort has an unknown outcome** — 50.6% at Dyersburg
State, 51.3% at Jackson State. These students earned no award and no subsequent enrollment was found
anywhere. It is the starkest number here and the most easily misread: it is **not a dropout rate**.

### The trend across eight cohorts

A single Outcome Measures file describes a single cohort, so answering "is this changing?" requires
eight separate files — one per entering cohort, each measured at its own eight-year point.

![Cohort trend](output/charts/5_cohort_trend.png)

| Institution | 2009-10 | 2016-17 | Change |
|---|---:|---:|---:|
| Arkansas Northeastern | 28.1% | **54.7%** | **+26.6 pts** |
| Dyersburg State | 16.2% | 30.3% | +14.1 pts |
| Jackson State | 16.6% | 27.9% | +11.3 pts |
| Murray State | 50.6% | 59.7% | +9.1 pts |
| UT Martin | 46.9% | 52.4% | +5.5 pts |

**Completion improved at every institution, and by far the most at the community colleges.**
Arkansas Northeastern's rate nearly doubled; Dyersburg State's and Jackson State's rose by roughly
two-thirds. The single-cohort snapshot above makes the community colleges look like they are
failing. The trend shows them closing the gap rapidly — and the two universities improving far more
slowly.

That reversal of impression is the strongest argument in this project for never reading a single
cohort as though it were a trend.

---

## Question 2 — Do living expenses relate to completion?

**No conclusion is supportable, and the analysis produced three independent demonstrations of why.**

Living expenses were assembled for fifteen academic years, 2009-10 to 2023-24, so every cohort can
be paired with the costs it actually faced.

![Living expenses](output/charts/2_cost_of_living.png)

### First: the cross-sectional correlation flips with an arbitrary choice

Using the five institutions' 2015-16 completion rates:

| Cost year used | Correlation | Reads as |
|---|---:|---|
| **2015-16** — when the cohort enrolled | **−0.55** | Higher costs, lower completion |
| **2023-24** — present day | **+0.82** | Higher costs, higher completion |

![Completion and cost](output/charts/3_combined.png)

Same institutions, same completion rates, opposite conclusions. The 2015-16 pairing is the
conceptually correct one — those are the prices the cohort actually faced — but an analyst reaching
for "the latest data" would get the reverse. The mechanism is visible directly: completion describes
one cohort and has no time series, so each institution moves only sideways.

![Cost shift](output/charts/4_cost_shift.png)

Murray State's living expenses rose **65%**, travelling from cheapest in the group to most expensive
and crossing every other institution. Because it also has the highest completion rate, moving it from
one end of the axis to the other inverts the apparent relationship.

### Second: within institutions, the sign disagrees between them

Pairing all eight cohorts with the living expenses of their own entry year:

| Institution | n | Cost at entry | Completion | r |
|---|---:|---|---|---:|
| Dyersburg State | 8 | $10,198 → $11,490 | 16.2% → 31.2% | **+0.90** |
| Murray State | 8 | $9,244 → $12,135 | 50.0% → 59.7% | +0.63 |
| UT Martin | 5 | $12,146 → $13,514 | 46.3% → 52.5% | +0.55 |
| Jackson State | 8 | $14,910 → $15,688 | 16.6% → 29.6% | +0.31 |
| Arkansas Northeastern | 8 | $10,524 → $18,575 | 26.8% → 54.7% | **−0.49** |

Plotting each institution's movement through cost-completion space from its first cohort to its last
shows where that variation comes from:

![Trajectory](output/charts/7_trajectory.png)

**Arkansas Northeastern appears to move left — but that is a reporting artifact, not a cost
decline.** Its reported living expenses fall from $18,575 in 2013-14 to $10,524 in 2014-15, a **43%
drop in a single year**, with both figures coming from the *same* source file. Local costs do not
halve; the institution changed how it calculates the estimate. Its arrow spans that break.

That single artifact is enough to flip the sign of the pooled correlation across all five
institutions. It is not a finding about cost — it is a demonstration of how little five institutions
can support, and of why a level break in a source series has to be found before the analysis is
built on it rather than after.

### Third: pooling the institutions reverses the sign — Simpson's paradox

![Within institution](output/charts/6_within_institution.png)

Pooled across all 37 institution-cohort observations, **r = −0.35** — negative, while four of the
five within-institution correlations are positive. The aggregate contradicts nearly every subgroup.

This is Simpson's paradox, and it is exactly what makes the naive analysis dangerous. The pooled
negative correlation is driven by *between*-institution differences: Jackson State has both high
costs and low completion, Murray State the reverse. The positive within-institution correlations are
driven by *time*: over a decade, living expenses rose and completion rose, for reasons that have
nothing to do with each other.

**Neither figure is evidence that living expenses affect completion.** A positive within-institution
correlation would imply that raising costs improves graduation, which is absurd. It is a spurious
correlation between two variables that both trend upward.

**No correlation coefficient, trend line, or p-value is reported as a finding anywhere in this
project.** The coefficients above appear solely to demonstrate their own unreliability.

---

## Reading the sector difference

The intuition that shorter programs are easier to finish is reasonable and **wrong**.

Mechanically the eight-year window *is* more generous to two-year colleges — 400% of normal time for
an associate degree against 200% for a bachelor's. Despite that, community college completion runs at
roughly half the four-year rate, nationally and here.

The gap is driven by **student population and institutional mission, not program length.** Community
colleges disproportionately serve lower-income, first-generation, and academically underprepared
students, and many enrollees never intend to earn a credential from that institution at all.

**Program length, student demographics, and institutional mission differ simultaneously across these
five institutions and cannot be separated at this sample size.** Higher completion at the two
universities is not evidence of institutional quality — particularly given that the community
colleges are improving several times faster.

**Completion-or-transfer** is therefore reported alongside completion. For a community college,
transferring to a four-year institution is mission success, not failure.

---

## Why Outcome Measures rather than graduation rates

**Fixed windows make sectors comparable.** The Graduation Rates component measures completion at 150%
of *normal* program time — three years for an associate degree, six for a bachelor's. Comparing those
across sectors is meaningless. OM uses absolute 4-, 6-, and 8-year windows; NCES chose the eight-year
point because it is at least 200% of normal time for every program type.

**Full-year cohorts include spring and summer entrants.** GR is built on a fall cohort, so anyone
first enrolling in January is invisible to it. OM covers a full 12-month entry period — which matters
most at community colleges.

**Only OM reports what happened to non-completers.** That breakdown exists **only** at the eight-year
point; the four- and six-year points carry award counts alone.

**Does the eight-year window inflate results?** No. Extending from six years to eight adds between
0.4 and 2.3 percentage points, and under 2% of any cohort is still enrolled at year eight — confirming
that eight years is a *measurement window*, not a typical enrollment duration.

| Institution | 6-year | 8-year | Gain | Still enrolled at year 8 |
|---|---:|---:|---:|---:|
| Murray State | 55.4% | 57.1% | +1.7 | 0.5% |
| UT Martin | 50.2% | 51.9% | +1.7 | 0.5% |
| Arkansas Northeastern | 41.4% | 43.7% | +2.3 | 1.9% |
| Dyersburg State | 30.2% | 31.2% | +1.0 | 0.9% |
| Jackson State | 29.2% | 29.6% | +0.4 | 1.2% |

---

## Method

**Sources**, from `nces.ed.gov/ipeds/`:

| File | Provides |
|---|---|
| `HD2025` | Institution directory — names, sector, county |
| `OM2017`–`OM2024` | Outcome Measures, eight cohorts (2009-10 to 2016-17) |
| `IC2012_AY`, `IC2016_AY`, `IC2019_AY`, `IC2023_AY` | Cost of attendance, 2009-10 to 2023-24 |

`OM2015` and `OM2016` are excluded: pilot years of the component, structurally different (~13,000
rows against ~50,000, no four-year status point) and missing `OMACHRT` entirely.

**Pipeline.**

```
src/download.py  →  src/clean.py  →  src/load.py  →  src/analyze.py  →  src/viz.py
                                         ↓                  ↓                ↓
                                      MySQL          output/queries/    output/charts/
```

**Schema.** Three tables, both fact tables in long format so adding a year or cohort is a new row
rather than a schema change:

- `institution` — one row per institution
- `om_cohort` — one row per institution per entering cohort (40 rows)
- `ic_cost_year` — one row per institution per academic year (75 rows)

**Measures.** Shares of the adjusted cohort (`OMACHRT`), first-time full-time cohort (`OMCHRT = 10`):

| Measure | Definition |
|---|---|
| Completion rate | Received an award ÷ cohort |
| Still-enrolled rate | No award, still enrolled at the reporting institution ÷ cohort |
| Transfer-out rate | No award, subsequently enrolled elsewhere ÷ cohort |
| Unknown-outcome rate | No award, no subsequent enrollment found ÷ cohort |
| Completion-or-transfer rate | (Awarded + enrolled elsewhere) ÷ cohort |

The four dispositions are mutually exclusive and must sum to the cohort. This is asserted in code
rather than assumed — `src/rates.py` and `src/clean.py` both raise if they do not, guarding against a
mis-mapped source variable across all 40 institution-cohort rows.

**What the cost figures are.** Labelled *cost of attendance: living expenses*, using IPEDS's own
terminology: an institution's **estimated student budget** for someone living off campus and not with
family — food and housing plus other expenses. It **excludes tuition and fees**, recorded separately,
because price of college and cost of living are different variables.

It is an administrative estimate produced by a financial aid office, not a measurement of local
prices. Institutions use differing methodologies and the figures cap federal aid eligibility.

**On BEA Regional Price Parities.** An external price index was intended as corroboration, evaluated,
and rejected. BEA's `SARPP` contains 52 geographies — the US, 50 states, DC — with no nonmetropolitan
rows; `MARPP` contains exactly one nonmetropolitan geography, a single national figure. Only Jackson
State falls within a BEA metro area; the other four would have shared one identical national value.

---

## Limitations

1. **"Unknown outcome" is not a dropout rate.** It is a residual, and also absorbs students who
   enrolled somewhere the National Student Clearinghouse does not cover.
2. **The transfer-out / unknown split is unreliable year to year; only their sum is stable.** Across
   the eight cohorts, Dyersburg State's transfer-out rate ranges over 38.7 points and its unknown
   rate over 45.4 points, while the *sum* of the two ranges over only 14.8 points. Jackson State's
   transfer-out swings from 22.4% to 5.6% and back to 23.5%. Student behaviour does not move like
   that — Clearinghouse matching quality does. When matching improves, students move from "unknown"
   into "enrolled elsewhere." Treat the boundary between those two categories as a data-quality
   artifact and their sum as the real quantity.
3. **Completion-or-transfer inherits that instability.** It is built on transfer-out, the unstable
   component, and is least reliable at the community colleges it was introduced to treat fairly. It
   remains worth reporting as a fuller picture of student success, but not as a precise figure.
4. **No inferential claim about cost is supportable.** Three separate demonstrations above show why.
5. **Dispositions, not motivations.** IPEDS records what happened, never why.
6. **Mixed sectors are a confound**, not a bias with a known direction.
7. **Simpson's paradox is present in the cost data.** Pooled and within-institution correlations have
   opposite signs; neither is interpretable as an effect.
8. **Within-institution correlations are spurious time trends.** Costs and completion both rose over
   the decade for unrelated reasons.
9. **Costs are self-reported and inconsistently maintained.** Jackson State reports a near-flat figure
   across eleven years; Arkansas Northeastern's 2013-14 value falls 43% the following year and is a
   suspected reporting error, flagged on the chart rather than removed.
10. **UT Martin reported no living expenses for 2009-10 to 2011-12**, so three of its eight cohorts
   cannot be paired with costs. A `LEFT JOIN` keeps those rows visible rather than silently dropping
   them.
11. **Cohorts are historical by construction.** The most recent completed cohort entered in 2016-17;
   an eight-year window and recent students are mutually exclusive.
12. **Cohort representativeness differs by sector.** First-time full-time students are under a third
    of enrollment at two-year colleges but nearly half at four-year institutions.

---

## Repository

```
data/processed/     cleaned CSVs — re-run the pipeline from load.py onward
sql/                schema.sql, analysis.sql (six queries)
src/                download, clean, load, analyze, viz, excel_report
tests/              unit tests for the rate calculations
output/queries/     every query result as CSV — inspectable without a database
output/charts/      the seven figures
output/             UTM_IPEDS_Analysis.xlsx
powerbi/            PowerBIAnalysis.pbix and PowerBIAnalysis.pdf (three-page dashboard)
docs/               MySQL setup, SQL primer, pandas and Power BI walkthroughs
```

**Reproducing.** Requires Python 3.14 and MySQL 8+. Create the database and a user with privileges on
it, put the password in `secrets/mysql_app_password.txt`, then:

```bash
python src/download.py && python src/clean.py && python src/load.py && python src/analyze.py && python src/viz.py && python src/excel_report.py
```

Run the tests with `python -m pytest tests/ -v`.

Raw IPEDS downloads are excluded — they are large, and `download.py` reproduces them exactly.
