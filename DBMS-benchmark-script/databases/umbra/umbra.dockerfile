# docker build -t umbra-database-image -f umbra.dockerfile .
# docker run -p 5900:5432 --name umbra-database-container umbra-database-image
# docker container exec -it umbra-database-container bash

FROM ubuntu:23.04

ARG UMBRA_VERSION=2023-11-14
RUN apt-get update -qq \
    && apt-get install -y wget xz-utils postgresql-client \
    && wget "https://db.in.tum.de/~fent/umbra-$UMBRA_VERSION.tar.xz" \
    && tar -xf "umbra-$UMBRA_VERSION.tar.xz" -C /usr/local/bin/ \
    && rm "umbra-$UMBRA_VERSION.tar.xz" \
    && apt-get remove -y wget xz-utils ca-certificates \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV UMBRA_DATA=/var/lib/umbra/data
RUN set -eux \
   && chmod -R 755 /usr/local/bin/umbra/bin \
   && groupadd -r umbra --gid=999 \
   && useradd -r -g umbra --uid=999 umbra \
   && mkdir -p ${UMBRA_DATA} \
   && chown -R umbra:umbra /var/lib/umbra

ENV UMBRA_PORT=5432
EXPOSE $UMBRA_PORT

VOLUME $UMBRA_DATA

USER umbra:umbra
WORKDIR $UMBRA_DATA

CMD test -f "$UMBRA_DATA/db" || /usr/local/bin/umbra/bin/sql -createdb "$UMBRA_DATA/db" && \
    if test -f "$UMBRA_DATA/key.pem"; \
       then exec /usr/local/bin/umbra/bin/server "$UMBRA_DATA/db" -address=0.0.0.0 "-port=$UMBRA_PORT"; \
       else exec /usr/local/bin/umbra/bin/server "$UMBRA_DATA/db" -address=0.0.0.0 "-port=$UMBRA_PORT" -createSSLFiles; \
    fi; \ 

# [Start]

# $ docker container exec -it umbra-database-container bash
# $ psql -h localhost -p 5432 -U postgres

# if error on 'psql -h localhost -p 5432 -U postgres':
  # $ psql -h /tmp -U postgres
  # postgres=# ALTER USER postgres WITH PASSWORD 'postgres';
  # CTRL + D
  # test 'psql -h localhost -p 5432 -U postgres' again...