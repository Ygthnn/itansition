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