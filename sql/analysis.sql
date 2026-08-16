-- UTM IPEDS Summer 2026 -- analysis queries
--
-- Query order determines output filenames (q1..q4). viz.py reads q1/q2/q3 by name,
-- so do not reorder without updating it.
--
-- Note: 100.0 (not 100) forces floating-point division. Integer division would
-- truncate every rate to 0.

USE utm_ipeds;

-- ---------------------------------------------------------------------------
-- Q1  Student outcomes, for Visualization 1.
-- ---------------------------------------------------------------------------
SELECT i.unitid,
       i.name,
       i.iclevel,
       o.cohort,
       o.awarded_8yr        AS awarded,
       o.still_enrolled,
       o.enrolled_elsewhere,
       o.unknown,
       o.awarded_6yr,
       ROUND(100.0 * o.awarded_8yr / o.cohort, 1) AS completion_pct,
       ROUND(100.0 * (o.awarded_8yr + o.enrolled_elsewhere) / o.cohort, 1)
                                                  AS completion_or_transfer_pct
FROM institution i
JOIN om_cohort o ON o.unitid = i.unitid AND o.cohort_year = '2015-16'
ORDER BY i.iclevel, completion_pct DESC;

-- ---------------------------------------------------------------------------
-- Q2  Full cost series, for Visualization 2.
--     Long format: one row per institution per academic year, 2013-14 .. 2023-24.
-- ---------------------------------------------------------------------------
SELECT i.unitid,
       i.name,
       i.iclevel,
       c.academic_year,
       c.food_housing,
       c.other_expenses,
       c.food_housing + c.other_expenses AS living_cost_total,
       c.books_supplies,
       c.tuition_fees_instate,
       c.source_file
FROM institution i
JOIN ic_cost_year c ON c.unitid = i.unitid
ORDER BY i.unitid, c.academic_year;

-- ---------------------------------------------------------------------------
-- Q3  Outcomes against cost, for Visualization 3.
--
--     Joins ic_cost_year TWICE: once at 2015-16, the year this cohort actually
--     entered, and once at 2023-24, the present-day snapshot. Reporting both is
--     the point -- if the two disagree about the direction of the relationship,
--     that is itself evidence the relationship is not real at this sample size.
-- ---------------------------------------------------------------------------
SELECT i.unitid,
       i.name,
       i.iclevel,
       o.cohort,
       o.awarded_8yr AS awarded,
       o.still_enrolled,
       o.enrolled_elsewhere,
       o.unknown,
       cohort_era.food_housing + cohort_era.other_expenses AS living_cost_2015_16,
       current_yr.food_housing + current_yr.other_expenses AS living_cost_2023_24,
       cohort_era.tuition_fees_instate                     AS tuition_2015_16,
       current_yr.tuition_fees_instate                     AS tuition_2023_24,
       ROUND(100.0 * ((current_yr.food_housing + current_yr.other_expenses)
                    - (cohort_era.food_housing + cohort_era.other_expenses))
             / (cohort_era.food_housing + cohort_era.other_expenses), 1)
                                                           AS living_cost_change_pct
FROM institution i
JOIN om_cohort    o          ON o.unitid = i.unitid AND o.cohort_year = '2015-16'
JOIN ic_cost_year cohort_era ON cohort_era.unitid = i.unitid
                            AND cohort_era.academic_year = '2015-16'
JOIN ic_cost_year current_yr ON current_yr.unitid = i.unitid
                            AND current_yr.academic_year = '2023-24'
ORDER BY living_cost_2015_16;

-- ---------------------------------------------------------------------------
-- Q4  Robustness check: does the 8-year window inflate completion?
--
--     The 8-year status point is used because it is the only one at which IPEDS
--     reports the enrollment-status breakdown. This quantifies what that choice
--     costs by comparing with the 6-year award counts, and reports how many
--     students are genuinely still enrolled at year 8 -- confirming that 8 years
--     is a measurement window, not a typical enrollment duration.
-- ---------------------------------------------------------------------------
SELECT i.unitid,
       i.name,
       i.iclevel,
       o.cohort,
       o.awarded_6yr,
       o.awarded_8yr,
       ROUND(100.0 * o.awarded_6yr / o.cohort, 1) AS completion_pct_6yr,
       ROUND(100.0 * o.awarded_8yr / o.cohort, 1) AS completion_pct_8yr,
       ROUND(100.0 * (o.awarded_8yr - o.awarded_6yr) / o.cohort, 1) AS gain_6_to_8_pct,
       o.awarded_8yr - o.awarded_6yr                                AS extra_graduates,
       ROUND(100.0 * o.still_enrolled / o.cohort, 1) AS still_enrolled_pct_at_8yr
FROM institution i
JOIN om_cohort o ON o.unitid = i.unitid AND o.cohort_year = '2015-16'
ORDER BY completion_pct_8yr DESC;

-- ---------------------------------------------------------------------------
-- Q5  Completion across all eight entering cohorts, for Visualization 5.
--
--     One row per institution per cohort, 2009-10 .. 2016-17, each measured at
--     its own eight-year status point. This is the only way to ask whether
--     completion is changing: a single OM file describes a single cohort and has
--     no time dimension of its own.
-- ---------------------------------------------------------------------------
SELECT i.unitid,
       i.name,
       i.iclevel,
       o.cohort_year,
       o.cohort,
       o.awarded_8yr,
       o.enrolled_elsewhere,
       ROUND(100.0 * o.awarded_8yr / o.cohort, 1) AS completion_pct,
       ROUND(100.0 * (o.awarded_8yr + o.enrolled_elsewhere) / o.cohort, 1)
                                                  AS completion_or_transfer_pct
FROM institution i
JOIN om_cohort o ON o.unitid = i.unitid
ORDER BY i.unitid, o.cohort_year;

-- ---------------------------------------------------------------------------
-- Q6  Each cohort paired with the living expenses of ITS OWN entry year.
--
--     This is the longitudinal question: within a single institution, when
--     living expenses rose, did completion fall? Pairing each cohort with the
--     costs it actually faced is the only defensible matching -- pairing a
--     2009-10 cohort with 2023-24 prices would be meaningless.
--
--     A LEFT JOIN is used deliberately: UT Martin did not report living expenses
--     for 2009-10 through 2011-12. An inner join would silently drop those three
--     cohorts and make the coverage gap invisible.
-- ---------------------------------------------------------------------------
SELECT i.unitid,
       i.name,
       i.iclevel,
       o.cohort_year,
       o.cohort,
       o.awarded_8yr,
       ROUND(100.0 * o.awarded_8yr / o.cohort, 1) AS completion_pct,
       c.food_housing,
       c.other_expenses,
       c.food_housing + c.other_expenses AS living_cost_at_entry,
       c.tuition_fees_instate            AS tuition_at_entry
FROM institution i
JOIN om_cohort    o ON o.unitid = i.unitid
LEFT JOIN ic_cost_year c ON c.unitid = i.unitid
                        AND c.academic_year = o.cohort_year
ORDER BY i.unitid, o.cohort_year;
