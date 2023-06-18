FROM python:latest as base
RUN mkdir /app
COPY . /app/
WORKDIR /app
COPY ./requirements.txt /tmp/
RUN pip install -Ur /tmp/requirements.txt

FROM base as production
COPY ./docker-entrypoint.sh /usr/bin/docker-entrypoint.sh
CMD ["bash", "/usr/bin/docker-entrypoint.sh"]