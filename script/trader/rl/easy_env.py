import numpy
import pandas
import os

from . import feature_converter
from .action_class import Action

class Env(object):

    def __init__(self, df):
        self.dataset = df
        self.state = None
        self.itr = None
        self.time = None
        self.fee = 1
        self.gap = 5

        self.trade = None
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
        state = feature_converter.convert(self.dataset, self.itr)
        self.trade = False
        return state

    def initialize(self):
        self.itr = 0

    def calc_reward(self, action):
        price = self.dataset["upper_price_slope_5"][self.itr]
        
        if action == Action.BUY:
            r = price
        else:
            r = 0
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
