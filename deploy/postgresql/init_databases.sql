CREATE ROLE dmz_app LOGIN PASSWORD 'change-me';

CREATE DATABASE dmz_close OWNER dmz_app ENCODING 'UTF8';
CREATE DATABASE dmz_open OWNER dmz_app ENCODING 'UTF8';

\connect dmz_close
GRANT ALL PRIVILEGES ON DATABASE dmz_close TO dmz_app;

\connect dmz_open
GRANT ALL PRIVILEGES ON DATABASE dmz_open TO dmz_app;
