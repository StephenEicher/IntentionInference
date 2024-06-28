import gameClasses
import agentClasses as ac
from pettingzoo import ParallelEnv
import unitClasses as u
import numpy as np
from copy import copy
from gymnasium.spaces import Discrete, MultiDiscrete
import functools


class fantasy_chess(ParallelEnv):

    metadata = {
        "name" : "fantasy_chess"
    }


    def __init__(self, opponent_class=None):
        self.possible_agents = ["melee", "ranged"]
        self.gmClass = gameClasses.GameManager
        self.game = None
        if opponent_class is None:
            self.opp = ac.RandomAgent
        self.opp = None
        team1 = [(1, 1, u.meleeUnit), (1, 2, u.rangedUnit)]
        team2 =  [(6,6, u.meleeUnit),]
        self.nUnits = 3
        teamComp = [team1, team2]
        self.teamComp = teamComp
        self.units = None
        
        

    def reset(self, seed=None, options=None):
        self.agents = copy(self.possible_agents)
        self.game = self.gmClass(ac.DummyAgent, self.opp, self.teamComp, inclPyGame = False, seed=42)
        self.units = np.zeros(len(self.game.allUnits.keys()))
        observations = self.gen_observations(self.game)
        infos = {a: {} for a in self.agents}
        return observations, infos

    def gen_observations(self, game):
        unitPos = []
        unitHP = []
        def linearPosition(unitID):
            idx = game.board.units_map == unitID
            return game.board.linear_map[idx]
        
        for idx, unitAlive in enumerate(self.units):
            unitID = idx + 1
            if unitAlive == 1:
                unit = game.allUnits.get(id, None)
                if unit is None:
                    self.units[id] = 0
                    unitPos.append(np.max(game.board.linear_map)+1)
                    unitHP.append(0)
                else:
                    unitPos.append(linearPosition(unitID))
                    unitHP.append(unit.currentHP)
            else:
                unitPos.append(np.max(game.board.linear_map)+1)
                unitHP.append(0)               
        return np.concatenate(unitPos + unitHP)
    
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        nTiles = np.max(self.game.board.linear_map)
        return MultiDiscrete([nTiles+1, nTiles + 1, nTiles + 1, 3, 3, 3])
    def action_space(self, agent):
        if self.
        if 