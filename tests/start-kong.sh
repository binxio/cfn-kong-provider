#!/bin/bash
if curl -sS -o /dev/null localhost:8000 && curl -sS -o /dev/null localhost:8001/status ; then
	echo 'INFO: kong is already running. no need to start it locally' >&2
	exit 0
fi

KONG_VERSION=0.13
docker pull postgres:9.6
docker pull kong:$KONG_VERSION


KONG_DB=$(docker run -d \
              -e POSTGRES_USER=kong \
              -e POSTGRES_DB=kong \
              postgres:9.6)


echo 'waiting for postgres.'
while ! docker exec -i -e PGPASSWORD=kong $KONG_DB psql --host localhost --user kong < /dev/null > /dev/null 2>&1; do
	echo -n '.'
	sleep 1
	[[ $C -gt 30 ]] && echo && echo "ERROR: failed to start postgres" && exit 1
	C=$(($C +1))
done
echo

docker run -it --rm \
    --link $KONG_DB:kong-database \
    -e KONG_DATABASE=postgres \
    -e KONG_PG_HOST=kong-database \
    -e KONG_CASSANDRA_CONTACT_POINTS=kong-database \
    kong:$KONG_VERSION kong migrations up

KONG_ID=$(docker run -d \
    --link $KONG_DB:kong-database \
    -e KONG_DATABASE=postgres \
    -e KONG_PG_HOST=kong-database \
    -e KONG_CASSANDRA_CONTACT_POINTS=kong-database \
    -e KONG_ADMIN_LISTEN=0.0.0.0:8001 \
    -e KONG_ADMIN_LISTEN_SSL=0.0.0.0:8444 \
    -p 8000:8000 \
    -p 8001:8001 \
    kong:$KONG_VERSION kong start --vv)

echo 'waiting for kong.'
while ! docker exec $KONG_ID curl -sS -o /dev/null http://localhost:8001/consumers ; do
	echo -n '.'
	sleep 1
	[[ $C -gt 30 ]] && echo && echo "ERROR: failed to start kong" && exit 1
	C=$(($C +1))
done
echo && echo 'kong is ready on http://localhost:8001'
