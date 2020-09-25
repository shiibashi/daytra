from . import _util
import pandas

import gc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

class TrainLogger(object):
    def __init__(self, save_path, test_data=None):
        self.data = []
        self.save_path = save_path
        self.test_data = test_data
        self.best_score = None

    def append(self, json_data):
        if "msg" in json_data.keys():
            print(json_data["msg"], flush=True)
        if "best_score" in json_data.keys():
            self.best_score = json_data["best_score"]
        self.data.append(json_data)
        
    def train_end(self):
        def f(d):
            return "episode" in d.keys() and "score" in d.keys()
        # scoreのlog.csv
        episode_list = [d["episode"] for d in self.data if f(d)]
        score_list = [d["score"] for d in self.data if f(d)]
        df = pandas.DataFrame({"episode": episode_list, "score": score_list})
        df.to_csv(self.save_path / "log.csv", index=False)
        
        # messageのtxt
        msg_list = [d["msg"] for d in self.data if "msg" in d.keys()]        
        _util.write_file(msg_list, self.save_path / "log.txt")

        _util.write_json(self.save_path / "best_score.json", {"best_score": self.best_score})

        # scoreの推移グラフ
        self.save(df)

        if self.test_data is not None:
            action_series_list = [d["action_list"] for d in self.data if "action_list" in d.keys()]
            if len(action_series_list) > 0:
                best_action_series = action_series_list[-1]
                action_df = pandas.DataFrame(best_action_series, columns=["index", "action"])
                merged = pandas.concat([self.test_data, action_df], axis=1)
                merged.to_csv(self.save_path / "test_action_data.csv", index=False)
                self.save_trade_graph(merged)        

    def test_end(self):
        pass
        
    def save_trade_graph(self, df):
        df = df.dropna().reset_index(drop=True)
        
        trade_data_list = []
        before_action = None
        for i, row in df.iterrows():
            action = row["action"]
            if before_action is None:
                before_action = action
                row_list = [row]
                continue
            if before_action == action:
                row_list.append(row)
            else:
                tmp_df = pandas.DataFrame(row_list).reset_index(drop=True)
                trade_data_list.append(tmp_df)
                row_list = [row]
                before_action = action

        for trade_data in trade_data_list:
            action = trade_data["action"][0]
            if action == 0:
                plt.plot(trade_data["index"], trade_data["upper_price"], c="b")
            else:
                plt.plot(trade_data["index"], trade_data["upper_price"], c="r")
            plt.savefig(self.save_path / "trade_graph")
            plt.close("all")
            gc.collect()

    def save(self, df):
        plt.plot(df["episode"], df["score"])
        plt.savefig(self.save_path / "score_graph")
        plt.close("all")
        gc.collect()
