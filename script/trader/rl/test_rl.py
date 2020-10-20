import pandas
import numpy
import random
import json
import datetime
import argparse
import itertools
import os
from pathlib import Path

from . import action_class
from . import feature_converter
from . import _util
from . import train_rl

ROOT = Path(__file__).parent

def get_model_dir_list():
    dirname = ROOT / "../../../output/rl"
    dirlist = os.listdir(dirname)
    return dirlist

def _get_best_score_model_path():
    dirname = ROOT / "../../../output/rl"
    dirlist = get_model_dir_list()

    a = []
    for dirpath in dirlist:
        try:
            j = _util.read_json(dirname / dirpath / "best_score.json" )
            a.append((dirpath, j["best_score"]))
        except Exception:
            continue
    if len(a) == 1:
        sorted_a = a
    else:
        sorted_a = sorted(a, key=lambda x: x[0])[-1] # 実行日が最新のものを取得
    print(sorted_a)
    best = sorted_a[0]
    model_path = best[0]
    return model_path


def get_agent():
    ymdhms = _get_best_score_model_path()
    #ymdhms = "rl_2020-09-24-22-20-18"
    model_path = ROOT / "../../../output/rl/{}".format(ymdhms)
    params_path = model_path / "params.json"
    params = _util.read_json(params_path)
    print("best_params {}".format(params))
    agent = train_rl._get_agent(params, params["backend"])
    #agent = train_rl._get_agent(params, "nn")
    agent.load_model(model_path / "best_model.h5")
    return agent

def get_all_params_list():
    dirlist = get_model_dir_list()
    params_list = []
    for ymdhms in dirlist:
        model_path = ROOT / "../../../output/rl/{}".format(ymdhms)
        params_path = model_path / "params.json"
        params = _util.read_json(params_path)
        params_list.append(params)
    return params_list
