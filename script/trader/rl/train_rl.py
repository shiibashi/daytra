import pandas
import numpy
import random
import json
import datetime
import argparse
import itertools
import os
from pathlib import Path


from . import _util
from .env import Env
from .agent_nn import Agent_NN
#from .agent_xgb import Agent_XGB
from .logger import TrainLogger
from . import action_class
from . import feature_converter
from .data_structure import prioritized_memory

ROOT = Path(__file__).parent

def split_train_test(df):
    ymd = sorted(set(df["ymd"]))
    n = 0.8
    i = int(len(ymd) * n)
    train_df = df[df["ymd"] < ymd[-5]].reset_index(drop=True)
    test_df = df[df["ymd"] >= ymd[-5]].reset_index(drop=True)
    return train_df, test_df

def simulate_nn(df):
    backend = "nn"
    alpha = [0.99]
    fixed_target_network_update_steps = [1000]
    memory_type = ["per"]
    memory_size = [108000]
    multi_step = [5]
    dueling = [True]
    ddqn = [True]
    noisy_dense = [False]
    episode = [30000]
    batch_size = [64]
    score_step_by = [2000]
    exploration_stop = [20000]

    count = 0
    for d in itertools.product(alpha, 
                               fixed_target_network_update_steps,
                               memory_type,
                               memory_size,
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
            "multi_step": d[4],
            "dueling": d[5],
            "ddqn": d[6],
            "noisy_dense": d[7],
            "episode": d[8],
            "batch_size": d[9],
            "score_step_by": d[10],
            "exploration_stop": d[11]
        }
        print("simulation params {}".format(params), flush=True)
        _main(df, params, backend)
        count += 1

def simulate_xgb(df):
    backend = "xgb"
    alpha = [0.99]
    fixed_target_network_update_steps = [1000, 100]
    memory_type = ["per"]
    memory_size = [108000]
    multi_step = [5, 10]
    episode = [100]
    batch_size = [64]
    score_step_by = [1000]
    exploration_stop = [80000]

    n_estimators = [1]
    max_depth = [4, 8]
    booster = ["gbtree", "gblinear"]
    eta = [0.1, 0.3, 0.5]
    colsample_bytree = [0.5, 1]
    ddqn = [True, False]

    count = 0
    for d in itertools.product(alpha,
                               fixed_target_network_update_steps,
                               memory_type,
                               memory_size,
                               multi_step,
                               episode,
                               batch_size,
                               score_step_by,
                               exploration_stop,
                               n_estimators,
                               max_depth,
                               booster,
                               eta,
                               colsample_bytree,
                               ddqn):
        print("simulation {} start".format(count), flush=True)
        params = {
            "alpha": d[0],
            "fixed_target_network_update_steps": d[1],
            "memory_type": d[2],
            "memory_size": d[3],
            "multi_step": d[4],
            "episode": d[5],
            "batch_size": d[6],
            "score_step_by": d[7],
            "exploration_stop": d[8],
            "n_estimators": d[9],
            "max_depth": d[10],
            "booster": d[11],
            "eta": d[12],
            "colsample_bytree": d[13],
            "ddqn": d[14]
        }
        print("simulation params {}".format(params), flush=True)
        _main(df, params, backend)
        count += 1

