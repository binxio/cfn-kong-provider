#!/bin/bash
docker-compose up -d
echo 'waiting for kong.'
while ! curl -sS --fail -o /dev/null http://localhost:8001/status ; do
	echo -n '.'
	sleep 1
	[[ $C -gt 30 ]] && echo && echo "ERROR: failed to start kong" && exit 1
	C=$(($C +1))
done
echo && echo 'kong is ready on http://localhost:8001'
