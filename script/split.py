import pandas


def split_train_test(df):
    ymd = sorted(set(df["ymd"]))
    n = 0.8
    i = int(len(ymd) * n)
    train_df = df[df["ymd"] <= ymd[i]].reset_index(drop=True)
    test_df = df[df["ymd"] > ymd[i]].reset_index(drop=True)
    return train_df, test_df
