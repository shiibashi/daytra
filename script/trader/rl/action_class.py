from enum import Enum

class Action(Enum):
    STAY = 1
    BUY = 2
    N = 2

ACTION_LIST = [Action.STAY, Action.BUY]

ACTION_INDEX = {Action.STAY: 0, Action.BUY: 1}

