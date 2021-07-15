FROM python:3.7-alpine

ENV BUILD_DEPS="build-base gcc libc-dev"
ENV RUNTIME_DEPS=""

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /irteamdash

WORKDIR /irteamdash

ADD ./REQUIREMENTS.txt /irteamdash/REQUIREMENTS.txt

RUN apk update &&\
    apk add --no-cache $BUILD_DEPS $RUNTIME_DEPS &&\
    pip install --no-cache-dir --upgrade pip &&\
    pip install --no-cache-dir -r REQUIREMENTS.txt &&\
    apk del $BUILD_DEPS &&\
    rm -rf /var/cache/apk/*

# docker run --rm -it --name irteamdash -v $PWD:/irteamdash -p 80:5000 --entrypoint "/bin/sh" irteamdash
# gunicorn --bind 0.0.0.0:5000 --worker-class eventlet --workers 1 irteamdash.wsgi:app --error-logfile - --log-level DEBUG
