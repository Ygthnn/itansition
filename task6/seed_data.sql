-- Clear old data
TRUNCATE TABLE lookup_values;

--------------------------------------------------
-- ENGLISH (en_US)
--------------------------------------------------

-- First names
INSERT INTO lookup_values (category, locale, value) VALUES
('first_name','en_US','John'),
('first_name','en_US','Michael'),
('first_name','en_US','David'),
('first_name','en_US','James'),
('first_name','en_US','Robert'),
('first_name','en_US','William'),
('first_name','en_US','Richard'),
('first_name','en_US','Thomas'),
('first_name','en_US','Christopher'),
('first_name','en_US','Daniel'),
('first_name','en_US','Matthew'),
('first_name','en_US','Anthony'),
('first_name','en_US','Mark'),
('first_name','en_US','Donald'),
('first_name','en_US','Steven'),
('first_name','en_US','Paul'),
('first_name','en_US','Andrew'),
('first_name','en_US','Joshua'),
('first_name','en_US','Kevin'),
('first_name','en_US','Brian');

-- Last names
INSERT INTO lookup_values (category, locale, value) VALUES
('last_name','en_US','Smith'),
('last_name','en_US','Johnson'),
('last_name','en_US','Williams'),
('last_name','en_US','Brown'),
('last_name','en_US','Jones'),
('last_name','en_US','Garcia'),
('last_name','en_US','Miller'),
('last_name','en_US','Davis'),
('last_name','en_US','Rodriguez'),
('last_name','en_US','Martinez'),
('last_name','en_US','Hernandez'),
('last_name','en_US','Lopez'),
('last_name','en_US','Gonzalez'),
('last_name','en_US','Wilson'),
('last_name','en_US','Anderson'),
('last_name','en_US','Thomas'),
('last_name','en_US','Taylor'),
('last_name','en_US','Moore'),
('last_name','en_US','Jackson'),
('last_name','en_US','Martin');

-- Cities
INSERT INTO lookup_values (category, locale, value) VALUES
('city','en_US','New York'),
('city','en_US','Los Angeles'),
('city','en_US','Chicago'),
('city','en_US','Houston'),
('city','en_US','Phoenix'),
('city','en_US','Philadelphia'),
('city','en_US','San Antonio'),
('city','en_US','San Diego'),
('city','en_US','Dallas'),
('city','en_US','San Jose');

-- Streets
INSERT INTO lookup_values (category, locale, value) VALUES
('street','en_US','Main St'),
('street','en_US','Oak St'),
('street','en_US','Pine St'),
('street','en_US','Maple Ave'),
('street','en_US','Cedar Rd'),
('street','en_US','Elm St'),
('street','en_US','Washington Ave'),
('street','en_US','Lake St'),
('street','en_US','Hill Rd'),
('street','en_US','Sunset Blvd');

-- Email domains
INSERT INTO lookup_values (category, locale, value) VALUES
('email_domain','en_US','gmail.com'),
('email_domain','en_US','yahoo.com'),
('email_domain','en_US','outlook.com'),
('email_domain','en_US','hotmail.com'),
('email_domain','en_US','icloud.com');

--------------------------------------------------
-- GERMAN (de_DE)
--------------------------------------------------

-- First names
INSERT INTO lookup_values (category, locale, value) VALUES
('first_name','de_DE','Hans'),
('first_name','de_DE','Lukas'),
('first_name','de_DE','Peter'),
('first_name','de_DE','Klaus'),
('first_name','de_DE','Stefan'),
('first_name','de_DE','Martin'),
('first_name','de_DE','Thomas'),
('first_name','de_DE','Andreas'),
('first_name','de_DE','Sebastian'),
('first_name','de_DE','Julian');

-- Last names
INSERT INTO lookup_values (category, locale, value) VALUES
('last_name','de_DE','Müller'),
('last_name','de_DE','Schmidt'),
('last_name','de_DE','Schneider'),
('last_name','de_DE','Fischer'),
('last_name','de_DE','Weber'),
('last_name','de_DE','Meyer'),
('last_name','de_DE','Wagner'),
('last_name','de_DE','Becker'),
('last_name','de_DE','Schulz'),
('last_name','de_DE','Hoffmann');

-- Cities
INSERT INTO lookup_values (category, locale, value) VALUES
('city','de_DE','Berlin'),
('city','de_DE','Munich'),
('city','de_DE','Hamburg'),
('city','de_DE','Cologne'),
('city','de_DE','Frankfurt');

-- Streets
INSERT INTO lookup_values (category, locale, value) VALUES
('street','de_DE','Hauptstraße'),
('street','de_DE','Bahnhofstraße'),
('street','de_DE','Schillerstraße'),
('street','de_DE','Goethestraße'),
('street','de_DE','Bergstraße');

-- Email domains
INSERT INTO lookup_values (category, locale, value) VALUES
('email_domain','de_DE','gmail.com'),
('email_domain','de_DE','web.de'),
('email_domain','de_DE','gmx.de');

--------------------------------------------------
-- GLOBAL VALUES
--------------------------------------------------

-- Eye colors (discrete)
INSERT INTO lookup_values (category, locale, value) VALUES
('eye_color','all','Blue'),
('eye_color','all','Brown'),
('eye_color','all','Green'),
('eye_color','all','Gray'),
('eye_color','all','Hazel');