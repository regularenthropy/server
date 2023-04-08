FROM ubuntu:latest
WORKDIR /app

COPY ./requirements.txt .

RUN apt update -y \
 && apt upgrade -y \
 && apt install -y tini openssl python3 python3-pip nginx libpq5 redis python3-dev libboost-dev libmecab-dev libpq-dev build-essential util-linux brotli wget unzip \
 && pip3 install --no-cache -r requirements.txt \
 && groupadd -g 1000 app \
 && useradd -d /app -s /bin/sh -u 1000 -g app app \
 && chown -R app:app /app \
 #&& su app -c "python3 -m pygeonlp.api setup /usr/pygeonlp_basedata" \
 && touch /var/run/nginx.pid \
 && chown -R app:app /var/run/nginx.pid \
 && chown -R app:app /var/lib/nginx \
 && chown -R app:app /var/log/nginx \
 && apt purge -y python3-dev libpq-dev build-essential \
 && apt autoremove --purge -y \
 && apt clean

COPY --chown=app:app . .

RUN cp -r /app/etc/* /etc/ \
 && cd /app \
 && rm -rf etc requirements.txt \
 && echo "dicdir = /app/mecab/mecab-ipadic-neologd" > /usr/local/etc/mecabrc \
 && apt install -y curl \
 && cd /app/blocklists/ \
 && bash mkblocklist.sh \
 && mv new.yml main.yml \
 && apt purge -y curl \
 && apt autoremove --purge -y \
 && apt clean \
 && chown app:app -R /app

USER app
CMD ["tini", "--", "/usr/bin/python3", "-u", "/app/core.py"]
