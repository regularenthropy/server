FROM fedora:latest

WORKDIR /app

RUN dnf update -y
RUN dnf install -y python3 python3-pip nginx boost mecab-ipadic sqlite redis python3-devel boost-devel mecab-devel sqlite-devel make automake gcc gcc-c++ util-linux

COPY ./requirements.txt .
RUN pip3 install --no-cache -r requirements.txt

COPY ./searxng/src/requirements.txt ./searxng/src/
RUN pip3 install --no-cache -r ./searxng/src/requirements.txt

COPY ./searxng/settings.yml /etc/searxng/

RUN groupadd app \
 && useradd -d /app -s /bin/sh -g app app

RUN chown -R app:app /app \
 && su app -c "python3 -m pygeonlp.api setup /usr/pygeonlp_basedata"

RUN dnf remove -y python3-devel boost-devel mecab-devel sqlite-devel make automake gcc gcc-c++
RUN dnf autoremove -y

COPY --chown=app:app . .
RUN cd ./searxng/src && pip install -e .

EXPOSE 8000
CMD ["su", "app", "-c", "python3 core.py"]
