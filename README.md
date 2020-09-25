
# 本番データ展開コマンドメモ
tar -zcvf prod_data.tar.gz prod_data/
tar -zxvf prod_data.tar.gz


prod_dataのデータを読み込む場合
```
cd script
python train.py --mode prod
```



test_dataのデータを読み込む場合

```
cd script
python train.py --mode dev
```

test_dataはlog_processed_2020-08-04.csvをコピーして日付をずらしてダミーデータを生成したもの

