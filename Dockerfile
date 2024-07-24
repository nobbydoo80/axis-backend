# syntax = docker/dockerfile:1.2
# Docker File for Axis

# docker build --secret id=github_token,env=GIT_AUTH_TOKEN --platform=linux/arm64 --platform=linux/amd64 --tag pivotalenergy/axis:latest .
# docker run -e DJANGO_SETTINGS_MODULE=settings.dev_docker -p 8000:8000 -ti pivotalenergy/axis

FROM python:3.10-alpine

EXPOSE 8000

MAINTAINER Pivotal Energy Solutions (steven@pivotal.energy)

RUN apk add --update --no-cache --virtual .build-deps \
    g++ make bzip2-dev zlib-dev libffi-dev libmemcached-dev \
    libxml2  libxml2-dev libjpeg-turbo-dev \
    libwebp-dev tcl-dev tk-dev && \
    apk add libxslt-dev freetype-dev mariadb-dev git which sudo docker

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=secret,id=github_token,dst=/root/.token \
    git config --global url.https://$(cat /root/.token)@github.com/.insteadOf https://github.com && \
    pip install --upgrade pip && \
    pip install ninja && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir watchdog PyYAML argh gunicorn && \
    rm -f ~/.gitconfig && ls -altr && \
    apk del .build-deps

COPY celeryapp.py urls.py wsgi.py /app/
COPY settings /app/settings
COPY webpack /app/webpack
COPY axis /app/axis
COPY .docker-entrypoint.sh docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
