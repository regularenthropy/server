# Frea Search のアーキテクチャ

## Search API
検索API

### `core.py`
各モジュールを呼び出す中枢システムです。各モジュールは別プロセスで並列で動作します。

### `worker.py`
検索を実行し、リクエストに応答します。`inteli_e.py`をロードし強調スニペットの処理も行います。

### `analyze.py`
結果をAIで解析します。

### `index_manager.py`, `job_manager.py`
インデックスを管理します。

### `searx.py`
SearXNGの設定の管理、呼び出しを担当します。

### `nginx.py`, `redis.py`
それぞれnginxとredisを起動します。

## Sea UI
公式のフロントエンドです。

