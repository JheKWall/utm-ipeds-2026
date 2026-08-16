"""Filter national IPEDS files to the five institutions and reshape for loading.

Two IPEDS quirks are handled centrally here:

1. Encoding. hd2025.csv and ic2023_ay.csv are UTF-8 with a byte-order mark, while
   om2023_RV.csv is not. Reading as latin-1 never fails but leaves the BOM glued to
   the first column name, so column names are normalized after reading.

2. Column case. IC_AY mixes cases in the same file (TUITION1 but chg7ay3), so all
   column names are upper-cased.
"""
import glob
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
import download

# OMCHRT selects the cohort: 10 = first-time full-time, total.
# 11 and 12 are its Pell and non-Pell splits, which this study does not use.
FTFT_COHORT = 10


def read_ipeds(pattern: str) -> pd.DataFrame:
    """Read a raw IPEDS CSV, preferring the revised (_RV) file when one exists."""
    files = [
        p for p in glob.glob(str(config.DATA_RAW / pattern))
        if "dict" not in Path(p).name.lower()
    ]
    if not files:
        raise FileNotFoundError(f"No raw file matching {pattern}")
    revised = [p for p in files if "_rv" in Path(p).name.lower()]
    chosen = revised[0] if revised else files[0]

    # index_col=False matters. Some older IPEDS files carry one more field per data
    # row than the header declares -- ic2012_ay.csv has 268 header fields and 269
    # data fields. Without this, pandas silently promotes UNITID to the index and
    # shifts every column left by one, so UNITID ends up holding imputation flags
    # ('R', 'A') and no institution is ever matched.
    df = pd.read_csv(chosen, encoding="latin-1", low_memory=False, index_col=False)
    df.columns = [
        c.replace("﻿", "").replace("ï»¿", "").strip().upper()
        for c in df.columns
    ]
    print(f"  read {Path(chosen).name}: {len(df):,} rows")
    return df


def clean_institutions() -> pd.DataFrame:
    df = read_ipeds("hd*.csv")
    df = df[df.UNITID.isin(config.INSTITUTIONS)]
    out = pd.DataFrame({
        "unitid": df.UNITID,
        "name": df.INSTNM.str.strip(),
        "city": df.CITY.str.strip(),
        "state": df.STABBR,
        # COUNTYCD loses its leading zero as an integer (Arkansas 05093 -> 5093).
        "county_fips": df.COUNTYCD.astype("Int64").astype(str).str.zfill(5),
        "iclevel": df.ICLEVEL,
        "sector": df.SECTOR,
    })
    missing = set(config.INSTITUTIONS) - set(out.unitid)
    if missing:
        raise ValueError(f"Institutions not found in HD: {missing}")
    return out.sort_values("unitid")


def clean_om_cohort() -> pd.DataFrame:
    """Outcome Measures across all eight cohorts, first-time full-time, 8-year point.

    Each OM file is itself LONG -- one row per institution per cohort type, keyed
    UNITID + OMCHRT -- so the FTFT cohort is selected by filtering rows, never by
    choosing column names. Stacking eight files then gives one row per institution
    per ENTERING cohort year.

    The enrollment-status breakdown exists only at the 8-year point; the 4- and
    6-year points carry award counts alone, so awarded_6yr is the only other figure.
    """
    frames = []
    for path in sorted(config.DATA_RAW.glob("om*.csv")):
        file_year = int(path.stem[2:6])
        if file_year not in download.OM_YEARS:
            continue                      # skips the 2015/2016 pilot files
        if "_rv" not in path.stem.lower():
            # Prefer the revised file when one exists alongside the provisional.
            revised = path.with_name(f"om{file_year}_rv.csv")
            revised_upper = path.with_name(f"om{file_year}_RV.csv")
            if revised.exists() or revised_upper.exists():
                continue

        df = read_ipeds(path.name)
        df = df[(df.UNITID.isin(config.INSTITUTIONS)) & (df.OMCHRT == FTFT_COHORT)]
        frames.append(pd.DataFrame({
            "unitid": df.UNITID,
            "cohort_year": download.om_cohort_year(file_year),
            "cohort": df.OMACHRT,
            "awarded_8yr": df.OMAWDN8,
            "still_enrolled": df.OMENRYI,
            "enrolled_elsewhere": df.OMENRAI,
            "unknown": df.OMENRUN,
            "awarded_6yr": df.OMAWDN6,
            "source_file": path.stem.upper(),
        }))

    out = pd.concat(frames, ignore_index=True)

    expected = len(config.INSTITUTIONS) * len(download.OM_YEARS)
    if len(out) != expected:
        raise ValueError(f"Expected {expected} institution-cohort rows, got {len(out)}")

    # The four dispositions are mutually exclusive and must sum to the cohort.
    # A mismatch means a variable is mis-mapped; fail loudly rather than chart it.
    total = out[["awarded_8yr", "still_enrolled", "enrolled_elsewhere", "unknown"]].sum(axis=1)
    bad = out[total != out.cohort]
    if not bad.empty:
        raise ValueError(f"Dispositions do not sum to cohort:\n{bad}")

    return out.sort_values(["unitid", "cohort_year"])


