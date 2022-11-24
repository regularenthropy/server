# Frea Search のアーキテクチャ

## スクレイピングサーバー (SearXNG)
アップストリームエンジンから結果を取得します。中身はSearXNGですが設定を変えて最適化しています。

## コアAPIサーバー
repo: [Gitlab](https://git.freasearch.org/core/api)  [mirror](https://github.com/frea-search/api-server)  
検索APIを提供するサーバーです。スクレイピングサーバーから取得した情報を加工し、よりエレガントな結果にします。  
結果の最適化アルゴリズムである`Innocence Force`はここに実装されています。また天気情報スニペットに使用する情報もここで取得、加工します。
Pythonで書かれており将来的にはAIをしようしてサイトを評価する機能などもここに実装予定です。  
一般公開されているAPIのエンドポイントでもあります。

## Legacy UI
repo: [Gitlab](https://git.freasearch.org/core/search)  [mirror](https://github.com/frea-search/ui-legacy)  
新しいUIが完成するまでのつなぎのフロントエンドで、SearXNGベースの従来の Frea Search を加工して作られました。

## Frea Worker + Sea
Ablaze内で開発が進められている次世代のフロントエンドです。Workerは強調スニペット関係の処理を行います。  
これは近い将来、Legacy UIを置き換える予定です。


