FROM postgres:15

ARG DB_REPL_USER

ARG DB_REPL_PASSWORD

COPY init.sql /init.sql

RUN apt-get update && apt-get install gettext-base

RUN envsubst '${DB_REPL_USER} ${DB_REPL_PASSWORD}' < /init.sql > /docker-entrypoint-initdb.d/init.sql 

RUN mkdir -p /oracle/pg_data/archive/ && chown -R postgres:postgres /oracle/pg_data/archive/


