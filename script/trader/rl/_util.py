import numpy
import json
import yaml
import pickle

def to_history_json(history):
    history_list = []
    for b in history:
        data = {
            "state": b[0],
            "action_id": b[1].index,
            "action_name": b[1].name,
            "reward": b[2],
            "next_state": b[3],
            "done": b[4]
        }
        history_list.append(data)
    return history_list


def read_yaml(filepath):
    with open(filepath, "r") as f:
        d = yaml.load(f, Loader=yaml.SafeLoader)
    return d


def read_file(filepath):
    with open(filepath, "r") as f:
        d = f.readlines()
    return d


def read_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        d = json.load(f)
    return d


def write_file(txt_list, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        for txt in txt_list:
            f.writelines(txt)


def write_json(filepath, json_data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, cls=MyEncoder)

def write_pkl(obj, filepath):
    with open(filepath, mode="wb") as f:
        pickle.dump(obj, f)

def read_pkl(filepath):
    with open(filepath, mode="rb") as f:
        obj = pickle.load(f)
    return obj

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)
