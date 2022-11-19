# Frea Search のアーキテクチャ

## メインサーバー (SearXNG)
Frea Search の中核というかベース。UIや基本的な検索機能を提供。

### plugin (searx/plugins)
文字通りSearXNGのプラグイン

### engines (searx/engines)
外部の検索エンジンから結果をスクレイピングするプログラム

### UI
#### searx/templates
htmlのテンプレート。これをベースにhtmlがレンダリングされブラウザに返されます。

#### searx/static/themes/simple/
CSSやフォントなどUIの部品。

## サブシステム（./subsystems)
強調スニペットや独自インデックスに関する処理を行う部分です。メインのプロセスとは別のプロセスとして実行されます。基本的にサブシステムとメインサーバー（SearXNG）間の通信はUNIXソケットを使用します。

## init (./tools/init)
Dockerコンテナ内のエントリーポイントです。サブシステムとメインサーバーを起動させます。

