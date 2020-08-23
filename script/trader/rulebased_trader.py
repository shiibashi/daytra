import pandas
from .base_line import BaselineTrader
import numpy
import datetime

def second_delta(hms_1, hms_2):
    # hms_1 - hms_2秒
    dt1 = datetime.datetime.strptime(hms_1, "%H-%M-%S")
    dt2 = datetime.datetime.strptime(hms_2, "%H-%M-%S")
    s = (dt1 - dt2).seconds
    return s

class RulebasedTrader(BaselineTrader):
    def __init__(self):
        self.name = "rulebased"

    def append_feature(self, df):
        df = df.copy()
        df["upper_price_ma_5"] = df["upper_price"].rolling(5).mean()
        df["upper_price_ma_25"] = df["upper_price"].rolling(25).mean()
        df["upper_price_ma_75"] = df["upper_price"].rolling(75).mean()
        df["upper_price_ma_5_diff_2"] = df["upper_price_ma_5"].diff(2)
        df["upper_price_ma_25_diff_5"] = df["upper_price_ma_25"].diff(5)
        df["upper_price_ma_75_diff_5"] = df["upper_price_ma_75"].diff(5)

        df = df.dropna().reset_index(drop=True)
        return df
        
    def trade(self, df):
        df = self.append_feature(df)
        trade_data_list = []
        for ymd in sorted(set(df["ymd"])):
            day_df = df[df["ymd"] == ymd].reset_index(drop=True)
            data_list = self._trade(day_df)
            trade_data_list += data_list
        return trade_data_list
        
    def _trade(self, df):        
        before_5m_hms = 0
        status = "sell"
        trade_data_list = []
        for i, row in df.iterrows():
            if i >= 5:
                before_5m_hms = df["hms"][i-5]
            upper_price = row["upper_price"]
            hms = row["hms"]
            ymd = row["ymd"]
            upper_price_ma_5_diff_2 = row['upper_price_ma_5_diff_2']
            upper_price_ma_25_diff_5 = row['upper_price_ma_25_diff_5']
            upper_price_ma_75_diff_5 = row['upper_price_ma_75_diff_5']
            if hms <= "10-00-00":
                continue

            if status == "sell" and self.buy_flag(i, row) and hms <= "14-50-00" and self.last_5m_trend(df, i):
                if len(trade_data_list) > 0  and second_delta(hms, trade_data_list[-1][1]) <= 244:
                    # 直前にエントリーアウトしてたら再エントリーしない
                    continue
                status = "buy"
                trade_data_list.append([ymd, hms, upper_price, "buy"])
                continue
            elif status == "buy" and (self.sell_flag(i, row) or hms >= "14-58-00"):
                status = "sell"
                trade_data_list.append([ymd, hms, upper_price, "sell"])
        return trade_data_list
    
    def buy_flag(self, i, row):
        upper_price_ma_5 = row["upper_price_ma_5"]
        upper_price_ma_25 = row["upper_price_ma_25"]
        upper_price_ma_75 = row["upper_price_ma_75"]
        upper_price_ma_5_diff_2 = row['upper_price_ma_5_diff_2']
        upper_price_ma_25_diff_5 = row['upper_price_ma_25_diff_5']
        upper_price_ma_75_diff_5 = row['upper_price_ma_75_diff_5']
        a = upper_price_ma_5 >= upper_price_ma_25
        b = upper_price_ma_5 >= upper_price_ma_75
        c = upper_price_ma_5_diff_2 >= 0
        d = upper_price_ma_75_diff_5 >= 0
        f = upper_price_ma_25_diff_5 >= 0
        e = upper_price_ma_5_diff_2 >= upper_price_ma_25_diff_5 >= upper_price_ma_75_diff_5
        return a and b and c and d and e and f

    def sell_flag(self, i, row):
        upper_price_ma_5 = row["upper_price_ma_5"]
        upper_price_ma_25 = row["upper_price_ma_25"]
        upper_price_ma_75 = row["upper_price_ma_75"]
        upper_price_ma_5_diff_2 = row['upper_price_ma_5_diff_2']
        upper_price_ma_25_diff_5 = row['upper_price_ma_25_diff_5']
        upper_price_ma_75_diff_5 = row['upper_price_ma_75_diff_5']
        a = upper_price_ma_5 <= upper_price_ma_25
        return a

    def last_5m_trend(self, df, index):
        # 直近5分で25MAを5MAが下から上に抜いたかどうか
        if index <= 5:
            return False
        flag1 = False
        flag2 = False
        for i, row in df.reset_index(drop=True)[index-5:index].iterrows():
            hms = row["hms"]
            upper_price = row["upper_price"]
            upper_price_ma_5 = row["upper_price_ma_5"]
            upper_price_ma_25 = row["upper_price_ma_25"]
            upper_price_ma_75 = row["upper_price_ma_75"]
            if upper_price_ma_5 <= upper_price_ma_25:
                flag1 = True
            if flag1 and upper_price_ma_5 >= upper_price_ma_25:
                flag2 = True
        return flag2
