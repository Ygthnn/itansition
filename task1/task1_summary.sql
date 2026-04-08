DROP TABLE IF EXISTS summary_by_year;

CREATE TABLE summary_by_year AS
SELECT
    publication_year,
    COUNT(*) AS book_count,
    ROUND(AVG(price_text), 2) AS average_price
FROM books_raw
GROUP BY publication_year
ORDER BY publication_year;

SELECT COUNT(*) AS books_raw_count FROM books_raw;
SELECT COUNT(*) AS summary_count FROM summary_by_year;
SELECT * FROM summary_by_year ORDER BY publication_year;