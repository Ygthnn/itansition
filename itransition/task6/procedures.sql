DROP FUNCTION IF EXISTS generate_fake_users(TEXT, INT, INT, INT) CASCADE;
DROP FUNCTION IF EXISTS generate_geo(INT, INT) CASCADE;
DROP FUNCTION IF EXISTS generate_email(TEXT, INT, INT) CASCADE;
DROP FUNCTION IF EXISTS generate_name(TEXT, INT, INT) CASCADE;
DROP FUNCTION IF EXISTS generate_address(TEXT, INT, INT) CASCADE;
DROP FUNCTION IF EXISTS generate_phone(TEXT, INT, INT) CASCADE;
DROP FUNCTION IF EXISTS generate_eye_color(INT, INT) CASCADE;
DROP FUNCTION IF EXISTS generate_height(INT, INT) CASCADE;
DROP FUNCTION IF EXISTS generate_weight(INT, INT) CASCADE;
DROP FUNCTION IF EXISTS generate_normal(INT, INT, FLOAT, FLOAT) CASCADE;
DROP FUNCTION IF EXISTS pick_value(TEXT, TEXT, INT, INT) CASCADE;
DROP FUNCTION IF EXISTS rand_int(INT, INT, INT, INT) CASCADE;
DROP FUNCTION IF EXISTS seeded_random(INT, INT) CASCADE;

CREATE OR REPLACE FUNCTION seeded_random(seed_value INT, pos INT)
RETURNS FLOAT AS $$
DECLARE
    hash TEXT;
    num BIGINT;
BEGIN
    hash := md5(seed_value::TEXT || ':' || pos::TEXT);
    num := ('x' || substr(hash, 1, 15))::bit(60)::bigint;
    RETURN num::FLOAT / 1152921504606846975.0;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION rand_int(seed_value INT, pos INT, min_val INT, max_val INT)
RETURNS INT AS $$
DECLARE
    r FLOAT;
BEGIN
    r := seeded_random(seed_value, pos);
    RETURN floor(r * (max_val - min_val + 1) + min_val);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_normal(seed_value INT, pos INT, mean FLOAT, stddev FLOAT)
RETURNS FLOAT AS $$
DECLARE
    u1 FLOAT;
    u2 FLOAT;
    z FLOAT;
BEGIN
    u1 := greatest(seeded_random(seed_value, pos), 0.000001);
    u2 := seeded_random(seed_value, pos + 1);

    z := sqrt(-2 * ln(u1)) * cos(2 * pi() * u2);

    RETURN mean + stddev * z;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pick_value(p_locale TEXT, p_category TEXT, seed_value INT, pos INT)
RETURNS TEXT AS $$
DECLARE
    cnt INT;
    idx INT;
    result TEXT;
BEGIN
    SELECT COUNT(*) INTO cnt
    FROM lookup_values
    WHERE category = p_category
      AND (locale = p_locale OR locale = 'all');

    IF cnt = 0 THEN
        RETURN NULL;
    END IF;

    idx := rand_int(seed_value, pos, 1, cnt);

    SELECT value INTO result
    FROM lookup_values
    WHERE category = p_category
      AND (locale = p_locale OR locale = 'all')
    ORDER BY id
    OFFSET idx - 1 LIMIT 1;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_name(p_locale TEXT, seed_value INT, pos INT)
RETURNS TEXT AS $$
DECLARE
    first_name TEXT;
    middle_name TEXT;
    last_name TEXT;
    title TEXT;
    variant INT;
    initial TEXT;
BEGIN
    first_name := pick_value(p_locale, 'first_name', seed_value, pos + 10);
    middle_name := pick_value(p_locale, 'first_name', seed_value, pos + 11);
    last_name := pick_value(p_locale, 'last_name', seed_value, pos + 12);
    variant := rand_int(seed_value, pos + 13, 1, 4);

    initial := substr(middle_name, 1, 1) || '.';

    IF p_locale = 'de_DE' THEN
        title := CASE rand_int(seed_value, pos + 14, 1, 3)
            WHEN 1 THEN 'Herr'
            WHEN 2 THEN 'Frau'
            ELSE ''
        END;
    ELSE
        title := CASE rand_int(seed_value, pos + 14, 1, 4)
            WHEN 1 THEN 'Mr.'
            WHEN 2 THEN 'Ms.'
            WHEN 3 THEN 'Dr.'
            ELSE ''
        END;
    END IF;

    IF variant = 1 THEN
        RETURN trim(first_name || ' ' || last_name);
    ELSIF variant = 2 THEN
        RETURN trim(first_name || ' ' || initial || ' ' || last_name);
    ELSIF variant = 3 THEN
        RETURN trim(title || ' ' || first_name || ' ' || last_name);
    ELSE
        RETURN trim(last_name || ', ' || first_name);
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_email(p_locale TEXT, seed_value INT, pos INT)
RETURNS TEXT AS $$
DECLARE
    first_name TEXT;
    last_name TEXT;
    domain TEXT;
    variant INT;
