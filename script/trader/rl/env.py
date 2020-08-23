import numpy
import pandas
import os

import feature_converter
import action_class

class Env(object):

    def __init__(self, df):
        self.dataset = df
        self.state = None
        self.itr = None
        self.time = None
        self.position = (Action.HOLD, 0)
        self.fee = 1
        self.gap = 5

        self.initialize()
    
    def step(self, action):
        reward = self.calc_reward(action)
        self.itr += 1
        next_state = feature_converter.convert(self.dataset, self.itr)
        done = self.done_flag()
        info = {}
        self.time = self.dataset["hms"][self.itr]
        self.ymd = self.dataset["ymd"][self.itr]
        return next_state, reward, done, info

    def reset(self):
        if self.itr >= len(self.dataset) - 1:
            self.initialize()
        self.time = self.dataset["hms"][self.itr]
        self.ymd = self.dataset["ymd"][self.itr]
        price = self.dataset["upper_price"][self.itr]
        self.position = (Action.HOLD, price)
        state = feature_converter.convert(self.dataset, self.itr)
        return state

    def initialize(self):
        self.itr = 0

    def calc_reward(self, action):
        price = self.dataset["upper_price"][self.itr]
        if self.position[0] == Action.BUY and action == Action.BUY:
            r = price - self.position[1]
        elif self.position[0] == Action.BUY and action == Action.HOLD:
            r = price - self.position[1] - self.fee - self.gap
        else:
            r = 0
        r = r / 100
        self.position = (action, price)
        return r

    def done_flag(self):
        time = self.dataset["hms"][self.itr]
        ymd = self.dataset["ymd"][self.itr]
        if self.ymd != ymd or self.itr >= len(self.dataset) - 1:
            return True
        else:
            return False
