
# 本番データ展開コマンドメモ
tar -zcvf prod_data.tar.gz prod_data/
tar -zxvf prod_data.tar.gz

```
cd script
python train.py --mode dev
```


```
cd script
python train.py --mode prod
```
