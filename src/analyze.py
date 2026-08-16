"""Run the analysis queries, apply the rate functions, export results to CSV.

Reads sql/analysis.sql, executes each statement, adds the computed rates where the
disposition columns are present, and writes one CSV per query into output/queries/.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
from load import connect
from rates import disposition_rates

# Columns a result must have before rates can be computed from it.
RATE_INPUTS = {"cohort", "awarded", "still_enrolled", "enrolled_elsewhere", "unknown"}


def read_statements(path: Path) -> list[str]:
    """Split a .sql file into executable statements, dropping comments and USE."""
    lines = [
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("--")
    ]
    return [
        stmt.strip()
        for stmt in "\n".join(lines).split(";")
        if stmt.strip() and not stmt.strip().upper().startswith("USE")
    ]


def run_query(conn, sql: str) -> pd.DataFrame:
    """Execute a statement and return the result as a DataFrame.

    Built from the cursor directly rather than via pandas.read_sql, which expects a
    SQLAlchemy engine and warns when handed a raw DBAPI connection.
    """
    cur = conn.cursor()
    cur.execute(sql)
    columns = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    return pd.DataFrame(rows, columns=columns)


def add_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Append the five disposition rates to a result that carries the raw counts."""
    computed = df.apply(
        lambda r: disposition_rates({
            "cohort": int(r.cohort),
            "awarded": int(r.awarded),
            "still_enrolled": int(r.still_enrolled),
            "enrolled_elsewhere": int(r.enrolled_elsewhere),
            "unknown": int(r.unknown),
        }),
        axis=1,
        result_type="expand",
    )
    return pd.concat([df, computed], axis=1)


def main() -> None:
    config.QUERIES.mkdir(parents=True, exist_ok=True)
    statements = read_statements(config.PROJECT_ROOT / "sql" / "analysis.sql")

    conn = connect()
    try:
        for i, sql in enumerate(statements, start=1):
            df = run_query(conn, sql)
            if RATE_INPUTS.issubset(df.columns):
                df = add_rates(df)
            path = config.QUERIES / f"q{i}.csv"
            df.to_csv(path, index=False)
            print(f"\n=== q{i} ({len(df)} rows) -> {path.name} ===")
            print(df.to_string(index=False))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
