DROP TABLE IF EXISTS lookup_values;

CREATE TABLE lookup_values (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    locale VARCHAR(10),
    value TEXT
);