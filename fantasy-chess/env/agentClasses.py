import abc
import time
import random
import numpy as np

# from mcts.searcher.mcts import MCTS

class Agent(metaclass=abc.ABCMeta):
    def __init__(self, name, agentIndex, team):       
        self.name = name
        self.agentIndex = agentIndex
        self.team = team
        self.inputReady = False
    @abc.abstractmethod
    def selectAction(self):
        pass


class RandomAgent(Agent):
    def selectAction(self, game, actionSpace, debugStr=None):
        return random.choice(actionSpace)

class DummyAgent(Agent):
    def selectAction(self, game, actionSpace, debugStr=None):
        return None

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
        

