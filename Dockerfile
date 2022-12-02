FROM fedora:latest

WORKDIR /app

RUN dnf update -y
RUN dnf install -y python3 python3-pip nginx boost mecab-ipadic sqlite redis python3-devel boost-devel mecab-devel sqlite-devel make automake gcc gcc-c++ util-linux tor

COPY ./requirements.txt .
RUN pip3 install --no-cache -r requirements.txt

COPY ./searxng/src/requirements.txt ./searxng/src/
RUN pip3 install --no-cache -r ./searxng/src/requirements.txt

COPY ./searxng/settings.yml /etc/searxng/
COPY ./config/nginx /etc/nginx
COPY ./config/tor/torrc1 /etc/tor/
COPY ./config/tor/torrc2 /etc/tor/

RUN groupadd app \
 && useradd -d /app -s /bin/sh -g app app

RUN chown -R app:app /app \
 && su app -c "python3 -m pygeonlp.api setup /usr/pygeonlp_basedata"

RUN mkdir /var/lib/tor1 /var/lib/tor2 \
 && chown app:app /var/lib/tor1 \
 && chown app:app /var/lib/tor2

RUN touch /var/run/nginx.pid && \
  chown -R app:app /var/run/nginx.pid && \
  chown -R app:app /var/lib/nginx && \
  chown -R app:app /var/log/nginx

RUN dnf remove -y python3-devel boost-devel mecab-devel sqlite-devel make automake gcc gcc-c++
RUN dnf autoremove -y

COPY --chown=app:app . .
RUN cd ./searxng/src && pip install -e .

EXPOSE 8000
CMD ["su", "app", "-c", "python3 core.py"]
