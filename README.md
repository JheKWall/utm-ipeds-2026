## Abstract

This analysis attempts to organize and visualize the outcome of eight cohorts across five different institutions, as well as attempting to correlate the completion rate of each cohort with the institution-reported living expenses. The data cannot support a conclusion in either direction.

---

## Questions

1. Among UT Martin and four nearby institutions, what is the outcome of entering first-time, full-time freshmen? How has it changed over time?
2. Is there a relationship between the institution-reported living expenses and the completion rate?

## Institutions

| Institution | UNITID | Sector | Location |
|---|---|---|---|
| The University of Tennessee-Martin (UTM) | 221768 | 4-year public | Martin, TN |
| Murray State University (MSU) | 157401 | 4-year public | Murray, KY |
| Dyersburg State Community College (DSCC) | 220057 | 2-year public | Dyersburg, TN |
| Jackson State Community College (JSCC) | 220400 | 2-year public | Jackson, TN |
| Arkansas Northeastern College (ANC) | 107327 | 2-year public | Blytheville, AR |

---

## Question 1: Cohort Outcomes

### The Oldest Cohort

The oldest cohort in the dataset enrolled between July 1, 2009 and June 30, 2010, with their status recorded August 31, 2017.

| Institution | Cohort | Completed | Transferred out | Still enrolled | Outcome unknown |
|---|---:|---:|---:|---:|---:|
| Murray State | 1,438 | 50.6% | 26.2% | 1.3% | 21.9% |
| UT Martin | 1,424 | 46.9% | 34.3% | 0.8% | 18.0% |
| Arkansas Northeastern | 449 | 28.1% | 32.7% | 3.1% | 36.1% |
| Dyersburg State | 1,315 | 16.6% | 22.4% | 2.0% | 59.0% |
| Jackson State | 917 | 16.2% | 22.6% | 1.2% | 60.0% |

### The Latest Cohort

Students entering between July 1, 2016 and June 30, 2017, with status recorded August 31, 2024.

| Institution | Cohort | Completed | Transferred out | Still enrolled | Outcome unknown |
|---|---:|---:|---:|---:|---:|
| Murray State | 1,526 | 59.7% | 14.7% | 0.4% | 25.2% |
| UT Martin | 966 | 52.4% | 23.1% | 0.4% | 24.1% |
| Arkansas Northeastern | 232 | 54.7% | 28.9% | 0.9% | 15.5% |
| Dyersburg State | 581 | 30.3% | 19.8% | 1.9% | 48.0% |
| Jackson State | 1,106 | 27.9% | 20.4% | 1.6% | 50.0% |

### Overall Cohort Trend

![Cohort Percentages from 2009-2017 per Institution](powerbi/screenshots/PowerBIAnalysis-pages-images-0.jpg)

Each institution has seen a broad increase in completion rates per cohort since the 2009-10 cohort to the 2016-17 cohort. This increase is most evident with ANC, which saw an increase from 28.1% to 54.7% over the timeframe of the study.

The remaining four-year and two-year institutions experienced around a ~10% growth in completion rates excluding UTM, which remained around ~50%.

| Institution | 2009-10 | 2016-17 | Change |
|---|---:|---:|---:|
| Arkansas Northeastern | 28.1% | **54.7%** | **+26.6 pts** |
| Dyersburg State | 16.2% | 30.3% | +14.1 pts |
| Jackson State | 16.6% | 27.9% | +11.3 pts |
| Murray State | 50.6% | 59.7% | +9.1 pts |
| UT Martin | 46.9% | 52.4% | +5.5 pts |

![Cohort Percentages from 2009-2017 per Institution](powerbi/screenshots/PowerBIAnalysis-pages-images-2.jpg)

The full outcome rate dataset shows that the two-year institutions trend towards higher unknown outcome rates, with the exception being ANC which achieved outcome rates similar to the four-year institutions for its latest 2016-17 cohort.

The four-year institutions maintained a higher completion rate and transfer out rate than the two-year institutions over the timeframe of the study.

