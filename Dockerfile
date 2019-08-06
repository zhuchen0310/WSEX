FROM python:3.6.5

# App Setup
WORKDIR /opt/wsex
ADD . /opt/wsex

# Env Setup
ENV PYTHONPATH=$PYTHONPATH:/opt/wsex
ENV PYTHONPATH=/opt/wsex:$PYTHONPATH
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir /opt/logs
