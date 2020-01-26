FROM node:13.7-alpine

MAINTAINER tg: @kekov

ADD package.json /app/package.json
ADD yarn.lock /app/yarn.lock
WORKDIR /app
RUN yarn install

ADD . /app

RUN chmod +x ./build.sh

CMD ["./build.sh"]