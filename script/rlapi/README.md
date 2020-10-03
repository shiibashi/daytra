# サーバ側の設定

- ファイアウォールの設定


# サーバの立ち上げスクリプト
```
python run_rlapi.py
```

# クライアント側の設定

環境変数に以下を追加<br>

- RLAPI_HOST・・・RLAPIのホスト(デフォルトは"127.0.0.1")
- RLAPI_PORT・・・RLAPIのポート(デフォルトは"8000")

windowsの場合<br>
http://ruby.kyoto-wu.ac.jp/info-com/Softwares/Win10set.html<br>
で設定できる

# クライアント側の接続テスト

```
python api_test.py
```
でテストできる
