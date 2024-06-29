import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fantasy_chess.env import gameClasses
from fantasy_chess.env import agentClasses as ac
from pettingzoo import ParallelEnv
from fantasy_chess.env import unitClasses as u
import numpy as np
from copy import copy
from gymnasium.spaces import Discrete, MultiDiscrete
from agilerl.wrappers.pettingzoo_wrappers import PettingZooVectorizationParallelWrapper
import functools



class parallel_env(ParallelEnv):

    metadata = {
        "name" : "fantasy_chess"
    }

    def __init__(self, opponent_class=None):
        self.possible_agents = ["melee", "ranged"]
        self.gmClass = gameClasses.GameManager
        self.game = None
        if opponent_class is None:
            self.opp = ac.RandomAgent
        else:
            self.opp = None
        team1 = [(1, 1, u.meleeUnit), (1, 2, u.rangedUnit)]
        team2 =  [(6,6, u.meleeUnit),]
        self.nUnits = 3
        teamComp = [team1, team2]
        self.agentUnit = {
            "melee" : 1,
            "ranged" : 2,
        }
        self.teamComp = teamComp
        
        

    def reset(self, seed=None, options=None):
        self.agents = copy(self.possible_agents)
        self.game = self.gmClass(ac.DummyAgent, self.opp, self.teamComp, inclPygame=False, seed=42)
        #Lets move this to the game manager

        obs = self.genObservations(self.game)
        gameActions, actionMask = self.genActions(self.game)
        observations = {}
        for agent in self.agents:
            observations[agent] = {"observation" : obs[agent], "action_mask" : actionMask[agent]}
        infos = {a: {} for a in self.agents}
        return observations, infos
    
    def step(self, actions):
        terminations = {a: False for a in self.agents}
        rewards = {a: 0 for a in self.agents}

        for agent in actions.keys():
            if self.game.gameOver:
                break
            unit = self.game.allUnits.get(self.agentUnit[agent], None)
            if unit is not None:
                actionID = actions[agent]
                gameActions, actionMask = self.genActions(self.game)
                gameActionID = np.sum(actionMask[:actionID])
                gameAction = gameActions[gameActionID]
                self.game.executeMove(gameAction)
            else:
                terminations[agent] = True
                rewards[agent] = -5

        if self.game.gameOver:
            terminations = {a: True for a in self.agents}
            if self.game.winner == 0:
                rewards = {a: 10 for a in self.agents}
            else:
                rewards = {a: -10 for a in self.agents}
        else:
            rewards = {"melee" : -0.1, "ranged": -0.1}
        

        truncations = {a: False for a in self.agents}
        if self.game.nTurns > 50:
            truncations = {a: True for a in self.agents}
        
        gameActions, actionMask = self.genActions(self.game)
        obs = self.genObservations(self.game)
        observations = {}
        for agent in self.agents:
            observations[agent] = {"observation" : obs[agent], "action_mask" : actionMask[agent]}
        infos = {a: {} for a in self.agents}

        return observations, rewards, terminations, truncations, infos

    def genObservations(self, game):
        unitPos = []
        unitHP = []
        def linearPosition(unitID):
            idx = game.board.units_map == unitID
            return game.board.linear_map[idx]
        for unitID in game.initUnitIDs:
            unit = game.allUnits.get(unitID, None)
            if unit is None:
                #If unit has died
                self.units[id] = 0
                unitPos.append(np.max(game.board.linear_map)+1)
                unitHP.append(0)
            else:
                unitPos.append(linearPosition(unitID))
                unitHP.append(unit.currentHP)
        obs = {}
        unitPos = np.array(unitPos).flatten()
        unitHP = np.array(unitHP).flatten()
        for agent in self.agents:
            obs[agent] = np.concatenate((unitPos, unitHP))
        return obs
    
    def genActions(self, game):
        actionMask = {}
        gameActions = {}
        for agent in self.possible_agents:
            unit = game.allUnits.get(self.agentUnit[agent], None)
            if unit is None:
                actionMask[agent] = None
            else:
                unitActions, unitMask = game.getCurrentUnitActions(game, unit.ID)
                actionMask[agent] = unitMask
                gameActions[agent] = unitActions
        return gameActions, actionMask


    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        nTiles = np.max(self.game.board.linear_map)
        return MultiDiscrete([nTiles+1, nTiles + 1, nTiles + 1, 3, 3, 3])
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Discrete(11)
    

env = parallel_env()
env = PettingZooVectorizationParallelWrapper(env, n_envs=5)