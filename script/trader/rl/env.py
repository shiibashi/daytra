import numpy
import pandas
import os
import math

from . import feature_converter
from .action_class import Action

class Env(object):

    def __init__(self, df):
        self.dataset = df
        self.state = None
        self.itr = None
        self.time = None
        self.position = None
        self.fee = 0#1
        self.gap = 0#5
        self.time_decay_param = 10

        self.trade = None
        self.initialize()
    
    def time_decay(self, ymd_index):
        w = 0.1 + 0.9 * math.exp(-self.time_decay_param * ymd_index)
        #print(w, ymd_index)
        assert 0.1 <= w <= 1
        return w
        #return 1

    def step(self, action):
        reward = self.calc_reward(action)
        self.itr += 1
        next_state = self._state()
        done = self.done_flag()
        ymd_index = self.dataset["ymd_index"][self.itr]
        info = {"weight": self.time_decay(ymd_index)}
        self.time = self.dataset["hms"][self.itr]
        self.ymd = self.dataset["ymd"][self.itr]
        return next_state, reward, done, info

    def reset(self):
        if self.itr >= len(self.dataset) - 1:
            self.initialize()
        self.time = self.dataset["hms"][self.itr]
        self.ymd = self.dataset["ymd"][self.itr]
        price = self.dataset["upper_price"][self.itr]
        self.position = (Action.STAY, price)
        state = self._state()
        self.trade = False
        return state

    def _state(self):
        state = feature_converter.convert(self.dataset, self.itr)
        if self.position[0] == Action.STAY:
            position = [0]
        elif self.position[0] == Action.BUY:
            position = [1] 
        else:
            raise
        new_state = state + position
        return new_state

    def initialize(self):
        self.itr = 0

    def calc_reward(self, action):
        price = self.dataset["upper_price"][self.itr]
        if self.position[0] == Action.BUY and action == Action.BUY:
            r = price - self.position[1]
        elif self.position[0] == Action.BUY and action == Action.STAY:
            r = price - self.position[1] - self.fee - self.gap
            self.trade = True
        else:
            r = 0
        r = r / 100
        self.position = (action, price)
        return r

    def done_flag(self):
        if self.trade:
            return True
        time = self.dataset["hms"][self.itr]
        ymd = self.dataset["ymd"][self.itr]
        if self.ymd != ymd or self.itr >= len(self.dataset) - 1:
            return True
        else:
            return False
