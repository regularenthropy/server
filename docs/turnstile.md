# Turnstileを使用してインスタンスの安全性を向上させる
Frea Search は Turnstile によるbot対策をサポートしています。これは主に攻撃の対象となるような大規模なインスタンスでの使用を想定したものです。  

## 重要: Turnstileを使用する際の注意点
 - ユーザーには一定時間ごとにチャレンジページが表示されるため、体感速度が大幅に低下します。
 - APIは使用できなくなります。
 - ユーザーのIPアドレスがCloudflareに送信されるため、プライバシーが低下します。
 - JavascriptとCookieが必須になります。
 - マイナーなブラウザを使用している場合、チャレンジを解決できない可能性があります。

## 設定方法
それぞれの設定ファイルに以下を追記します。

### settings.yml
```
server:
  secret_key: "secretkey"
  use_turnstile: true ←これを追記
```

### docker-compose.yml
```
  frea:
    [省略]
    environment:
      TURNSTILE_SECRET_KEY: "[Turnstileのシークレットキー]"
      TURNSTILE_SITE_KEY: "[Turnstileのサイトキー]"

```
