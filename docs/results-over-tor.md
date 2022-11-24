# Torネットワークを経由してアップストリームエンジンからの結果を取得する
Frea Search のセルフホストインスタンス上でTorを使用して結果を取得する方法をこのセクションでは説明します。  
これは主に以下のユーザーを対象とした機能です。

 - 高度なプライバシーを求めるユーザー
 - 自宅からアップストリームエンジンにリクエストを送信したくないが、プロキシサーバーを金銭的な事情で構築できないユーザー
 - 大量のリクエストを捌くインスタンス
 
## 設定
https://docs.freasearch.org/setup/ の手順でセットアップを行っていることが前提条件です。  
設定ファイルに以下のように追記します。

#### settings.yml
```
outgoing:
  request_timeout: 3.0
  proxies:
    all://:
      - socks5h://tor:9050
  using_tor_proxy: true

```

### docker-compose.yml
```
  tor:
    image: osminogin/tor-simple
    container_name: tor
    restart: always
    volumes:
      - ./torrc:/etc/tor/torrc:ro
```

続いて`torrc`というファイルを作成し、以下の内容を書き込みます。
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

Dockerコンテナを再起動したら完了です。
