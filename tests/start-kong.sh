#!/bin/bash
NGROK_AUTHTOKEN=$(yq .authtoken  ~/.ngrok2/ngrok.yml) docker-compose up -d
echo 'waiting for kong.'
while ! curl -sS --fail -o /dev/null http://localhost:8001/status ; do
	echo -n '.'
	sleep 1
	[[ $C -gt 30 ]] && echo && echo "ERROR: failed to start kong" && exit 1
	C=$(($C +1))
done
echo "======================================" 
echo 'kong is ready on http://localhost:8001'
echo "======================================" 
docker compose logs ngrok 2>&1 | sed -n -e 's/.*started tunnel.*url=\(.*\)/make ADMIN_URL=\1 demo/p' 

