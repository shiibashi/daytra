import argparse
import converter.convert
import os
import pandas
import trade_report, split, load

def _arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", help="dev or prod", required=True)
    args = parser.parse_args()
    return args

def main(args):
    print(args.mode)
    #_init()
    #df = _load_data(args.mode)
    #converted_df = converter.convert.run(df)
    #os.makedirs("../output/converter", exist_ok=True)
    #converted_df.to_csv("../output/converter/data.csv", index=False)

    data = pandas.read_csv("../output/converter/data.csv")
    #train_data, test_data = split.split_train_test(data)
    #train_data = data
    #print(train_data)
    #print(set(test_data["ymd"]))
    #trade_report.train(train_data)
    _, test_data = split.split_train_test(data)
    print(set(test_data["ymd"]))
    trade_report.run(test_data) # 強化学習の学習で使ってるデータと被ってるから結果をみるとき注意

def _init():
    os.system("rm -rf ../output")
    os.makedirs("../output", exist_ok=True)
 
def _load_data(mode):
    if mode == "dev":
        dirpath = "../test_data"
    else:
        dirpath = "../prod_data"

    df = load.read_log_data(dirpath)
    return df

if __name__ == "__main__":
    args = _arg_parse()
    main(args)
    
