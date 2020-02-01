FROM python:3.7-alpine

MAINTAINER tg: @pomo_mondreganto

ENV PYTHONUNBUFFERED=1

RUN apk add gcc musl-dev make

ADD backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD docker_config/backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ADD backend /app

CMD ["/entrypoint.sh"]
