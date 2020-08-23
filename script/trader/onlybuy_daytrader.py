import pandas
from .base_line import BaselineTrader

class OnlyBuyDayTrader(BaselineTrader):
    def __init__(self):
        self.name = "onlybuyday"
        
    def trade(self, df):
        trade_data_list = []
        for ymd in sorted(set(df["ymd"])):
            day_df = df[df["ymd"] == ymd].reset_index(drop=True)
            data_list = self._trade(day_df)
            trade_data_list += data_list
        return trade_data_list
        
    def _trade(self, df):        
        status = ""
        buy_price = 0
        sell_price = 0
        trade_data_list = []
        for i, row in df.iterrows():
            upper_price = row["upper_price"]
            hms = row["hms"]
            ymd = row["ymd"]
            if self.buy(i, row):
                status = "buy"
                trade_data_list.append([ymd, hms, upper_price, "buy"])
            elif self.sell(i, row) or i == len(df) - 1:
                status = "sell"
                trade_data_list.append([ymd, hms, upper_price, "sell"])
        return trade_data_list
