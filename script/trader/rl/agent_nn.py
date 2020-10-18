from . import action_class
from . import _util
from .custom_keras import noisy_dense
from .custom_keras import network


import math
import keras
import keras.models
import random
import numpy

class Agent_NN(object):
    def __init__(self, action_size, feature_size,
                 alpha=0.95,
                 fixed_target_network_update_steps=50,
                 dueling=False,
                 ddqn=False,
                 noisy_dense=False,
                 exploration_stop=20000):
        self.action_size = action_size
        self.feature_size = feature_size

        self.alpha = alpha
        self.fixed_target_network_update_steps = fixed_target_network_update_steps
        self.dueling = dueling
        self.ddqn = ddqn
        self.noisy_dense = noisy_dense

        self.evaluator = self.build_evaluator()
        self.evaluator_copy = self.build_evaluator()
        self.set_clone_evaluator()
 
        # epsilon-greedy選択のパラメータ
        self.epsilon = 1
        self.epsilon_ub = 1
        self.epsilon_lb = 0.1
        self.exploration_stop = exploration_stop
        self.epsilon_lambda = -math.log(0.01) / self.exploration_stop

    def save_model(self, path):
        self.evaluator.save(path)
       
    def load_model(self, path):
        model = keras.models.load_model(path, custom_objects={"NoisyDense": noisy_dense.NoisyDense})
        self.evaluator = model

    def save_agent(self, path):
        _util.write_pkl(self, path)
    
    def build_evaluator(self):
        model = network.nn(self.action_size,
            self.feature_size,
            self.dueling,
            self.noisy_dense)
        return model

    def set_clone_evaluator(self, custom_objects={}):
        self.evaluator_copy.set_weights(self.evaluator.get_weights())

    def get_action(self, state):
        if state[0] >= 0.97: # 14:50くらい
            return action_class.Action.STAY
        if state[0] <= 0.1: # 9:30くらい
            return action_class.Action.STAY
        if random.random() < self.epsilon:
            return random.choice(action_class.ACTION_LIST)
        else:
            return self.get_best_action(state)

    def get_best_action(self, state, with_q=False):
        if state[0] >= 0.95: # 14:45くらい
            if not with_q:
                return action_class.Action.STAY
            else:
                return action_class.Action.STAY, 0
        if state[0] <= 0.166: # 10:00くらい
            if not with_q:
                return action_class.Action.STAY
            else:
                return action_class.Action.STAY, 0
        estimates = self.predict_value(numpy.array([state]))
        if not with_q:
            action_id = numpy.argmax(estimates)
            best_action = action_class.ACTION_LIST[action_id]
            return best_action
        else:
            buy_id = action_class.ACTION_INDEX[action_class.Action.BUY]
            q = estimates[buy_id]
            action_id = numpy.argmax(estimates)
            best_action = action_class.ACTION_LIST[action_id]
            return best_action, q


    def predict_value(self, state):
        return self.evaluator.predict(state)[0]
 
    def predict_values(self, states):
        return self.evaluator.predict(states)

    def predict_values_with_clone(self, states):
        return self.evaluator_copy.predict(states)

    def train(self, batch, epoch=0):
        """
            batch (list): leafのリスト
                leaf= {
                    "x": x,
                    "y": y,
                    "time": t,
                    "error": error,
                    "history": history
                }
        """
        if epoch % self.fixed_target_network_update_steps == 0:
            self.set_clone_evaluator()

        self.epsilon = self.epsilon_lb + (self.epsilon_ub - self.epsilon_lb) * math.exp(-self.epsilon_lambda * epoch)
        x = numpy.array([leaf["x"] for leaf in batch])
        y = numpy.array([leaf["y"] for leaf in batch])
        weight = numpy.array([leaf["weight"] for leaf in batch])
        self.evaluator.fit(x, y, epochs=1, sample_weight=weight)

    def make_mini_batch(self, history, t, multi_step):
        x, y, error, weight = self._make_batch_point(history, t, multi_step)
        return x, y, error, weight

    def _make_batch_point(self, history, t, multi_step):
        """distributed rl出ない場合のバッチ作成
        history: list
            state = data[0]
            action = data[1]
            reward = data[2]
            next_state = data[3]
            done = data[4]
        """
        states = numpy.array([data[0] for data in history])
        actions = [data[1] for data in history]
        rewards = [data[2] for data in history]
        next_states = numpy.array([data[3] for data in history])
        dones = [data[4] for data in history]
        infos = [data[5] for data in history]

        estimates = self.predict_values(states)
        futures = self.predict_values_with_clone(next_states)
        
        x = states[t]
        state = states[t]
        action = actions[t]
        info = infos[t]
        weight = info["weight"]
        action_index = action_class.ACTION_INDEX[action]
        tmp = estimates[t][action_index]

        if t + multi_step < len(estimates):
            done = dones[t + multi_step]
            # k = 1, 2,...., multi_step
            r = [self.alpha ** (k - 1) * rewards[t + k - 1] for k in range(1, multi_step + 1)]
            reward = numpy.array(r).sum()
            if not done:
                if self.ddqn:
                    multi_steped_state = next_states[t + multi_step - 1]
                    best_action = self.get_best_action(multi_steped_state)
                    best_action_index = action_class.ACTION_INDEX[best_action]
                    reward += self.alpha * futures[t + multi_step - 1][best_action_index]
                else:
                    reward += self.alpha * numpy.max(futures[t + multi_step - 1])
        else:
            # k = 1, 2,...., len(futures) - t
            r = [self.alpha ** (k - 1) * rewards[t + k - 1] for k in range(1, len(futures) - t + 1)]
            reward = numpy.array(r).sum()

        estimates[t][action_index] = reward
        y = estimates[t]
        error = math.fabs(tmp - reward)
        return x, y, error, weight
