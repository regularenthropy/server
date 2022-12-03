# インスタンスを建てる
Frea search をセルフホストする方法について説明します。  
セルフホストインスタンスはプライバシー、速度の点で他人のインスタンスを使用するより優れています。

## フロントサーバー

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
# オプション: 自宅サーバーで実行する際は強く推奨
outgoing:
  request_timeout: 3.0
  proxies:
    all://:
      - socks5h://tor:9050
  using_tor_proxy: true
```

#### docker-compose.yml
```
version: '3'

services:
version: '3.7'

services:
  redis:
    container_name: redis
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

  # オプション: 自宅サーバーで実行する際は強く推奨
  tor:
    image: osminogin/tor-simple
    container_name: tor
    restart: always
    volumes:
      - ./torrc:/etc/tor/torrc:ro

  frea-ui:
    container_name: frea-ui
    image: nexryai/frea-ui:devel
    restart: always
    depends_on:
      - db
      - redis
      - tor
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

```

### step2
`sed -i -e "s/ultrasecretkey/$(openssl rand -hex 16)/g" "settings.yml"`を実行しサーバーのシークレットキーを設定します。  
必要に応じて、settings.yml内の以下の値を編集します。

 - `privacypolicy_url` インスタンスにプライバシーポリシーが存在する場合、そのURLを指定します。


### step3
実行します。  
`docker-compose up`

### step4
適当なhttpサーバーをシステムにインストールし、`localhost:8888`へリバースプロキシするように設定します。https化するのを忘れないでください。


## APIサーバー
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
      - "127.0.0.1:8000:8000"
    cap_drop:
      - ALL
    cap_add:
      - SETGID
      - SETUID
      - DAC_OVERRIDE
```

### step2
実行します。  
`docker-compose up`

### step3
適当なhttpサーバーをシステムにインストールし、`localhost:8000`へリバースプロキシするように設定します。https化するのを忘れないでください。
