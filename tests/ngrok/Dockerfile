from alpine:latest

run wget -O /tmp/ngrok.zip https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip && \
    unzip -d /usr/local/bin /tmp/ngrok.zip  && \
    apk --no-cache add libc6-compat && \
    rm -f /tmp/ngrok.zip

add ngrok.yml /root/.ngrok2/ngrok.yml


entrypoint [ "/usr/local/bin/ngrok"]
cmd [ "http", "80" ]

