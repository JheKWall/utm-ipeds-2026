-- UTM IPEDS Summer 2026 -- table definitions
--
-- Run as ipeds_app against the utm_ipeds database. This script does NOT create the
-- database: ipeds_app has privileges only *within* utm_ipeds, which root created
-- during setup (see docs/mysql-setup.md).

USE utm_ipeds;

-- Children first: they reference institution by foreign key.
DROP TABLE IF EXISTS om_cohort;
DROP TABLE IF EXISTS om_counts;         -- superseded by om_cohort
DROP TABLE IF EXISTS ic_cost_year;
DROP TABLE IF EXISTS ic_costs;          -- superseded by ic_cost_year
DROP TABLE IF EXISTS institution;

-- One row per institution under study.
CREATE TABLE institution (
    unitid      INT PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    city        VARCHAR(100),
    state       CHAR(2)      NOT NULL,
    county_fips CHAR(5)      COMMENT 'CHAR, to preserve the leading zero',
    iclevel     TINYINT      NOT NULL COMMENT '1 = 4-year, 2 = 2-year',
    sector      TINYINT      NOT NULL
);

-- Outcome Measures, LONG format: one row per institution per ENTERING cohort year,
-- first-time full-time cohort (OMCHRT = 10), measured at the 8-year status point.
--
-- Assembled from OM2017..OM2024, covering cohorts 2009-10 through 2016-17. Each
-- cohort comprises students entering across a full 12-month period (July 1 - June 30),
-- so spring and summer entrants are included -- unlike the Graduation Rates component,
-- which uses a fall-only cohort.
--
-- OM2015 and OM2016 are excluded: pilot years, structurally different, missing OMACHRT.
--
-- The four dispositions are mutually exclusive and sum to cohort.
CREATE TABLE om_cohort (
    unitid             INT         NOT NULL,
    cohort_year        CHAR(7)     NOT NULL COMMENT 'academic year of entry, e.g. 2015-16',
    cohort             INT         NOT NULL COMMENT 'OMACHRT, adjusted cohort',
    awarded_8yr        INT         NOT NULL COMMENT 'OMAWDN8, received an award',
    still_enrolled     INT         NOT NULL COMMENT 'OMENRYI, still enrolled here',
    enrolled_elsewhere INT         NOT NULL COMMENT 'OMENRAI, enrolled at another institution',
    unknown            INT         NOT NULL COMMENT 'OMENRUN, no subsequent enrollment found',
    awarded_6yr        INT                  COMMENT 'OMAWDN6; no disposition split exists at 6 years',
    source_file        VARCHAR(20) NOT NULL COMMENT 'which OM file supplied the row',
    PRIMARY KEY (unitid, cohort_year),
    FOREIGN KEY (unitid) REFERENCES institution(unitid)
);

-- Cost of attendance, LONG format: one row per institution per academic year,
-- assembled from three IC_AY files covering 2013-14 to 2023-24.
--
-- Long rather than wide because eleven years would otherwise mean 40+ columns.
-- Adding a year becomes a new row, not a schema change.
--
-- Living costs and tuition are separate columns and are never summed: price of
-- college and cost of living are different variables (design spec section 5).
CREATE TABLE ic_cost_year (
    unitid               INT         NOT NULL,
    academic_year        CHAR(7)     NOT NULL COMMENT 'e.g. 2015-16',
    food_housing         INT         COMMENT 'CHG7AY*, off campus not with family',
    other_expenses       INT         COMMENT 'CHG8AY*, off campus not with family',
    books_supplies       INT         COMMENT 'CHG4AY*',
    tuition_fees_instate INT         COMMENT 'CHG2AY*, published in-state tuition and fees',
    source_file          VARCHAR(20) NOT NULL COMMENT 'which IC_AY file supplied the row',
    PRIMARY KEY (unitid, academic_year),
    FOREIGN KEY (unitid) REFERENCES institution(unitid)
);
