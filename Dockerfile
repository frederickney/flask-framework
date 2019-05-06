FROM debian:buster

RUN apt update && \
    apt install python3 python3-pip sudo -y

COPY requirements.txt /requirements

COPY extensions.txt /extensions

COPY entrypoint.sh /entrypoint

RUN pip3 install --upgrade pip && \
    pip3 install -r /requirements && \
    pip3 install -r /extensions && \
    chmod +x /entrypoint && \
    useradd dev -u 1000 -m && \
    usermod -aG sudo dev && \
    mkdir -p /home/dev && \
    chown -R dev:dev /home/dev && \
    mkdir -p /etc/server/ && \
    mkdir -p /var/log/server/ && \
    chown -R dev:dev /var/log/server/ && \
    echo "%sudo ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

COPY ./config/config.docker.json /etc/server/config.json

USER dev

CMD /bin/bash
