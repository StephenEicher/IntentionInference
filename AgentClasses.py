import abc
import time
import random
import MCTS

class Agent(metaclass=abc.ABCMeta):
    def __init__(self, name, agentIndex, team, game = None, pygame = None):       
        self.name = name
        self.agentIndex = agentIndex
        self.team = team
        self.game = game
        self.aPygame = pygame
        self.inputReady = False
    @abc.abstractmethod
    def selectAction(self):
        pass

class RandomAgent(Agent):
    def selectAction(self, waitingUnits, board, allActions, flatActionSpace):
        time.sleep(0.5)
        if len(flatActionSpace) > 3:
            for unit, actionDict in flatActionSpace:
                if actionDict["type"] == "castAbility":
                    if actionDict['abilityDict'].get("name") == "End Unit Turn":
                       flatActionSpace.remove((unit, actionDict)) 
        unit, actionDict = random.choice(flatActionSpace)    
        return (unit, actionDict)

class MCTSAgent(Agent):
    def selectAction(self, waitingUnits, board, allActions, flatActionSpace):
        pass
        # gamma = 0.9
        # problem = MCTS.MDP(gamma, None, getActionFunction, None, getRewardFunction, getTransitionRewardFunction)
        # d = 12 #Tree depth
        # m = 500 #num simulations
        # c = 500 #exploration
        # solver = MCTS.MonteCarloTreeSearch(problem, {}, {}, d, m, c, dc.getValue)
        # return solver(dc)
    
class HumanAgent(Agent):
    selectedUnit = None
    def selectUnit(self, waitingUnits):
        self.aPygame.drawButtons({}, None)
        
        self.aPygame.getInput = True
        time.sleep(0.1)
        unitDict = self.game.actionQueue.get()
        selectedUnit = unitDict["unit"]
        self.selectedUnit = selectedUnit
        return selectedUnit
    
    def selectAction(self, waitingUnits, board, allActions, flatActionSpace):
        self.aPygame.drawSelectUnit(waitingUnits)
        if self.selectedUnit is None:
            unit = self.selectUnit(waitingUnits)
        else:
            if self.selectedUnit.ID not in allActions.keys():
                unit = self.selectUnit(waitingUnits)
            unit = self.selectedUnit
        unitAbilitiesDict = allActions[unit.ID]
        validAbilities = unitAbilitiesDict.get('abilities', None)
        validMoveDirections = unitAbilitiesDict.get('moves', None)
        if unit.canMove is False and unit.canAct is False:
            print(f"Warning! This should never happen, unit {unit.ID} that cannot act and cannot move in waitingUnits List")
            unit.Avail = False
            return (None, None)
        if unit.canMove or unit.canAct:
            self.aPygame.getInput = True
        
        
        self.aPygame.validDirections = validMoveDirections
        
        self.aPygame.drawButtons(validAbilities, unit)

        actionDict = self.game.actionQueue.get()
        if actionDict is not None:
            if actionDict["type"] == "unit":
                self.selectedUnit = actionDict["unit"]
                self.aPygame.getTarget = False
                (unit, actionDict) = self.selectAction(waitingUnits, board, allActions, None)


            self.aPygame.getInput = False
            self.aPygame.getTarget = False
            return (unit, actionDict)
        else:
            return (None, None)
        

