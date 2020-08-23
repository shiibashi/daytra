import _util
import pandas

import gc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

class TrainLogger(object):
    def __init__(self, save_path):
        self.data = []
        self.save_path = save_path

    def append(self, json_data):
        if "msg" in json_data.keys():
            print(json_data["msg"], flush=True)
        self.data.append(json_data)
        
    def train_end(self):
        def f(d):
            return "episode" in d.keys() and "score" in d.keys()
        episode_list = [d["episode"] for d in self.data if f(d)]
        score_list = [d["score"] for d in self.data if f(d)]
        df = pandas.DataFrame({"episode": episode_list, "score": score_list})
        df.to_csv(self.save_path / "log.csv", index=False)
        
        msg_list = [d["msg"] for d in self.data if "msg" in d.keys()]
        
        _util.write_file(msg_list, self.save_path / "log.txt")

        self.save(df)
        
    def test_end(self):
        pass
        
    def save(self, df):
        plt.plot(df["episode"], df["score"])
        plt.savefig(self.save_path / "score_graph")
        plt.close("all")
        gc.collect()
