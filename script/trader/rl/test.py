import pandas
import numpy
import random
import json
import datetime
import argparse
import itertools
import os
from pathlib import Path


from env import Env
from agent import Agent
import action_class
import feature_converter
from data_structure import prioritized_memory

ROOT = Path(__file__).parent

def split_train_test(df):
    ymd = sorted(set(df["ymd"]))
    n = 0.8
    i = int(len(ymd) * n)
    train_df = df[df["ymd"] <= ymd[i]].reset_index(drop=True)
    test_df = df[df["ymd"] > ymd[i]].reset_index(drop=True)
    return train_df, test_df

def simulate():
    alpha = [0.95]
    fixed_target_network_update_steps = [100]
    memory_type = ["per"]
    memory_size = [4096]
    sampling_algorithm = ["uniform"]
    multi_step = [3]
    dueling = [True]
    ddqn = [True]
    noisy_dense = [False]
    episode = [200]
    batch_size = [32]
    score_step_by = [100]
    exploration_stop = [200]

    count = 0
    for d in itertools.product(alpha, 
                               fixed_target_network_update_steps,
                               memory_type,
                               memory_size,
                               sampling_algorithm,
                               multi_step,
                               dueling,
                               ddqn,
                               noisy_dense,
                               episode,
                               batch_size,
                               score_step_by,
                               exploration_stop):
        print("simulation {} start".format(count), flush=True)
        params = {
            "alpha": d[0],
            "fixed_target_network_update_steps": d[1],
            "memory_type": d[2],
            "memory_size": d[3],
            "sampling_algorithm": d[4],
            "multi_step": d[5],
            "dueling": d[6],
            "ddqn": d[7],
            "noisy_dense": d[8],
            "episode": d[9],
            "batch_size": d[10],
            "score_step_by": d[11],
            "exploration_stop": d[12]
        }
        print("simulation params {}".format(params), flush=True)
        _main(params)
        count += 1


def main():
    params = {
        "alpha": 0.95,
        "fixed_target_network_update_steps": 100,
        "memory_type": "per",
        "memory_size": 2048,
        "sampling_algorithm": "uniform",
        "multi_step": 3,
        "dueling": True,
        "ddqn": True,
        "noisy_dense": False,
        "episode": 30000,
        "batch_size": 32,
        "score_step_by": 100,
        "exploration_stop": 20000
    }
    _main(params)

def _main(params):
    # hyper parameter
    alpha = params["alpha"]
    fixed_target_network_update_steps = params["fixed_target_network_update_steps"]
    memory_type = params["memory_type"] # prioritized_memory 
    #memory_type = "que" # Que
    multi_step = params["multi_step"]
    sampling_algorithm = params["sampling_algorithm"]
    dueling = params["dueling"]
    ddqn = params["ddqn"]
    noisy_dense = params["noisy_dense"]
    episode = params["episode"]
    batch_size = params["batch_size"]
    memory_size = params["memory_size"]
    score_step_by = params["score_step_by"]
    exploration_stop = params["exploration_stop"]

    agent = Agent(len(action_class.ACTION_LIST), len(feature_converter.STATE_COLUMNS),
                 alpha=alpha,
                 fixed_target_network_update_steps=fixed_target_network_update_steps,
                 dueling=dueling,
                 ddqn=ddqn,
                 noisy_dense=noisy_dense,
                 exploration_stop=exploration_stop)

    df = pandas.read_csv(ROOT / "../../../output/converter/data.csv")
    
    assert False
    episode = 1
    env = Env(df)
    for e in range(episode):
        state = env.reset()
        done = False
        history = []
        while not done:
            action = agent.get_action(state)
            next_state, reward, done, info = env.step(action)
            one_batch = (state, action, reward, next_state, done)
            state = next_state
            history.append(one_batch)

        for t in range(len(history)):
            x, y, error = agent.make_mini_batch(history, t, multi_step)
            leaf = {
                "x": x,
                "y": y,
                "time": t,
                "error": error,
                "history": history
            }
            memory.add(leaf)
        
        if memory.trainable(batch_size):
            # キューにデータがたまったら学習
            #(idx, p, data)
            batch_list = memory.sample(batch_size, sampling_algorithm=sampling_algorithm)
            batch = [d[2] for d in batch_list]
            agent.train(batch, epoch=e)

            # PERの重みをアップデートする処理が必要
            # memoryに保存するのはs,a,n_s,r,d,i？
            for b in batch_list:
                idx = b[0]
                p = b[1]
                leaf = b[2]
                _, _, new_error = agent.make_mini_batch(leaf["history"], leaf["time"], multi_step)                    
                memory.update(idx, new_error)

        
        if e % score_step_by == 0 and memory.trainable(batch_size):
            # テスト環境で評価
            score_list = calc_score(agent, env_test)
            score_mean = numpy.array(score_list).mean()
            mes = "episode:{}, score:{}".format(e, score_mean)
            logging_data = {"episode": e, "score": score_mean, "msg": mes}
            logger.append(logging_data)
            if best_score < score_mean:
                best_score = score_mean
                mes = "best_model updated, episode:{}, score:{}\n".format(e, score_mean)
                logger.append({"msg": mes})
                agent.save_model(save_path / "best_model.h5")
                agent.save_agent(save_path / "agent.pkl")

    logger.train_end()

if __name__ == "__main__":
    simulate()
