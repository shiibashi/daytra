from trader.base_line import BaselineTrader
from trader.onlybuy_daytrader import OnlyBuyDayTrader
from trader.rulebased_trader import RulebasedTrader

def run(df):
    trader_list = [
        BaselineTrader(),
        OnlyBuyDayTrader(),
        RulebasedTrader()
    ]
    for trader in trader_list:
        trade_data_list = trader.trade(df)
        score = trader.score(trade_data_list)
        score_with_slippage = trader.score_with_slippage(trade_data_list)
        print(trader.name, score, score_with_slippage)
