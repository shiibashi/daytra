import pandas
import numpy
from .base_line import BaselineTrader
from .rl import train_rl, test_rl, feature_converter, action_class

class RLTrader(BaselineTrader):
    def __init__(self):
        self.name = "rl"
        self.agent = None
        self.buy_tau = 0.000
        self.sell_tau = 0

    def train(self, df):
        train_rl.simulate_nn(df) # backendがニューラルネットワーク
        #train_rl.simulate_xgb(df) # backendがxgboost

    def set_agent(self):
        self.agent = test_rl.get_agent()

    def trade(self, df):
        self.set_agent()
        trade_data_list = []
        for ymd in sorted(set(df["ymd"])):
            day_df = df[df["ymd"] == ymd].reset_index(drop=True)
            data_list = self._trade(day_df)
            trade_data_list += data_list
        return trade_data_list
        
    def _trade(self, df):
        status = "sell"
        buy_price = 0
        sell_price = 0
        trade_data_list = []
        position = [0]
        buy_count = 0
        for i, row in df.iterrows():
            upper_price = row["upper_price"]
            hms = row["hms"]
            ymd = row["ymd"]
            state = feature_converter.convert(df, i)
            new_state = state + position
            #pred_arr = self.agent.predict_value(numpy.array([new_state]))
            #print(pred_arr)
            #action = self.agent.get_best_action(new_state, tau=None)
            #print(self.agent, new_state, i, hms, ymd)
            #action, q  = self.agent.get_best_action(new_state, with_q=True)
            action = self.agent.get_best_action(new_state, with_q=False)
            q = 0
            #action, q = self.predict(df, i, position)
            if (status == "sell" and action == action_class.Action.BUY and q >= self.buy_tau)\
            or (status == "buy" and q >= self.sell_tau)\
            or 1 <= buy_count <= 5:
                status = "buy"
                trade_data_list.append([ymd, hms, upper_price, "buy"])
                position = [1]
                buy_count += 1
                print(ymd,hms, q, upper_price)
            else:
                status = "sell"
                trade_data_list.append([ymd, hms, upper_price, "sell"])
                position = [0]
                buy_count = 0
        return trade_data_list

    def predict(self, df, i, position):
        state = feature_converter.convert(df, i)
        new_state = state + position
        action, q  = self.agent.get_best_action(new_state, with_q=True)
        q = 0
        return action, q

    def rename(self, action):
        if action == action_class.Action.BUY:
            return "buy"
        else:
            return "sell"
