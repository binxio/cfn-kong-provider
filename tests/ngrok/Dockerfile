from alpine:latest

run wget -O /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz && \
    tar -xvzf /tmp/ngrok.zip  -C /usr/local/bin && \
    apk --no-cache add libc6-compat && \
    rm -f /tmp/ngrok.zip

add ngrok.yml /root/.ngrok2/ngrok.yml


entrypoint [ "/usr/local/bin/ngrok"]
cmd [ "http", "80" ]

