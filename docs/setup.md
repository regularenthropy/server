# インスタンスを建てる
Frea search をセルフホストする方法について説明します。  
セルフホストインスタンスはプライバシー、速度の点で他人のインスタンスを使用するより優れています。

## APIサーバー
### docker-compose.yml
```
version: '3.7'

services:
  frea:
    image: nexryai/frea-api:latest
    restart: always
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      - FREA_DEBUG_MODE=false
      # プロキシを使う際はここに記述
      # - FREA_PROXY_0=socks5h://127.0.0.1:9050
      # - FREA_PROXY_1=socks5h://127.0.0.1:9050
      # ...
      - POSTGRES_HOST=db
      - POSTGRES_DB=frea
      - POSTGRES_USER=frea
      - POSTGRES_PASSWD=CHANGEME
    links:
      - db
    volumes:
      - ./mecab:/app/mecab

  db:
    restart: always
    image: postgres:15
    environment:
      - POSTGRES_DB=frea
      - POSTGRES_USER=frea
      - POSTGRES_PASSWORD=CHANGEME
    volumes:
      - ./db:/var/lib/postgresql/data
```

## UIサーバー

### docker-compose.yml
```
version: '3.7'

services:  
  ui:
    image: nexryai/frea-ui:latest
    restart: always
    ports:
      - "127.0.0.1:3002:3000"
    environment:
      - NEXT_TELEMETRY_DISABLED=1
      - API_URL=[APIサーバーのURL（公式は https://api.freasearch.org）]
```
