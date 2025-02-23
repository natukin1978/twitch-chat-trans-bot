# Twitchのチャットの外国語を翻訳するBOT

## 主な特徴

### 外国語と判定された時だけ翻訳します

外国語ではない場合は翻訳しないため、翻訳サービスの使用量が節約できます。

### 合成音声による読み上げ

※ 要 AssistantSeika

- COEIROINK, AivisSpeechなどの合成音声の読み上げを行います
- 翻訳された場合、翻訳結果のみ読み上げを行います
- 同じ人が連続で発言した場合、お名前の読み上げを省略します
- ユーザー毎に読み上げ音声を変える事もできます

※ 要 わんコメ

- わんコメで設定したニックネームを使ってお名前を読み上げます。


これらの特徴に恩恵を受けないなら[翻訳ちゃん(twitchTransFreeNext)](https://github.com/sayonari/twitchTransFreeNext)という優れたアプリがあるのでそちらを使ってください。

## 設定

※ JSONファイルを編集する場合、JSON形式をサポートしているテキストエディタの使用を推奨します。

### config.json

| キー                        | 概要                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------ |
| twitch.loginChannel         | ログインする対象のチャンネル                                                         |
| twitch.accessToken          | 翻訳結果をコメントするユーザーのOAuthトークン https://twitchapps.com/tmi/            |
| translate.target            | 翻訳結果の言語(つまり母国語)                                                         |
| translate.service           | 使用する翻訳サービス(`deepL`もしくは`translate_gas`)                                 |
| deepL                       | DeepLのエンドポイントやAPIキーを設定します                                           |
| translate_gas               | GAS(Google Apps Script)の翻訳APIのURLを設定します ※1                                 |
| assistantSeika              | 合成音声による読み上げを行いたい時の設定                                             |
| assistantSeika.defaultCid   | キャラクターのID                                                                     |
| honorifics.default          | 通常使用する敬称で、これをユーザー名の末尾に追加します                               |
| honorifics.other            | その他の敬称。ユーザー名の末尾がこのリストに含まれている場合はそのまま読み上げます   |
| oneComme.pathUsersCsv       | わんコメのユーザーリストをCSV出力したパスを指定します。(ニックネームで使用)          |

※1 Google翻訳APIを無料で作る方法
https://qiita.com/satto_sann/items/be4177360a0bc3691fdf

### exclude_words.txt

翻訳を除外するキーワード郡を設定する事ができます。

- 完全一致で指定します
- 大文字・小文字及び全角半角を区別しません
- 正規表現での指定が可能です

### voice_map.csv

CSVファイルを使って、ユーザー毎に読み上げ音声を変える事もできます。

例. `電脳娘フユカ`というユーザーはCOEIROINKのリリンちゃんの声で読み上げたい

```
電脳娘フユカ,90181
```

※ 各種設定を変更した場合、アプリを再起動してください。
