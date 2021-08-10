FROM ubuntu:20.04

ENV TERM linux
## for apt to be noninteractive
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

ADD ./kubectl /usr/local/bin/kubectl

RUN apt-get update && \
    apt-get install -y software-properties-common wget curl tar gzip bash ca-certificates supervisor git

RUN apt-get install -y python3-dev python3-pip python3-venv
RUN python3 -m venv /root/venv
RUN . /root/venv/bin/activate && pip3 install -U pip setuptools wheel ipdb ipython

# COPY ./requirements.txt /root/requirements.txt
# RUN . /root/venv/bin/activate && pip3 install -r /root/requirements.txt

COPY setup/kubectl_game_config /root/kubectl_game_config

COPY setup/supervisord.conf /etc/supervisord.conf

COPY ./bot.py /root

CMD cd /root && /root/venv/bin/python bot.py
