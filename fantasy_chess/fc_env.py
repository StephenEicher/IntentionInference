import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import random
from fantasy_chess.env import gameClasses
from fantasy_chess.env import agentClasses as ac
from pettingzoo import ParallelEnv
from gymnasium import spaces
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

    def __init__(self, reward, opponent_class):
        self.possible_agents = ["melee", "ranged"]
        self.gmClass = gameClasses.GameManager
        self.game = None
        self.opp = opponent_class
        self.rewardFn = reward
        team1 = [(1, 1, u.meleeUnit), (1, 2, u.rangedUnit)]
        team2 =  [(6,6, u.meleeUnit)]
        self.nUnits = 4
        teamComp = [team1, team2]
        self.agentUnitDict = {
            "melee" : 1,
            "ranged" : 2,
        }
        self.teamComp = teamComp
        
        

    def reset(self, seed=None, options=False):
        self.agents = copy(self.possible_agents)
        grid_size = 8
        # Generate all possible coordinates in the grid
        all_coordinates = [(x, y) for x in range(grid_size) for y in range(grid_size)]
        all_coordinates.remove((4, 4))
        # Randomly sample three unique coordinates
        coords = random.sample(all_coordinates, 3)

        team1 = [(0, 0, u.meleeUnit), (7, 7, u.rangedUnit)]
        # team1 = [(coords[0][0], coords[0][1], u.meleeUnit)]
        team2 =  [(4, 4, u.meleeUnit)]

        teamComp = [team1, team2]
        self.teamComp = teamComp
        self.game = self.gmClass(ac.DummyAgent('Learning Agent'), self.opp, self.teamComp, inclPygame=options, verbose=False, seed=random.randint(0, 999999), noObstacles=True)
        #Lets move this to the game manager

        observations = observations = self.game.genObservationsDict(self.agentUnitDict)
        gameActions, actionMask = self.game.genActionsDict(self.agentUnitDict)
        # infos = {a: {} for a in self.agents}
        # for a in self.agents:
        #     infos[a]['action_mask'] = actionMask[a]
        #     infos[a]['agent_mask'] = np.invert(actionMask[a].astype(bool).all())
        infos = actionMask
        return observations, infos
    
    def step(self, actions):
        terminations = {a: False for a in self.agents}
        agentGameActions = {}
        preUnits = {}
        postUnits = {}
        for key in self.game.allUnits:
            preUnits[key] = self.game.allUnits[key].clone()

        for agent in actions.keys():
            if self.game.gameOver:
                break
            unit = self.game.allUnits.get(self.agentUnitDict[agent], None)
            actionID = actions[agent]
            if unit is not None and actionID != 11:
                gameActions, actionMask = self.game.genActionsDict(self.agentUnitDict)
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
        
        for key in self.game.allUnits:
            postUnits[key] = self.game.allUnits[key].clone()

        if self.game.gameOver:
            terminations = {a: True for a in self.agents}
        else:
            for agent in self.agents:
                unit = self.game.allUnits.get(self.agentUnitDict[agent], None)
                gameAction = agentGameActions.get(agent, None)
                if unit is None:
                    terminations[agent] = True
        rewards = self.rewardFn(self, self.game, agentGameActions,preUnits, postUnits)
        truncations = {a: False for a in self.agents}
        if self.game.nTurns > 5:
            truncations = {a: True for a in self.agents}
        
        gameActions, actionMask = self.game.genActionsDict(self.agentUnitDict)
        observations = self.game.genObservationsDict(self.agentUnitDict)
        # infos = {a: {} for a in self.agents}

        # for a in self.agents:
        #     infos[a]['action_mask'] = actionMask[a]
        #     infos[a]['agent_mask'] = np.invert(actionMask[a].astype(bool).all())
        infos = actionMask

        return observations, rewards, terminations, truncations, infos


    



    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        obs_space = spaces.Box(
                        low=0, high=1, shape=(4, 8, 8), dtype=np.int8
                    )

        # obs_space = spaces.Box(
        #                 low=0, high=1, shape=(6, 7, 2), dtype=np.int8
        #             )

        return obs_space
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Discrete(12)
    