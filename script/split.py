import pandas


def split_train_test(df):
    ymd = sorted(set(df["ymd"]))[-70:]
    n = 0.8
    i = int(len(ymd) * n)
    train_df = df[df["ymd"] < ymd[-10]].reset_index(drop=True)
    test_df = df[df["ymd"] >= ymd[-10]].reset_index(drop=True)
    return train_df, test_df
