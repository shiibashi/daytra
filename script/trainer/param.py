WIN_LINE = 0.01
LOSE_LINE = -0.01
"""
FEATURE_COLUMNS = ['over_under_ma-30', 'over_under_rate-30',
       'over_under_ma-60', 'over_under_rate-60', 'over_under_ma-90',
       'over_under_rate-90']
"""
FEATURE_COLUMNS = ['over_under_rate-30']
TARGET_COLUMNS = ["profit_flag_positive", "profit_flag_negative"]
BACK_STEP = 10
LSTM_HIDDEN_NUM = 10
DROPOUT = 0.2
EPOCHS = 2000
TEST_RATE = 0.2


"""
FEATURE_COLUMNS = ['over_under_rate-30']
TARGET_COLUMNS = ["profit_flag_positive", "profit_flag_negative"]
BACK_STEP = 50
LSTM_HIDDEN_NUM = 50
DROPOUT = 0.2
"""
