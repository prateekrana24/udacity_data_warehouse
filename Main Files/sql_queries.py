import configparser

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

ARN = config.get('IAM_ROLE', 'ARN')
LOG_DATA = config.get('S3', 'LOG_DATA')
LOG_JSONPATH = config.get('S3', 'LOG_JSONPATH')
SONG_DATA = config.get('S3', 'SONG_DATA')

# DROP TABLES
staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs;"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time;"

# CREATE TABLES
staging_events_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_events (
    artist          VARCHAR       NULL,
    auth            VARCHAR       NULL,
    firstName       VARCHAR       NULL,
    gender          CHAR(1)       NULL,
    itemInSession   INTEGER       NULL,
    lastName        VARCHAR       NULL,
    length          FLOAT         NULL,
    level           VARCHAR       NULL,
    location        VARCHAR       NULL,
    method          VARCHAR       NULL,
    page            VARCHAR       NULL,
    registration    BIGINT        NULL,
    sessionId       INTEGER       NULL SORTKEY DISTKEY,
    song            VARCHAR       NULL,
    status          INTEGER       NULL,
    ts              BIGINT        NULL,
    userAgent       VARCHAR       NULL,
    userId          INTEGER       NULL
);
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs (
    num_songs        INTEGER       NULL,
    artist_id        VARCHAR       NULL SORTKEY DISTKEY,
    artist_latitude  FLOAT         NULL,
    artist_longitude FLOAT         NULL,
    artist_location  VARCHAR(255)  NULL,
    artist_name      VARCHAR(255)  NULL,
    song_id          VARCHAR       NULL,
    title            VARCHAR(255)  NULL,
    duration         FLOAT         NULL,
    year             INTEGER       NULL
);
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays (
    songplay_id    INTEGER IDENTITY(0,1) NULL SORTKEY,
    start_time     TIMESTAMP NULL,
    user_id        VARCHAR NULL DISTKEY,
    level          VARCHAR NULL,
    song_id        VARCHAR NULL,
    artist_id      VARCHAR NULL,
    session_id     INTEGER NULL,
    location       VARCHAR(255) NULL,
    user_agent     VARCHAR(255) NULL
);
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users (
    user_id    INTEGER NULL SORTKEY,
    first_name VARCHAR NULL,
    last_name  VARCHAR NULL,
    gender     VARCHAR NULL,
    level      VARCHAR NULL
) diststyle all;
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs (
    song_id   VARCHAR NULL SORTKEY,
    title     VARCHAR NULL,
    artist_id VARCHAR NULL,
    year      INTEGER NULL,
    duration  FLOAT   NULL
);
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists (
    artist_id VARCHAR NULL SORTKEY,
    name      VARCHAR NULL,
    location  VARCHAR(255) NULL,
    latitude  FLOAT   NULL,
    longitude FLOAT   NULL
) diststyle all;
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time (
    start_time TIMESTAMP NULL SORTKEY,
    hour       INTEGER   NULL,
    day        INTEGER   NULL,
    week       INTEGER   NULL,
    month      INTEGER   NULL,
    year       INTEGER   NULL,
    weekday    INTEGER   NULL
) diststyle all;
""")

# STAGING TABLES
staging_events_copy = ("""
COPY staging_events FROM '{}'
CREDENTIALS 'aws_iam_role={}'
FORMAT AS JSON '{}'
REGION 'us-west-2';
""").format(LOG_DATA, ARN, LOG_JSONPATH)

staging_songs_copy = ("""
COPY staging_songs FROM '{}'
CREDENTIALS 'aws_iam_role={}'
FORMAT AS JSON 'auto'
REGION 'us-west-2';
""").format(SONG_DATA, ARN)

# FINAL TABLES
songplay_table_insert = ("""
INSERT INTO songplays (
    start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
)
SELECT DISTINCT
    TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second' AS start_time,
    se.userId AS user_id,
    se.level,
    ss.song_id,
    ss.artist_id,
    se.sessionId AS session_id,
    se.location,
    se.userAgent AS user_agent
FROM staging_events se
LEFT JOIN staging_songs ss
ON se.song = ss.title
   AND se.artist = ss.artist_name
WHERE se.page = 'NextSong';
""")

user_table_insert = ("""
INSERT INTO users (
    user_id, first_name, last_name, gender, level
)
SELECT DISTINCT
    userId AS user_id,
    firstName AS first_name,
    lastName AS last_name,
    gender,
    level
FROM staging_events
WHERE userId IS NOT NULL;
""")

song_table_insert = ("""
INSERT INTO songs (
    song_id, title, artist_id, year, duration
)
SELECT DISTINCT
    song_id,
    title,
    artist_id,
    year,
    duration
FROM staging_songs
WHERE song_id IS NOT NULL;
""")

artist_table_insert = ("""
INSERT INTO artists (
    artist_id, name, location, latitude, longitude
)
SELECT DISTINCT
    artist_id,
    artist_name AS name,
    artist_location AS location,
    artist_latitude AS latitude,
    artist_longitude AS longitude
FROM staging_songs
WHERE artist_id IS NOT NULL;
""")

time_table_insert = ("""
INSERT INTO time (
    start_time, hour, day, week, month, year, weekday
)
SELECT DISTINCT
    start_time,
    EXTRACT(HOUR FROM start_time) AS hour,
    EXTRACT(DAY FROM start_time) AS day,
    EXTRACT(WEEK FROM start_time) AS week,
    EXTRACT(MONTH FROM start_time) AS month,
    EXTRACT(YEAR FROM start_time) AS year,
    EXTRACT(DOW FROM start_time) AS weekday
FROM (
    SELECT DISTINCT
        TIMESTAMP 'epoch' + ts/1000 * INTERVAL '1 second' AS start_time
    FROM staging_events
    WHERE page = 'NextSong'
) AS time_data;
""")

# QUERY LISTS
create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]

drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]

copy_table_queries = [staging_events_copy, staging_songs_copy]

insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
