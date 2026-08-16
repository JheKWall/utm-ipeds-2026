"""Load the processed CSVs into MySQL.

Run after clean.py. Connects as ipeds_app, whose password is read from secrets/
via config -- it is never hardcoded here.
"""
import sys
from pathlib import Path

import mysql.connector
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config

# institution first on insert: the other two reference it by foreign key.
TABLES = ["institution", "om_cohort", "ic_cost_year"]


def connect():
    """Open a connection as ipeds_app."""
    return mysql.connector.connect(password=config.mysql_password(), **config.MYSQL)


def load_table(cursor, table: str) -> int:
    """Replace the contents of one table from its processed CSV."""
    df = pd.read_csv(config.DATA_PROCESSED / f"{table}.csv")
    columns = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    rows = [
        tuple(None if pd.isna(v) else (int(v) if isinstance(v, float) and v.is_integer() else v)
              for v in record)
        for record in df.itertuples(index=False)
    ]
    cursor.executemany(
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", rows
    )
    return len(rows)


def main() -> None:
    conn = connect()
    cur = conn.cursor()

    # Delete children before parents, or the foreign keys reject it.
    for table in reversed(TABLES):
        cur.execute(f"DELETE FROM {table}")

    for table in TABLES:
        print(f"{table}: {load_table(cur, table)} rows")

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
