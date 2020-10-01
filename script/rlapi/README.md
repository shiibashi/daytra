# サーバ側の設定

- ファイアウォールの設定


# サーバの立ち上げスクリプト
```
python run.py
```

or


```
uvicorn rl_api:app --reload
```

# クライアント側の設定

環境変数に以下を追加<br>

- RLAPI_HOST・・・RLAPIのホスト(デフォルトは"127.0.0.1")
- RLAPI_PORT・・・RLAPIのポート(デフォルトは"8000")

# クライアント側の接続テスト

```
python api_test.py
```
でテストできる