---

## Question 2: Cohort Relationship to Institution-reported Living Expenses

The dataset shows an increase in the institution-reported living expenses as well as an increase in the completion rates for all cohorts. However, it does not fully support the conclusion that the institution-reported living expenses are correlated with cohort completion rate.

The metric utilized in this study is not cost of living, but the institution-reported living expenses. The primary difference is that the institution-reported living expenses measure the average cost of housing, food, and other basic necessities excluding tuition.

The timespan of the institution-reported living expenses data ranges from 2009-10 (the entry of the first cohort) to 2023-2024 (the exit of the last cohort).

Do note however that the UTM institution-reported living expenses data only starts at 2012-13. Additionally, the ANC data shows a large drop from the 2013-2014 academic year to the 2014-15 academic year ($18,575 to $10,524). This is believed to not be an actual reduction in the institution-reported living expenses, but rather a change in reporting methodology.

![Institution-reported Living Expenses from 2009-2024](powerbi/screenshots/PowerBIAnalysis-pages-images-1.jpg)

The data here shows a general increase in the institution-reported living expenses, with a non-insignificant spike from the 2022-23 to 2023-24 academic year.

Despite the dataset showing a noticeable increase in both the completion rate and institution-reported living expenses, it cannot support a conclusion that there is a positive relationship between the two metrics. This is due to multiple factors:

1. Pairing the completion rate and institution-reported living expenses requires an arbitrary choice or an average.
   - Because a cohort's completion rate is a single value summarizing an eight-year span, it cannot be directly compared to the accompanying range of institution-reported living expenses which span the cohort's eight years.
   - This forces us to arbitrarily choose a single institution-reported living expense within the cohort's range to represent it, or to take an average of all of the values to represent it.
2. The dataset does not account for external factors affecting the metrics.
   - The completion rate and institution-reported living expenses likely have multitudes of un-accounted factors affecting them such as advancements in teaching methods and/or inflation.
3. The quality and quantity of the dataset is lacking.
   - Assumed errors such as ANC's 2013-14 to 2014-15 drop in institution-reported living expenses and JSCC's near-flat living expenses across the entire timespan raise concerns about the quality of the dataset, while eight cohorts across only five institutions cannot be expected to provide substantial evidence of any correlation.

---

## Limitations

1. Completion rate and institution-reported living expenses are measured on incompatible timescales. The completion rate is a single value covering an eight-year window, while the living expenses are annual. Pairing them requires an arbitrary choice or an averaged value.
2. Five institutions is not a sample. Institutions were selected for proximity to UTM, so no conclusion would've generalized to the state, sector, or nation.
3. Institution-reported living expenses are self-reported estimates, not measured prices. Each institution's reporting office is likely to have differing methodologies in how they determine the living expenses.
4. Two of the institution-reported living expense series are abnormal, while one starts late. ANC's figure falls from $18,575 to $10,524 between 2013-14 and 2014-15, JSCC's total rises only 4.7% across fifteen years, while UTM's living expenses only start get published in 2012-13.
5. Cohort data is historical by nature. The latest cohort data is from the 2016-17 cohorts, which is distanced far from the latest cohorts today.

---

## Repository

```
processed/          cleaned CSVs — re-run the pipeline from load.py onward
sql/                schema.sql, analysis.sql (six queries)
src/                download, clean, load, analyze, viz, excel_report
powerbi/            PowerBIAnalysis.pbix and PowerBIAnalysis.pdf (three-page dashboard)
```

Reproduction requires Python 3.14 and MySQL 8+. Create the database and a user with privileges on
it, put the password in `secrets/mysql_app_password.txt`, then:

```bash
python src/download.py && python src/clean.py && python src/load.py && python src/analyze.py && python src/viz.py && python src/excel_report.py
```

Run the tests with `python -m pytest tests/ -v`.

Raw IPEDS downloads are excluded — they are large, and `download.py` reproduces them exactly.
