import pandas

class BaselineTrader(object):
    """初回に買ってずっとホールドする
    """
    def __init__(self):
        self.name = "baseline"
        
    def trade(self, df):
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
    
    def buy(self, i, row):
        return i == 0
    
    def sell(self, i, row):
        return False


    def score(self, trade_data_list):
        buy_list, sell_list = self._score(trade_data_list)
        profit = 0
        for b, s in zip(buy_list, sell_list):
            p = s - b
            profit += p
        return profit

    def score_with_slippage(self, trade_data_list):
        buy_list, sell_list = self._score(trade_data_list)
        profit = 0
        for b, s in zip(buy_list, sell_list):
            p = s - b - 5
            profit += p
        return profit

    def _score(self, trade_data_list):
        buy_list = []
        sell_list = []
        position = ""
        for log in trade_data_list:
            ymd, hms, price, status = log
            if status == "buy":
                position = "buy"
                buy_list.append(price)
            elif status == "sell":
                position = "sell"
                sell_list.append(price)
        return buy_list, sell_list
