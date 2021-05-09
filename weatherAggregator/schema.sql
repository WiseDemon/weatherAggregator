DROP TABLE IF EXISTS city;
DROP TABLE IF EXISTS weather_source;
DROP TABLE IF EXISTS city_source;
DROP TABLE IF EXISTS weather_data;


CREATE TABLE city (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    lat REAL,
    lon REAL,
    country_code CHAR(2),
    UNIQUE (name, country_code)
);

CREATE TABLE weather_source (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

--Stores ids of cities in different sources
CREATE TABLE city_source(
    city_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    local_id INTEGER NOT NULL,
    PRIMARY KEY (city_id, source_id),
    FOREIGN KEY (city_id) REFERENCES city,
    FOREIGN KEY (source_id) REFERENCES weather_source
);

CREATE TABLE weather_data(
    id INTEGER PRIMARY KEY,
    city_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    ob_dt INTEGER NOT NULL, --Time of obtainment
    temp REAL NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city,
    FOREIGN KEY (source_id) REFERENCES weather_source,
    UNIQUE (city_id, source_id, ob_dt)
);