#!/usr/bin/env python3


from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path


def parse_malformed_json(input_path: Path) -> list[dict]:
    text = input_path.read_text(encoding="utf-8")

    # Convert Ruby-style symbol keys to JSON keys.
    # Example: :title=>"abc"  ->  "title":"abc"
    normalized = re.sub(r":(\w+)=>", r'"\1":', text)

    try:
        return json.loads(normalized)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to normalize and parse {input_path}: {exc}") from exc


DDL_AND_TRANSFORM_SQL = """
DROP TABLE IF EXISTS books_raw;
CREATE TABLE books_raw (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT NOT NULL,
    publisher TEXT NOT NULL,
    publication_year INTEGER NOT NULL,
    price_text TEXT NOT NULL
);

DROP TABLE IF EXISTS summary_by_year;
CREATE TABLE summary_by_year AS
WITH normalized_prices AS (
    SELECT
        publication_year,
        CASE
            WHEN price_text LIKE '$%' THEN CAST(SUBSTR(price_text, 2) AS REAL)
            WHEN price_text LIKE '€%' THEN ROUND(CAST(SUBSTR(price_text, 2) AS REAL) * 1.2, 2)
            ELSE NULL
        END AS price_usd
    FROM books_raw
)
SELECT
    publication_year,
    COUNT(*) AS book_count,
    ROUND(AVG(price_usd), 2) AS average_price_usd
FROM normalized_prices
GROUP BY publication_year
ORDER BY publication_year;
"""


SUMMARY_QUERY = """
WITH normalized_prices AS (
    SELECT
        publication_year,
        CASE
            WHEN price_text LIKE '$%' THEN CAST(SUBSTR(price_text, 2) AS REAL)
            WHEN price_text LIKE '€%' THEN ROUND(CAST(SUBSTR(price_text, 2) AS REAL) * 1.2, 2)
            ELSE NULL
        END AS price_usd
    FROM books_raw
)
SELECT
    publication_year,
    COUNT(*) AS book_count,
    ROUND(AVG(price_usd), 2) AS average_price_usd
FROM normalized_prices
GROUP BY publication_year
ORDER BY publication_year;
"""


def build_database(records: list[dict], db_path: Path) -> tuple[int, int]:
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        # Create raw table first.
        cur.executescript(
            """
            DROP TABLE IF EXISTS books_raw;
            CREATE TABLE books_raw (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT NOT NULL,
                publisher TEXT NOT NULL,
                publication_year INTEGER NOT NULL,
                price_text TEXT NOT NULL
            );
            """
        )

        cur.executemany(
            """
            INSERT INTO books_raw (
                id, title, author, genre, publisher, publication_year, price_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    str(row["id"]),
                    row["title"],
                    row["author"],
                    row["genre"],
                    row["publisher"],
                    int(row["year"]),
                    row["price"],
                )
                for row in records
            ],
        )

        # Transformation happens inside the database.
        cur.executescript(
            """
            DROP TABLE IF EXISTS summary_by_year;
            CREATE TABLE summary_by_year AS
            WITH normalized_prices AS (
                SELECT
                    publication_year,
                    CASE
                        WHEN price_text LIKE '$%' THEN CAST(SUBSTR(price_text, 2) AS REAL)
                        WHEN price_text LIKE '€%' THEN ROUND(CAST(SUBSTR(price_text, 2) AS REAL) * 1.2, 2)
                        ELSE NULL
                    END AS price_usd
                FROM books_raw
            )
            SELECT
                publication_year,
                COUNT(*) AS book_count,
                ROUND(AVG(price_usd), 2) AS average_price_usd
            FROM normalized_prices
            GROUP BY publication_year
            ORDER BY publication_year;
            """
        )

        conn.commit()

        raw_count = cur.execute("SELECT COUNT(*) FROM books_raw").fetchone()[0]
        summary_count = cur.execute("SELECT COUNT(*) FROM summary_by_year").fetchone()[0]
        return raw_count, summary_count
    finally:
        conn.close()


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python task1_ingest_sqlite.py /path/to/task1_d.json /path/to/output.db")
        return 1

    input_path = Path(sys.argv[1])
    db_path = Path(sys.argv[2])

    records = parse_malformed_json(input_path)
    raw_count, summary_count = build_database(records, db_path)

    print(f"Loaded {raw_count} rows into books_raw")
    print(f"Created {summary_count} rows in summary_by_year")
    print(f"SQLite database written to: {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
