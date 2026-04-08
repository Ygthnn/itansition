# Task 1 solution (SQLite version)

This solution ingests the malformed `task1_d.json` file into SQLite and creates the required summary table **inside the database**.

## Files

- `task1_ingest_sqlite.py` — parses the malformed input and loads the raw table.
- `task1_summary.sql` — SQL that creates the summary table.
- `task1_solution.db` — ready-to-open SQLite database generated from the uploaded file.

## Raw input peculiarity

The source file is **not valid JSON**. It uses Ruby-style hashes, for example:

```text
{:id=>10292064894005717421, :title=>"Look Homeward, Angel", ...}
```

The script converts keys such as `:id=>` into valid JSON keys like `"id":` and then parses the result.

## How to run

```bash
python task1_ingest_sqlite.py task1_d.json task1_solution.db
```

## Database objects

### Raw table

```sql
books_raw(
    id TEXT PRIMARY KEY,
    title TEXT,
    author TEXT,
    genre TEXT,
    publisher TEXT,
    publication_year INTEGER,
    price_text TEXT
)
```

### Summary table

```sql
summary_by_year(
    publication_year INTEGER,
    book_count INTEGER,
    average_price_usd REAL
)
```

## Conversion rule used

- `$x` stays as USD
- `€x` is converted using **€1 = $1.2**
- yearly average is rounded to **2 decimal places**

## Row counts for the uploaded file

- `books_raw`: **5003** rows
- `summary_by_year`: **49** rows

## Example query to show the summary table

```sql
SELECT *
FROM summary_by_year
ORDER BY publication_year;
```

## First rows of the resulting summary

| publication_year | book_count | average_price_usd |
|---:|---:|---:|
| 1871 | 43 | 48.08 |
| 1883 | 56 | 52.51 |
| 1886 | 54 | 54.73 |
| 1904 | 37 | 54.74 |
| 1905 | 59 | 50.62 |
| 1938 | 21 | 43.64 |
| 1955 | 27 | 53.81 |
| 1958 | 28 | 53.66 |
| 1986 | 111 | 50.58 |
| 1987 | 93 | 48.12 |

## Last rows of the resulting summary

| publication_year | book_count | average_price_usd |
|---:|---:|---:|
| 2026 | 116 | 50.13 |
| 2025 | 108 | 51.74 |
| 2024 | 108 | 53.81 |
| 2023 | 94 | 49.12 |
| 2022 | 103 | 48.43 |
| 2021 | 102 | 54.63 |
| 2020 | 131 | 50.12 |
| 2019 | 91 | 50.32 |
| 2018 | 82 | 50.86 |
| 2017 | 104 | 50.49 |
