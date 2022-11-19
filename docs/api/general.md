# 検索API仕様（ver2.0）

## Example

### 一般カテゴリ
```
{
  "query": "ラクスマン",
  "number_of_results": 0,
  "results": [
    {
      "url": "https://ja.wikipedia.org/wiki/%E3%82%A2%E3%83%80%E3%83%A0%E3%83%BB%E3%83%A9%E3%82%AF%E3%82%B9%E3%83%9E%E3%83%B3",
      "title": "アダム・ラクスマン - Wikipedia",
      "content": "アダム・キリロヴィチ・ラクスマン （ 露: Адам Кириллович Лаксман, 典: Adam Laxman 、 1766年 - 1806年 以降）は、 ロシア帝国 （ ロマノフ朝 ）の軍人で陸軍中尉、北部沿海州 ギジガ 守備隊長。. ロシア最初の遣日使節。. 父は フィンランド 生まれの博物学者 キリル・ラクスマン で、漂流民の 大黒屋光太夫 の保護と帰国に尽力した人物。. アダム ...",
      "engine": "google",
      "parsed_url": [
        "https",
        "ja.wikipedia.org",
        "/wiki/%E3%82%A2%E3%83%80%E3%83%A0%E3%83%BB%E3%83%A9%E3%82%AF%E3%82%B9%E3%83%9E%E3%83%B3",
        "",
        "",
        ""
      ],
      "template": "default.html",
      "engines": [
        "google",
        "neeva",
        "duckduckgo",
        "goo"
      ],
      "positions": [
        1,
        3,
        1,
        5
      ],
      "is_onion": false,
      "score": 10.133333333333333,
      "category": "general",
      "pretty_url": "https://ja.wikipedia.org/wiki/%E3%82%A[...]A9%E3%82%AF%E3%82%B9%E3%83%9E%E3%83%B3",
      "open_group": true
    },
 [省略]
    {
      "title": "ラクスマン来航（根室）欧米諸国による開国要求の最初 1792年 ...",
      "content": "ラクスマン来航（根室）欧米諸国による開国要求の最初 1792年. 1792（寛政4）年10月20日、ロシアの使節ラクスマンが根室港に来航した。. 日本人漂流民・大黒屋光太夫ら3名の日本人の返還という名目で、国書を持参し日本に通商を求めてきた。. 1792（寛政4）年は鎖国のただ中、松平定信の治世下である。. 10月20日、ロシアの使節ラクスマンが根室港に来航した ...",
      "url": "https://500ji-nihonshi.com/edo/post-805/",
      "engine": "duckduckgo",
      "parsed_url": [
        "https",
        "500ji-nihonshi.com",
        "/edo/post-805/",
        "",
        "",
        ""
      ],
      "template": "default.html",
      "engines": [
        "duckduckgo"
      ],
      "positions": [
        16
      ],
      "score": 0.0625,
      "category": "general",
      "pretty_url": "https://500ji-nihonshi.com/edo/post-805/"
    }
  ],
  "answers": [
    null
  ],
  "corrections": [],
  "infoboxes": [
    {
      "infobox": "ラクスマン",
      "id": "https://www.wikidata.org/entity/Q42443988",
      "content": "インドにおける男性の名前 (लक्ष्मण)",
      "img_src": null,
      "urls": [
        {
          "title": "Wikidata",
          "url": "http://www.wikidata.org/entity/Q42443988"
        }
      ],
      "attributes": [
        {
          "label": "文字体系",
          "value": "デーヴァナーガリー",
          "entity": "P282"
        }
      ],
      "engine": "wikidata",
      "engines": [
        "wikidata"
      ]
    }
  ],
  "suggestions": [
    "ラクスマン 来航 理由",
    "ラクスマン 根室 なぜ",
    "ラックスマン アンプ 中古",
    "1792年 ラクスマン",
    "ラクスマン何した",
    "ラクスマン 根室",
    "ラクスマン来航",
    "ラクスマン レザノフ",
    "レザノフ 航路",
    "レザノフ 何しに来た",
    "ラックスマン ロシア",
    "ラクスマン 出身",
    "ラクスマン エカチェリーナ",
    "ラクスマン 来航場所",
    "ラクスマン 生涯"
  ],
  "unresponsive_engines": []
}
```

## 解説

### results
文字通り結果の一覧です。

### answers
強調スニペットの内容です。数パターンあるので注意してください。

#### 強調スニペットなし
```
  "answers": [
    null
  ],
```

#### 標準強調スニペット
```
  "answers": [
    {
      "type": "answer",
      "answer": "日本側では、日本で最初のロシア語辞典を作成したり、エカテリーナ号の模型を作ったり、ロシアの地図を写し地名を聞き取ったりしました。 ラクスマンらも、日本の地図を写し、植物・鉱物を採集し標本にしたり、根室港周辺を測量したり、アイヌの人々と日本商人らの関係を聞き取ったりしました。2018/03/01"
    }
  ],
```

#### 天気情報
`weather_icon_2d`は二日目（翌日）の天気です。
```
  "answers": [
    {
      "type": "weather",
      "answer": "現在の天気: fair_day",
      "weather": "MET Norway",
      "hide_icon": "true",
      "weather_icon": "fair_day",
      "weather_temp": 15.9,
      "weather_icon_2d": "lightrain",
      "weather_temp_2d": 14.5,
      "weather_icon_3d": "lightrainshowers_day",
      "weather_temp_3d": 17.6,
      "d2_disp": "11/20",
      "d3_disp": "11/21"
    }
  ],
```

#### 津波情報あり
これの実装は必須ではありませんが、目立つよう特別メッセージを表示することを強く推奨します。  
```
  "answers": [
    {
      "type": "tsunami_warn",
      "message": "警告: 現在、一部の沿岸地域に津波警報が発表されています。",
      "tsunami": "true",
      "hide_icon": "true"
    },
    {
      "type": "answer",
      "answer": "日本側では、日本で最初のロシア語辞典を作成したり、エカテリーナ号の模型を作ったり、ロシアの地図を写し地名を聞き取ったりしました。 ラクスマンらも、日本の地図を写し、植物・鉱物を採集し標本にしたり、根室港周辺を測量したり、アイヌの人々と日本商人らの関係を聞き取ったりしました。2018/03/01"
    }
  ],
```
