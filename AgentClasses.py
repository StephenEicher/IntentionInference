import abc
import time
import random
import numpy as np

# from mcts.searcher.mcts import MCTS
class Agent(metaclass=abc.ABCMeta):
    def __init__(self, name, agentIndex, team, game = None, pygame = None):       
        self.name = name
        self.agentIndex = agentIndex
        self.team = team

        self.game = game
        self.pygameUI = pygame
        self.inputReady = False
    @abc.abstractmethod
    def selectAction(self):
        pass

class HumanAgent(Agent):
    selectedUnit = None
    def selectUnit(self, waitingUnits):
        self.pygameUI.drawButtons({}, None)
        
        self.pygameUI.getInput = True
        time.sleep(0.1)
        unitTuple = self.game.pgQueue.get()
        if unitTuple is not None:
            unitID, _, selectedUnit = unitTuple
            self.selectedUnit = selectedUnit
            return selectedUnit
        else:
            return self.selectUnit(waitingUnits)
    
    def selectAction(self, game, actionSpace, debugStr=None):
        action = self.selectActionRecursive(game, actionSpace)
        return action

    def selectActionRecursive(self, game, actionSpace):
        waitingUnits = set()
        sortedAbilities = {}
        sortedMoves = {}
        for entry in actionSpace:
            ID, actionType, info = entry
            waitingUnits.add(game.allUnits[ID])
            if sortedAbilities.get(ID, None) is None:
                sortedAbilities[ID] = set()
            if sortedMoves.get(ID, None) is None:
                sortedMoves[ID] = []

            if actionType == 'ability':
                sortedAbilities[ID].add(info[0])
            else:
                sortedMoves[ID].append(info)
        waitingUnits = list(waitingUnits)
        self.pygameUI.drawSelectUnit(waitingUnits)

        if self.selectedUnit is None:
            unit = self.selectUnit(waitingUnits)
        else:
            if self.selectedUnit.ID not in sortedAbilities.keys() and self.selectedUnit.ID not in sortedMoves.keys():
                unit = self.selectUnit(waitingUnits)
            unit = self.selectedUnit
        validAbilities = sortedAbilities[unit.ID]
        validMoveDirections = np.array(sortedMoves[unit.ID])
        if unit.canMove is False and unit.canAct is False:
            print(f"Warning! This should never happen, unit {unit.ID} that cannot act and cannot move in waitingUnits List")
            unit.Avail = False
            return None
        if unit.canMove or unit.canAct:
            self.pygameUI.getInput = True
        
        
        self.pygameUI.validDirections = validMoveDirections
        
        self.pygameUI.drawButtons(validAbilities, unit)
        action = self.game.pgQueue.get()
        
        if action is not None:
            _, actionType, info = action
            if actionType == "unit":
                self.selectedUnit = info
                self.pygameUI.getTarget = False
                action = self.selectActionRecursive(game, actionSpace)


            self.pygameUI.getInput = False
            self.pygameUI.getTarget = False
            return action
        else:
            return None
        

