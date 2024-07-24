# Docker File for Axis
# docker build -t axis-messaaging  .
# docker run --env-file .env -ti axis_node


FROM python:3.10-alpine

EXPOSE 8002
EXPOSE 8080

ENV APP_HOST app
ENV DJANGO_HTTP_PORT 8000

MAINTAINER Pivotal Energy Solutions (sklass@pivotal.energy)

RUN apk add nodejs npm git

WORKDIR /app

COPY ./axis/messaging/server /app

RUN cd /app && npm install && npm install -g forever

ENTRYPOINT ["forever", "-m", "10", "--minUptime", "1000", "--spinSleepTime",  "5000", "server.js"]
