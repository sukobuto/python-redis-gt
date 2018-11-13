### スロットル制御しつつ処理を行う

- [x] テスト環境をつくる
- [x] Redis を受け取って操作するクラスを作る
- [x] fakeredis を使ってテストする
- [x] throttle に何かをさせるメソッドを追加する
- [x] await するまで実行されないことを確認する
- [x] throttle に並列上限を設定する
- [x] 並列上限を超えた場合は待機する
- [x] throttle に名前空間を与える
- [x] 待機 timeout を設ける
- [x] 処理 timeout を設ける
- [x] ゴミが残らないように TTL を設ける
- [x] asyncio を使わない Throttle を実装する
- [x] Throttle と AsyncThrottle のデコレータを実装するo

throttle をテストするアイデア
- 待たされた回数を記録する
- 待たされた時間を記録する ← これにした（他の方法がうまく実現できなかったため）
- 擬似的に完了を再現する
    - Future を渡しておいて set_result する
- 待機時間を設けてログを記録する

### pip install できるようにする

- [ ] CircleCI を導入する
- [ ] setup.py を記述する
- [ ] PyPI に登録する

参考: https://qiita.com/icoxfog417/items/edba14600323df6bf5e0
