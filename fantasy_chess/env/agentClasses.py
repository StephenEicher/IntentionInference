import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import abc
import time
import random
import numpy as np
from fantasy_chess.env import unitClasses as u

# from mcts.searcher.mcts import MCTS

class Agent(metaclass=abc.ABCMeta):
    agentIndex = None
    team = None

    def __init__(self, name):       
        self.name = name

    @abc.abstractmethod
    def selectAction(self):
        pass
    def init(self, agentIndex, team):
        self.team = team
        self.agentIndex = agentIndex


class RandomAgent(Agent):
    #Selects move at random
    def selectAction(self, game, actionSpace, debugStr=None):
        return random.choice(actionSpace)

class DummyAgent(Agent):
    def selectAction(self, game, actionSpace, debugStr=None):
        return None
    
class StaticAgent(Agent):
    #Always selects end turn
    def selectAction(self, game, actionSpace, debugStr=None):
        for action in actionSpace:
            selectedUnitID, actionType, info = action
            if actionType == "ability":
                abilityClass, targetID = info
                if abilityClass == -1:
                    choice = action
                    break
        return choice

class RLAgent(Agent):
    agent = None
    agentUnitDict = None
    possibleAgents = None
    def __init__(self, name, agent, possibleAgents):
        self.name = name
        self.agent = agent
        self.possibleAgents = possibleAgents

        
    def init(self, agentIndex, team):
        self.team = team
        self.agentIndex = agentIndex
        self.agentUnitDict = {}
        for agent in self.possibleAgents:
            self.agentUnitDict[agent] = -1
            for unit in self.team:
                if agent == "melee" and isinstance(unit, u.meleeUnit):
                    self.agentUnitDict[agent] = unit.ID
                    break
                elif agent == "ranged" and isinstance(unit, u.rangedUnit):
                    self.agentUnitDict[agent] = unit.ID
                    break


    def selectAction(self, game, actionSpace, debugStr=None):  
        state = game.genObservationsDict(self.agentUnitDict)
        gameActions, action_mask = game.genActionsDict(self.agentUnitDict)
        cont_actions, discrete_actions = self.agent.get_action(
            state,
            training=False,
            agent_mask = None,
            env_defined_actions=None,
            action_mask = action_mask
        ) 
        actions = discrete_actions
        for key in actions.keys():
            if actions[key] is not None:
                actions[key] = actions[key][0]
        for agent in actions.keys():
            if game.gameOver:
                return None
            unit = game.allUnits.get(self.agentUnitDict[agent], None)
            actionID = actions[agent]
            if unit is not None and actionID != 11:
                curMask = action_mask[agent]
                gameActionID =  np.sum(curMask[:actionID]).astype(int)
                curActions = gameActions[agent]
                gameAction = curActions[gameActionID]
                return gameAction


class HumanAgent(Agent):
    selectedUnit = None
    def selectUnit(self, game, waitingUnits):
        game.pygameUI.drawButtons({}, None)
        
        game.pygameUI.getInput = True
        time.sleep(0.1)
        unitTuple = game.pgQueue.get()
        if unitTuple is not None:
            unitID, _, selectedUnit = unitTuple
            self.selectedUnit = selectedUnit
            return selectedUnit
        else:
            return None
    
    def selectAction(self, game, actionSpace, debugStr=None):
        action = self.selectActionRecursive(game, actionSpace)
        return action

    def selectActionRecursive(self, game, actionSpace):
        waitingUnitIDs = set()
        sortedAbilities = {}
        sortedMoves = {}
        for entry in actionSpace:
            ID, actionType, info = entry
            waitingUnitIDs.add(ID)
            if sortedAbilities.get(ID, None) is None:
                sortedAbilities[ID] = set()
            if sortedMoves.get(ID, None) is None:
                sortedMoves[ID] = []

            if actionType == 'ability':
                sortedAbilities[ID].add(info[0])
            else:
                sortedMoves[ID].append(info)
        waitingUnits = [game.allUnits[ID] for ID in waitingUnitIDs]

        game.pygameUI.drawSelectUnit(waitingUnits)

        if self.selectedUnit is None:
            unit = self.selectUnit(game, waitingUnits)
        else:
            if self.selectedUnit.ID not in sortedAbilities.keys() and self.selectedUnit.ID not in sortedMoves.keys():
                unit = self.selectUnit(game, waitingUnits)
                self.selectedUnit = unit
            else:
                unit = self.selectedUnit
        if unit is None:
            return None
        validAbilities = sortedAbilities[unit.ID]
        validMoveDirections = np.array(sortedMoves[unit.ID])
        if unit.canMove is False and unit.canAct is False:
            print(f"Warning! This should never happen, unit {unit.ID} that cannot act and cannot move in waitingUnits List")
            unit.Avail = False
            return None
        if unit.canMove or unit.canAct:
            game.pygameUI.getInput = True
        
        
        game.pygameUI.validDirections = validMoveDirections
        
        game.pygameUI.drawButtons(validAbilities, unit)
        action = game.pgQueue.get()
        
        if action is not None:
            _, actionType, info = action
            if actionType == "unit":
                self.selectedUnit = info
                game.pygameUI.getTarget = False
                action = self.selectActionRecursive(game, actionSpace)


            game.pygameUI.getInput = False
            game.pygameUI.getTarget = False
            return action
        else:
            return None
        

