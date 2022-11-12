FROM alpine:latest

WORKDIR /app

RUN apk add python3 py3-pip

COPY . .
RUN pip3 install --no-cache -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "server:app", "--workers", "5"]
