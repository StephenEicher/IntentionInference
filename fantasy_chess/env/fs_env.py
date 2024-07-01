import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import random
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
        team2 =  [(6,6, u.meleeUnit)]
        self.nUnits = 4
        teamComp = [team1, team2]
        self.agentUnit = {
            "melee" : 1,
            "ranged" : 2,
        }
        self.teamComp = teamComp
        
        

    def reset(self, seed=None, options=False):
        self.agents = copy(self.possible_agents)
        yValues =  random.sample(range(0, 7), 3)
        team1 = [(random.randint(0, 5), yValues[0], u.meleeUnit), (random.randint(0, 5), yValues[1], u.rangedUnit)]
        team2 =  [(random.randint(2, 6), yValues[2], u.meleeUnit)]
        teamComp = [team1, team2]
        self.teamComp = teamComp
        self.game = self.gmClass(ac.DummyAgent, self.opp, self.teamComp, inclPygame=options, verbose=False)
        #Lets move this to the game manager

        observations = self.genObservations(self.game)
        gameActions, actionMask = self.genActions(self.game)
        # infos = {a: {'agent_mask' : actionMask[a]} for a in self.agents}
        infos = actionMask

        return observations, infos
    
    def step(self, actions):
        terminations = {a: False for a in self.agents}
        rewards = {a: 0 for a in self.agents}
        agentGameActions = {}
        deltaHP = {}

        for agent in self.agents:
            unit = self.game.allUnits.get(self.agentUnit[agent], None)
            if unit is not None:
                deltaHP[agent] = unit.currentHP

        for agent in actions.keys():
            if self.game.gameOver:
                break
            unit = self.game.allUnits.get(self.agentUnit[agent], None)
            if unit is not None:
                actionID = actions[agent]
                gameActions, actionMask = self.genActions(self.game)
                curMask = actionMask[agent]
                gameActionID =  np.sum(curMask[:actionID]).astype(int)
                curActions = gameActions[agent]
                gameAction = curActions[gameActionID]
                agentGameActions[agent] = gameAction
                self.game.executeMove(gameAction)


        while not isinstance(self.game.currentAgent, ac.DummyAgent) and not self.game.gameOver:
            allAgentActions = self.game.getCurrentStateActions(self.game)
            action = self.game.currentAgent.selectAction(self.game, allAgentActions, 'gameLoop')
            self.game.executeMove(action)

        if self.game.gameOver:
            terminations = {a: True for a in self.agents}
            if self.game.winner == 0:
                rewards = {a: 100 for a in self.agents}
            else:
                rewards = {a: -100 for a in self.agents}
        else:
            for agent in self.agents:
                unit = self.game.allUnits.get(self.agentUnit[agent], None)
                gameAction = agentGameActions.get(agent, None)
                if unit is None:
                    terminations[agent] = True
                    rewards[agent] = -25    
                else:
                    _, actionType, actionInfo = gameAction
                    if actionType == "ability" and actionInfo[0] != -1:
                        rewards[agent] = 5
                    else:
                        rewards[agent] = -0.25
                    deltaHP[agent] = deltaHP[agent] - unit.currentHP
                    if deltaHP[agent] != 0:
                        rewards[agent] = rewards[agent] - 10
        

        truncations = {a: False for a in self.agents}
        if self.game.nTurns > 50:
            truncations = {a: True for a in self.agents}
        
        gameActions, actionMask = self.genActions(self.game)
        observations = self.genObservations(self.game)
        # infos = {a: {} for a in self.agents}
        infos = actionMask
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
                unitPos.append(np.array([np.max(game.board.linear_map)+1]))
                unitHP.append(np.array(0))
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
                actionMask[agent] = np.zeros(11)
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