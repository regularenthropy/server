FROM fedora:37
WORKDIR /app

COPY ./requirements.txt .
COPY ./searxng/src/requirements.txt ./searxng/src/

RUN dnf update -y \
 && dnf install -y python3 python3-pip nginx boost mecab-ipadic sqlite libpq redis python3-devel boost-devel mecab-devel sqlite-devel libpq-devel make automake gcc gcc-c++ util-linux tor brotli wget unzip \
 && pip3 install --no-cache -r requirements.txt \
 && pip3 install --no-cache -r ./searxng/src/requirements.txt \

 && groupadd app \
 && useradd -d /app -s /bin/sh -g app app \

 && chown -R app:app /app \
 && su app -c "python3 -m pygeonlp.api setup /usr/pygeonlp_basedata" \

 && mkdir /var/lib/tor_p1 /var/lib/tor_p2 /var/lib/tor_e1 /var/lib/tor_e2 \
 && chown app:app /var/lib/tor_p1 \
 && chown app:app /var/lib/tor_p2 \
 && chown app:app /var/lib/tor_e1 \
 && chown app:app /var/lib/tor_e2 \

 && touch /var/run/nginx.pid \
 && chown -R app:app /var/run/nginx.pid \
 && chown -R app:app /var/lib/nginx \
 && chown -R app:app /var/log/nginx \
 && dnf remove -y python3-devel boost-devel mecab-devel sqlite-devel libpq-devel make automake gcc gcc-c++ \
 && dnf autoremove -y

COPY --chown=app:app . .
RUN cd ./front/src \
 && npm i \
 && echo "API_URL=https://127.0.0.1:8889" > .env.local \
 && cd /app
COPY ./etc/ /etc/

RUN find ./searxng/src/searx/static \( -name '*.html' -o -name '*.css' -o -name '*.js' \
    -o -name '*.svg' -o -name '*.eot' \) \
    -type f -exec gzip -9 -k {} \+ -exec brotli --best {} \+ \
 && cd ./searxng/src && pip install -e . \
 && rm -rf .coveragerc .dir-locals.el .dockerignore .git .gitattributes .github .gitignore .nvmrc .pylintrc .weblate .yamllint.yml AUTHORS.rst CHANGELOG.rst CONTRIBUTING.md Dockerfile LICENSE Makefile PULL_REQUEST_TEMPLATE.md README.rst SECURITY.md babel.cfg dockerfiles docs examples manage package.json pyrightconfig-ci.json pyrightconfig.json requirements-dev.txt requirements.txt searxng_extra setup.py src tests utils \
 && cd /app \
 && rm -rf etc requirements.txt \
 && echo "dicdir = /app/mecab/mecab-ipadic-neologd" > /usr/local/etc/mecabrc \
 && chown app:app /etc/searxng/settings.yml

ENV FREA_DEBUG_MODE=false

CMD ["su", "app", "-c", "python3 -u core.py"]