BEGIN
    first_name := lower(pick_value(p_locale, 'first_name', seed_value, pos + 20));
    last_name := lower(pick_value(p_locale, 'last_name', seed_value, pos + 21));
    domain := pick_value(p_locale, 'email_domain', seed_value, pos + 22);
    variant := rand_int(seed_value, pos + 23, 1, 3);

    first_name := translate(first_name, 'äöüßÄÖÜ', 'aousAOU');
    last_name := translate(last_name, 'äöüßÄÖÜ', 'aousAOU');

    IF variant = 1 THEN
        RETURN first_name || '.' || last_name || pos || '@' || domain;
    ELSIF variant = 2 THEN
        RETURN substr(first_name, 1, 1) || last_name || pos || '@' || domain;
    ELSE
        RETURN first_name || '_' || last_name || pos || '@' || domain;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_address(p_locale TEXT, seed_value INT, pos INT)
RETURNS TEXT AS $$
DECLARE
    street TEXT;
    city TEXT;
    house_number INT;
    zip_code INT;
    apartment INT;
    variant INT;
BEGIN
    street := pick_value(p_locale, 'street', seed_value, pos + 30);
    city := pick_value(p_locale, 'city', seed_value, pos + 31);
    house_number := rand_int(seed_value, pos + 32, 1, 999);
    apartment := rand_int(seed_value, pos + 33, 1, 80);
    variant := rand_int(seed_value, pos + 34, 1, 3);

    IF p_locale = 'de_DE' THEN
        zip_code := rand_int(seed_value, pos + 35, 10000, 99999);

        IF variant = 1 THEN
            RETURN street || ' ' || house_number || ', ' || zip_code || ' ' || city;
        ELSIF variant = 2 THEN
            RETURN street || ' ' || house_number || ' Wohnung ' || apartment || ', ' || zip_code || ' ' || city;
        ELSE
            RETURN zip_code || ' ' || city || ', ' || street || ' ' || house_number;
        END IF;
    ELSE
        zip_code := rand_int(seed_value, pos + 35, 10000, 99999);

        IF variant = 1 THEN
            RETURN house_number || ' ' || street || ', ' || city || ', ' || zip_code;
        ELSIF variant = 2 THEN
            RETURN house_number || ' ' || street || ' Apt ' || apartment || ', ' || city || ', ' || zip_code;
        ELSE
            RETURN city || ', ' || house_number || ' ' || street || ', ZIP ' || zip_code;
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_phone(p_locale TEXT, seed_value INT, pos INT)
RETURNS TEXT AS $$
DECLARE
    a INT;
    b INT;
    c INT;
    d INT;
    variant INT;
BEGIN
    variant := rand_int(seed_value, pos + 40, 1, 3);

    IF p_locale = 'de_DE' THEN
        a := rand_int(seed_value, pos + 41, 151, 179);
        b := rand_int(seed_value, pos + 42, 1000000, 9999999);

        IF variant = 1 THEN
            RETURN '+49 ' || a || ' ' || b;
        ELSIF variant = 2 THEN
            RETURN '0' || a || '/' || b;
        ELSE
            RETURN '+49-' || a || '-' || b;
        END IF;
    ELSE
        a := rand_int(seed_value, pos + 41, 200, 999);
        b := rand_int(seed_value, pos + 42, 200, 999);
        c := rand_int(seed_value, pos + 43, 1000, 9999);

        IF variant = 1 THEN
            RETURN '+1 (' || a || ') ' || b || '-' || c;
        ELSIF variant = 2 THEN
            RETURN a || '-' || b || '-' || c;
        ELSE
            RETURN '(' || a || ') ' || b || ' ' || c;
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_geo(seed_value INT, pos INT)
RETURNS TABLE(lat FLOAT, lon FLOAT) AS $$
DECLARE
    u1 FLOAT;
    u2 FLOAT;
BEGIN
    u1 := seeded_random(seed_value, pos + 50);
    u2 := seeded_random(seed_value, pos + 51);

    lon := 360 * u1 - 180;
    lat := degrees(asin(2 * u2 - 1));

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_eye_color(seed_value INT, pos INT)
RETURNS TEXT AS $$
BEGIN
    RETURN pick_value('all', 'eye_color', seed_value, pos + 60);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_height(seed_value INT, pos INT)
RETURNS FLOAT AS $$
BEGIN
    RETURN round(generate_normal(seed_value, pos + 70, 172, 10)::numeric, 1)::FLOAT;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_weight(seed_value INT, pos INT)
RETURNS FLOAT AS $$
BEGIN
    RETURN round(generate_normal(seed_value, pos + 80, 72, 15)::numeric, 1)::FLOAT;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_fake_users(
    p_locale TEXT,
    seed_value INT,
    batch_index INT,
    batch_size INT
)
RETURNS TABLE(
    full_name TEXT,
    address TEXT,
    latitude FLOAT,
    longitude FLOAT,
    height_cm FLOAT,
    weight_kg FLOAT,
    eye_color TEXT,
    phone TEXT,
    email TEXT
) AS $$
DECLARE
    i INT;
    pos INT;
BEGIN
    FOR i IN 0..batch_size-1 LOOP
        pos := batch_index * batch_size + i;

        RETURN QUERY
        SELECT
            generate_name(p_locale, seed_value, pos),
            generate_address(p_locale, seed_value, pos),
            g.lat,
            g.lon,
            generate_height(seed_value, pos),
            generate_weight(seed_value, pos),
            generate_eye_color(seed_value, pos),
            generate_phone(p_locale, seed_value, pos),
            generate_email(p_locale, seed_value, pos)
        FROM generate_geo(seed_value, pos) g;
    END LOOP;
END;
$$ LANGUAGE plpgsql;