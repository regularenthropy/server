# インスタンスを建てる
Frea search をセルフホストする方法について説明します。  
セルフホストインスタンスはプライバシー、速度の点で他人のインスタンスを使用するより優れています。

### step0 (通常は不要な手順)
手動でビルドする場合は、[このリポジトリ](https://git.freasearch.org/frea/search)をcloneし`docker build --tag frea:latest --file Dockerfile .`を実行してください。

### step1
適当なディレクトリへ移動し、以下の2つのファイルを作成します。

#### settings.yml
```
use_default_settings: true

general:
  debug: false
  privacypolicy_url: false
  donation_url: https://donate.freasearch.org

server:
  secret_key: "ultrasecretkey"
  
# communication with search engines
outgoing:
  # default timeout in seconds, can be override by engine
  request_timeout: 3.0
  # uncomment below section if you want to use a proxyq see: SOCKS proxies
  #   https://2.python-requests.org/en/latest/user/advanced/#proxies
  # are also supported: see
  #   https://2.python-requests.org/en/latest/user/advanced/#socks
  #
  #  proxies:
  #    all://:
  #      - http://proxy1:8080
  #      - http://proxy2:8080
  #
```

#### docker-compose.yml
```
version: '3'

services:
  db:
    container_name: db
    image: postgres:alpine
    restart: always
    networks:
      - frea
    environment:
      POSTGRES_DB: freasearch
      POSTGRES_USER: freasearch
      POSTGRES_PASSWORD: freasearch
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - DAC_READ_SEARCH
      - FOWNER
      - SETGID
      - SETUID
    volumes:
      - ./data:/var/lib/postgresql/data

  redis:
    container_name: redis
    image: redis:alpine
    restart: always
    command: redis-server --save "" --appendonly "no" --protected-mode "no"
    networks:
      - frea
    tmpfs:
      - /var/lib/redis
      - /var/redis
    cap_drop:
      - ALL
    cap_add:
      - SETGID
      - SETUID
      - DAC_OVERRIDE

  frea:
    container_name: frea
    image: nexryai/frea:latest
    restart: always
    depends_on:
      - db
      - redis
    networks:
      - frea
    environment:
      POSTGRESQL_HOST: db
      POSTGRESQL_USER: freasearch
      POSTGRESQL_PASSWORD: freasearch
      COUNT_USERS: "true"
      TZ: Asia/Tokyo
    ports:
     - "127.0.0.1:8888:8888"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - DAC_OVERRIDE
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./settings.yml:/etc/frea/settings.yml:ro

networks:
  frea:

```

### step2
`sed -i -e "s/ultrasecretkey/$(openssl rand -hex 16)/g" "settings.yml"`を実行しサーバーのシークレットキーを設定します。  
必要に応じて、settings.yml内の以下の値を編集します。

 - `privacypolicy_url` インスタンスにプライバシーポリシーが存在する場合、そのURLを指定します。
 - `proxies` 外部の検索エンジンへリクエストを送信する際に使用するプロキシを設定します。


### step3
実行します。  
`docker-compose up`

### step4
適当なhttpサーバーをシステムにインストールし、`localhost:8888`へリバースプロキシするように設定します。https化するのを忘れないでください。
