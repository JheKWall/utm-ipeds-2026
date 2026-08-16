"""Download IPEDS complete data files and their dictionaries.

Verified 2026-08-15:
  * Current files live under /ipeds/complete-data-files/. Older ones (roughly 2022
    and earlier) are only on the legacy /ipeds/datacenter/data/ path, so both are
    tried.
  * Cost of attendance is NOT in the main IC file -- it lives in IC<year>_AY
    ("academic year charges"). IC2025 contains no cost columns at all.
  * Each IC_AY file carries a rolling FOUR-year window: chg*ay0..ay3 correspond to
    academic years (Y-3) through Y. Three files therefore cover 2013-14 to 2023-24
    continuously.
  * Revised records ship as an extra _RV.csv inside the same archive.
"""
import io
import sys
import zipfile
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config

BASES = [
    "https://nces.ed.gov/ipeds/complete-data-files",
    "https://nces.ed.gov/ipeds/datacenter/data",   # legacy, for older years
]

# HD2025 - directory: names, sector, county.
#
# OM2017..OM2024 - Outcome Measures, one file per entering cohort. OM<Y> reports the
#   cohort that entered in (Y-8), so these eight files cover cohorts 2009-10 through
#   2016-17. OM2015 and OM2016 are deliberately EXCLUDED: they are the component's
#   pilot years, structurally different (~13k rows rather than ~50k, no four-year
#   status point) and missing OMACHRT entirely.
#
# IC2012_AY..IC2023_AY - cost of attendance. Each file carries a rolling four-year
#   window (Y-3 .. Y), so these four give a continuous 2009-10 .. 2023-24 series,
#   covering every cohort's own enrolment period plus the present day.
OM_YEARS = list(range(2017, 2025))
FILES = (
    ["HD2025"]
    + [f"OM{y}" for y in OM_YEARS]
    + ["IC2012_AY", "IC2016_AY", "IC2019_AY", "IC2023_AY"]
)


def om_cohort_year(file_year: int) -> str:
    """OM<Y> reports the cohort that entered in academic year (Y-8).

    Verified against each file's dictionary: OM2023 reports the 2015-16 cohort at
    its eight-year status point (August 31, 2023).
    """
    start = file_year - 8
    return f"{start}-{str(start + 1)[-2:]}"


def download_ipeds(name: str) -> list[str]:
    """Download and extract one file plus its dictionary into data/raw/.

    Tries each base URL in turn; older files are absent from the current path.
    """
    config.DATA_RAW.mkdir(parents=True, exist_ok=True)
    extracted: list[str] = []
    for target in (name, f"{name}_Dict"):
        for base in BASES:
            resp = requests.get(f"{base}/{target}.zip", timeout=180)
            if resp.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                    zf.extractall(config.DATA_RAW)
                    extracted.extend(zf.namelist())
                break
        else:
            raise RuntimeError(f"{target}.zip not found on any known IPEDS path")
    return extracted


if __name__ == "__main__":
    for name in FILES:
        print(f"{name}: {', '.join(download_ipeds(name))}")