def _get_agent(params, backend):
    assert backend in ["nn", "xgb"]
    if backend == "nn":
        alpha = params["alpha"]
        fixed_target_network_update_steps = params["fixed_target_network_update_steps"]
        dueling = params["dueling"]
        ddqn = params["ddqn"]
        noisy_dense = params["noisy_dense"]
        exploration_stop = params["exploration_stop"]

        agent = Agent_NN(len(action_class.ACTION_LIST), len(feature_converter.STATE_COLUMNS),
                 alpha=alpha,
                 fixed_target_network_update_steps=fixed_target_network_update_steps,
                 dueling=dueling,
                 ddqn=ddqn,
                 noisy_dense=noisy_dense,
                 exploration_stop=exploration_stop)
    else:
        alpha = params["alpha"]
        fixed_target_network_update_steps = params["fixed_target_network_update_steps"]
        exploration_stop = params["exploration_stop"]
        n_estimators = params["n_estimators"]
        max_depth = params["max_depth"]
        booster = params["booster"]
        eta = params["eta"]
        colsample_bytree = params["colsample_bytree"]
        ddqn = params["ddqn"]        

        agent = Agent_XGB(len(action_class.ACTION_LIST), len(feature_converter.STATE_COLUMNS),
            alpha=alpha,
            fixed_target_network_update_steps=fixed_target_network_update_steps,
            exploration_stop=exploration_stop,
            n_estimators=n_estimators,
            max_depth=max_depth,
            booster=booster,
            eta=eta,
            colsample_bytree=colsample_bytree,
            ddqn=ddqn
        )
    return agent

def _main(df, params, backend):
    assert backend in ["nn", "xgb"]
    agent = _get_agent(params, backend)

    params["backend"] = backend
    memory_type = params["memory_type"] # prioritized_memory 
    multi_step = params["multi_step"]
    episode = params["episode"]
    batch_size = params["batch_size"]
    memory_size = params["memory_size"]
    score_step_by = params["score_step_by"]

    df_train, df_test = split_train_test(df)
    ymdhms = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    save_path = ROOT / "../../../output/rl/rl_{}".format(ymdhms)
    #os.system("rm -rf {}".format(ROOT / "../../../output/rl"))
    os.makedirs(save_path, exist_ok=True)
    _util.write_json(save_path / "params.json", params)
    logger = TrainLogger(save_path, test_data=df_test)

    memory = prioritized_memory.PrioritizedMemory(capacity=memory_size)

    env = Env(df_train)
    env_test = Env(df_test)
    best_score = -999999
    for e in range(episode):
        state = env.reset()
        done = False
        history = []
        while not done:
            action = agent.get_action(state)
            next_state, reward, done, info = env.step(action)
            reward = reward * 2 if reward < 0 else reward
            one_batch = (state, action, reward, next_state, done, info)
            state = next_state
            history.append(one_batch)

        for t in range(len(history)):
            x, y, error, weight = agent.make_mini_batch(history, t, multi_step)
            leaf = {
                "x": x,
                "y": y,
                "time": t,
                "error": error,
                "history": history,
                "weight": weight
            }
            memory.add(leaf)
        
        if memory.trainable(batch_size):
            # キューにデータがたまったら学習
            #(idx, p, data)
            batch_list = memory.sample(batch_size, sampling_algorithm="uniform")
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
            score_list, action_list = calc_score(agent, env_test)
            score_sum = numpy.array(score_list).sum()
            score_max = numpy.array(score_list).max()
            score_min = numpy.array(score_list).min()
            mes = "episode:{}, score:{}, max_reward: {}, min_reward: {}".format(
                  e, score_sum, score_max, score_min)
            logging_data = {
                "episode": e,
                "score": score_sum,
                "msg": mes,
                "score_max": score_max
            }
            logger.append(logging_data)
            if best_score < score_sum:
                best_score = score_sum
                mes = "best_model updated, episode:{}, score:{}\n".format(e, score_sum)
                logger.append({"msg": mes, "aiction_list": action_list, "best_score": score_sum})
                agent.save_model(save_path / "best_model.h5")
                #agent.save_agent(save_path / "agent.pkl")

    logger.train_end()

def calc_score(agent, env):
    env.initialize()
    reward_list = []
    action_list = []
    for e in range(len(env.dataset)-1):
        if env.itr >= len(env.dataset) - 1:
            break
        state = env.reset()
        done = False
        sum_reward = 0
        while not done:
            action = agent.get_best_action(state)
            action_list.append((env.itr, action_class.ACTION_INDEX[action]))
            next_state, reward, done, info = env.step(action)
            state = next_state
            sum_reward += reward
        reward_list.append(sum_reward)
    return reward_list, action_list

