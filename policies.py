from __future__ import division

import math
import random
import time
import numpy as np
from mcts.base.base import BaseState


# def depth_limited_policy(state: BaseState, max_depth: int, discount: int) -> float:
#     depth = 0
#     total_reward = 0
#     while not state.is_terminal() and depth < max_depth:
#         try:
#             action = random.choice(state.get_possible_actions())
#         except IndexError:
#             raise Exception("Non-terminal state has no possible actions: " + str(state))
#         preVal = state.get_reward()
#         state = state.take_action(action)
#         postVal = state.get_reward()
#         delta = postVal - preVal
#         total_reward += (discount**depth) * delta
#         depth += 1
#     return total_reward


def random_policy(state: BaseState) -> float:
    while not state.is_terminal():
        try:
            action = random.choice(state.get_possible_actions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.take_action(action)
    return state.get_reward()


def depth_limited_policy(state: BaseState, max_depth: int) -> float:
    depth = 0
    total_reward = 0
    while not state.is_terminal() and depth < max_depth:
        try:
            action = random.choice(state.get_possible_actions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        preVal = state.get_reward()
        state = state.take_action(action)
        TR = state.get_action_reward(action)
        postVal = state.get_reward()
        delta = postVal - preVal
        total_reward += TR
        depth += 1
    # Handle terminal state reward
    if state.is_terminal() and depth == 0:
        total_reward += state.get_reward()
    return total_reward