def _academic_year(file_year: int, suffix: int) -> str:
    """Map an IC_AY column suffix to its academic year.

    Each IC_AY file carries a rolling four-year window: ay0..ay3 correspond to
    academic years (file_year - 3) .. file_year. So IC2023_AY's chg7ay0 is 2020-21
    and its chg7ay3 is 2023-24.
    """
    start = file_year - 3 + suffix
    return f"{start}-{str(start + 1)[-2:]}"


def clean_ic_cost_year() -> pd.DataFrame:
    """Cost of attendance from every IC_AY file, reshaped to long format.

    chg7ay* / chg8ay* are off-campus (not with family) food+housing and other
    expenses -- the cost-of-LIVING measure. chg2ay* is in-state tuition and fees,
    kept separate because price of college is a different variable (spec section 5).

    Three files (2016, 2019, 2023) give a continuous 2013-14 .. 2023-24 series.
    Where two files report the same academic year, the more recent file wins, as it
    carries the later revision.
    """
    frames = []
    for path in sorted(config.DATA_RAW.glob("ic*_ay.csv")):
        file_year = int(path.stem[2:6])
        df = read_ipeds(path.name)
        df = df[df.UNITID.isin(config.INSTITUTIONS)]

        for suffix in range(4):
            frames.append(pd.DataFrame({
                "unitid": df.UNITID,
                "academic_year": _academic_year(file_year, suffix),
                # IPEDS writes "." for missing values, which reads as a string.
                # Coerce so those become NaN rather than poisoning the column dtype.
                "food_housing": pd.to_numeric(df.get(f"CHG7AY{suffix}"), errors="coerce"),
                "other_expenses": pd.to_numeric(df.get(f"CHG8AY{suffix}"), errors="coerce"),
                "books_supplies": pd.to_numeric(df.get(f"CHG4AY{suffix}"), errors="coerce"),
                "tuition_fees_instate": pd.to_numeric(df.get(f"CHG2AY{suffix}"), errors="coerce"),
                "source_file": path.stem.upper(),
                "_file_year": file_year,
            }))

    out = pd.concat(frames, ignore_index=True)
    # Overlapping years: keep the row from the most recent file.
    out = (out.sort_values("_file_year", ascending=False)
              .drop_duplicates(subset=["unitid", "academic_year"], keep="first")
              .drop(columns="_file_year"))

    missing = set(config.INSTITUTIONS) - set(out.unitid)
    if missing:
        raise ValueError(f"Institutions not found in IC_AY: {missing}")

    return out.sort_values(["unitid", "academic_year"])


if __name__ == "__main__":
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    for name, frame in [
        ("institution", clean_institutions()),
        ("om_cohort", clean_om_cohort()),
        ("ic_cost_year", clean_ic_cost_year()),
    ]:
        frame.to_csv(config.DATA_PROCESSED / f"{name}.csv", index=False)
        print(f"\n{name}.csv ({len(frame)} rows)")
        print(frame.to_string(index=False))
