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
| honorifics.default          | 通常使用する敬称で、これをユーザー名の末尾に追加します                               |
| honorifics.other            | その他の敬称。ユーザー名の末尾がこのリストに含まれている場合はそのまま読み上げます   |
| oneComme.pathUsersCsv       | わんコメのユーザーリストをCSV出力したパスを指定します。(ニックネームで使用)          |

※1 Google翻訳APIを無料で作る方法
https://qiita.com/satto_sann/items/be4177360a0bc3691fdf

※ 設定を変更した場合、アプリを再起動してください。

### voice.json

読み上げに関する設定

| キー                        | 概要                                                 |
| --------------------------- | ---------------------------------------------------- |
| defaultCid                  | キャラクターID <br> (0の場合、読み上げ無効化)        |
| effects.speed               | 速度                                                 |
| effects.volume              | 音量                                                 |
| playAsync                   | 再生を同期するか <br> false: PLAY2, true: PLAYASYNC2 |
| maps                        | マッピング情報                                       |

#### maps

特定の`cid`の読み上げ速度および音量を上書きします。
`cid`は正規表現(完全一致)で指定する事ができます。

例. VOICEVOXの速度を1.3に、AivisSpeechの音量を0.1にする

```json
"maps": [
  {
    "cid": "5....",
    "effects": {
      "speed": 1.3
    }
  },
  {
    "cid": "2.....",
    "effects": {
      "volume": 0.1
    }
  }
]
```

配列になっているため複数の設定が可能です。
マッチングは上から順に評価される事を留意してください。

※ この設定は変更後に再起動の必要がありません。

### exclude_words.txt

翻訳を除外するキーワード郡を設定する事ができます。

- 完全一致で指定します
- 大文字・小文字及び全角半角を区別しません
- 正規表現での指定が可能です

※ この設定は変更後に再起動の必要がありません。

### voice_map.csv

CSVファイルを使って、ユーザー毎に読み上げ音声を変える事もできます。

例. `電脳娘フユカ`というユーザーはCOEIROINKのリリンちゃんの声で読み上げたい

```
電脳娘フユカ,90181
```

※ この設定は変更後に再起動の必要がありません。

## 実行

実行するには以下のコマンドを実行します。
```
TwitchChatTransBot.exe
```

## トラブルシューティング

### WindowsによってPCが保護されました

得体のしれないアプリという事でOSによって保護されました。
このアプリを信用する場合は実行を許可してあげてください。
やっぱ無理！って場合は利用を諦めてください。

## 貢献する

このソフトに貢献したい場合は、Issue を開いてアイデアを議論するか、プルリクを送信してください。

ただし、このツールは私の配信のために作ったので、余計な機能は付けませんし、使わない機能は削除します。

## 作者

ナツキソ

- X(旧Twitter): [@natukin1978](https://x.com/natukin1978)
- Mastodon: [@natukin1978](https://mstdn.jp/@natukin1978)
- Threads: [@natukin1978](https://www.threads.net/@natukin1978)
- GitHub: [@natukin1978](https://github.com/natukin1978)
- Mail: natukin1978@hotmail.com

## ライセンス

Twitchのチャットの外国語を翻訳するBOT は [MIT License](https://opensource.org/licenses/MIT) の下でリリースされました。
