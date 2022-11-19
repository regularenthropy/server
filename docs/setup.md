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
適当なディレクトリへ移動し、以下の3つのファイルを作成します。

#### setting.yml
長いので[ここから](https://git.freasearch.org/core/api/-/raw/main/searxng/settings.yml?inline=false)ダウンロード

##### アップストリームエンジンとの通信にTorを使用する場合（推奨）
`outgoing:`セクションを以下のように変更  

```
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

  # オプション: Tor利用時のみ
  tor:
    image: osminogin/tor-simple
    container_name: tor
    restart: always
    volumes:
      - ./torrc:/etc/tor/torrc:ro

  searxng:
    container_name: searxng
    image: searxng/searxng:latest
    volumes:
      - ./settings.yml:/etc/searxng/settings.yml:ro
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
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

#### torrc（Tor利用時のみ）
```
SocksPort 0.0.0.0:9050

# オプション: ブリッジを使用する場合のみ
UseBridges 1
Bridge [ブリッジのアドレス]:[ブリッジのポート]

# オプション: 高速化、もしくはプライバシー強化のためノードのリージョンを制限したい場合のみ
StrictNodes 1
ExcludeNodes {bd},{be},{bf},{bg},{ba},{bb},{wf},{bl},{bm},{bn},{bo},{bh},{bi},{bj},{bt},{jm},{bv},{bw},{ws},{bq},{br},{bs},{je},{by},{bz},{ru},{rw},{rs},{lt},{re},{lu},{lr},{ro},{ls},{gw},{gu},{gt},{gs},{gr},{gq},{gp},{gy},{gg},{gf},{ge},{gd},{gb},{ga},{gn},{gm},{gl},{kw},{gi},{gh},{om},{jo},{hr},{ht},{hu},{hk},{hn},{hm},{ad},{pr},{ps},{pw},{pt},{kn},{py},{ai},{pa},{pf},{pg},{pe},{pk},{ph},{pn},{pl},{pm},{zm},{eh},{ee},{eg},{za},{ec},{al},{ao},{kz},{et},{zw},{ky},{es},{er},{me},{md},{mg},{mf},{ma},{mc},{uz},{mm},{ml},{mo},{mn},{mh},{mk},{mu},{mt},{mw},{mv},{mq},{mp},{ms},{mr},{au},{ug},{my},{mx},{vu},{fr},{aw},{af},{ax},{fi},{fj},{fk},{fm},{fo},{ni},{nl},{no},{na},{nc},{ne},{nf},{ng},{nz},{np},{nr},{nu},{ck},{ci},{ch},{co},{cn},{cm},{cl},{cc},{ca},{cg},{cf},{cd},{cz},{cy},{cx},{cr},{kp},{cw},{cv},{cu},{sz},{sy},{sx},{kg},{ke},{ss},{sr},{ki},{kh},{sv},{km},{st},{sk},{sj},{si},{sh},{so},{sn},{sm},{sl},{sc},{sb},{sa},{se},{sd},{do},{dm},{dj},{dk},{de},{ye},{at},{dz},{us},{lv},{uy},{yt},{um},{tz},{lc},{la},{tv},{tt},{tr},{lk},{li},{tn},{to},{tl},{tm},{tj},{tk},{th},{tf},{tg},{td},{tc},{ly},{va},{vc},{ae},{ve},{ag},{vg},{iq},{vi},{is},{ir},{am},{it},{vn},{aq},{as},{ar},{im},{il},{io},{in},{lb},{az},{ie},{id},{ua},{qa},{mz}
ExitNodes {jp},{kr},{tw},{hk},{sg}
```

### step2
`sed -i -e "s/ultrasecretkey/$(openssl rand -hex 16)/g" "settings.yml"`を実行しサーバーのシークレットキーを設定します。  

### step3
実行します。  
`docker-compose up`

### step4
適当なhttpサーバーをシステムにインストールし、`localhost:8000`へリバースプロキシするように設定します。https化するのを忘れないでください。
