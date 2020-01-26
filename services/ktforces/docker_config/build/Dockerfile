FROM node:13.7-alpine

MAINTAINER tg: @kekov

ADD . /app
WORKDIR /app

RUN chmod +x ./build.sh

CMD ["./build.sh"]