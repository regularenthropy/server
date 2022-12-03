# インスタンスを建てる
Frea search をセルフホストする方法について説明します。  
セルフホストインスタンスはプライバシー、速度の点で他人のインスタンスを使用するより優れています。


### step1
適当なディレクトリへ移動し、以下のファイルを作成します。

#### docker-compose.yml
```
version: '3'

services:
version: '3.7'

services:
  db:
    container_name: db
    image: "redis:alpine"
    command: redis-server --save "" --appendonly "no"
    tmpfs:
      - /var/lib/redis
    cap_drop:
      - ALL
    cap_add:
      - SETGID
      - SETUID
      - DAC_OVERRIDE

  frea-api:
    image: "nexryai/frea-api:latest"
    restart: always
    ports:
      - "127.0.0.1:8080:8080"
```

### step2
実行します。  
`docker-compose up`

### step3
適当なhttpサーバーをシステムにインストールし、`localhost:8080`へリバースプロキシするように設定します。https化するのを忘れないでください。
