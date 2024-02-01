FROM debian:buster

RUN apt update && \
    apt install python3 python3-pip libldap2-dev libsasl2-dev sudo -y && \
    pip3 install --upgrade pip && \
    pip3 install flask-framework-mvc &&\
    useradd flask -u 1000 -m && \
    mkdir -p /home/flask && \
    chown -R flask:flask /home/flask && \
    mkdir -p /etc/server/ && \
    mkdir -p /var/log/server/ && \
    mkdir -p /srv/http/ && \
    chown -R flask:flask /var/log/server/ /srv/http/ && \
    chmod -R 775 /var/log/server/ /srv/http/

COPY ./config/* /etc/server/

USER flask

WORKDIR /srv/http

ENTRYPOINT /bin/bash