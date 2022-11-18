FROM fedora:latest

WORKDIR /app

RUN dnf update -y
RUN dnf install -y python3 python3-pip boost mecab-ipadic sqlite python3-devel boost-devel mecab-devel sqlite-devel make automake gcc gcc-c++

COPY ./requirements.txt .
RUN pip3 install --no-cache -r requirements.txt

RUN groupadd app \
 && useradd -d /app -s /bin/sh -g app app


RUN sudo dnf install -y util-linux
RUN chown -R app:app /app \
 && su app -c "python3 -m pygeonlp.api setup /usr/pygeonlp_basedata"

RUN dnf remove -y python3-devel boost-devel mecab-devel sqlite-devel make automake gcc gcc-c++
RUN dnf autoremove -y

COPY --chown=app:app . .

EXPOSE 8000
CMD ["su", "app", "-c", "python3 init.py"]
