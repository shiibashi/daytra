from trader.base_line import BaselineTrader
from trader.onlybuy_daytrader import OnlyBuyDayTrader
from trader.rulebased_trader import RulebasedTrader
from trader.rl_trader import RLTrader


def train(df):
    trader_list = [
        RLTrader()
    ]
    for trader in trader_list:
        trader.train(df)

def run(df):
    trader_list = [
        RLTrader(),
        BaselineTrader(),
        OnlyBuyDayTrader(),
        RulebasedTrader(),
    ]
    for trader in trader_list:
        trade_data_list = trader.trade(df)
        buy_list, sell_list = trader._score(trade_data_list)
        score = trader.score(trade_data_list)
        score_with_slippage = trader.score_with_slippage(trade_data_list)
        print("trade report, ", trader.name, score, score_with_slippage, len(buy_list))
