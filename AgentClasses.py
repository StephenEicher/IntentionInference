import abc
import time
import random
import MCTS
import numpy as np
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
    def selectAction(self, game, waitingUnits, allActions, flatActionSpace, debugStr=None):
        if len(flatActionSpace) > 3:
            for unit, actionDict in flatActionSpace:
                if actionDict["type"] == "castAbility":
                    if actionDict['abilityDict'].get("name") == "End Unit Turn":
                       flatActionSpace.remove((unit, actionDict)) 
        unitID, actionDict = random.choice(flatActionSpace)  
        return (unitID, actionDict) 

# class GreedyAgent(Agent):
#     def selectAction(self, game, waitingUnits, allActions, flatActionSpace, debugStr=None):
#         attackActions = []
#         for unit, actionDict in flatActionSpace:
#             if actionDict["type"] == "castAbility":
#                 if actionDict['abilityDict'].get("name") != "End Unit Turn":
#                     attackActions.append((unit, actionDict))
#                 else:
#                     endTurnAction = (unit, actionDict)
#         if attackActions:
#             return random.choice(attackActions)
#         else:
#             centroid = np.zeros(2)
#             for unit in waitingUnits:
#                 centroid = centroid + np.array(unit.position)
#             centroid = np.mean(centroid)

#             d = np.Inf
#             unitToMoveTo = None
#             for unit in game.getOpponentTeam(self.agentIndex):
#                 qd = np.linalg.norm(np.array(unit.position) - centroid)
#                 if qd < d:
#                     d = qd
#                     unitToMoveTo = unit
#                 for unit in waitingUnits:
#                     if unit.ID in allActions.keys():    
#                         if allActions[unit.ID].get('moves', None) is not None:
#                             delta = np.array(unitToMoveTo.position) - np.array(unit.position)
#                             dirToMove = game.board.convDeltaToAdjDirections(delta)
#                             moves = list(allActions[unit.ID]['moves'].keys())
#                             key = None
#                             for dir in moves:
#                                 if dir[0] == dirToMove:
#                                     key = dir
#                             if key is not None:
#                                 actionDict = {'type': 'move', 'directionDict' : {key : allActions[unit.ID]['moves'][key]}}
#                                 return (unit.ID, actionDict)
                        
#         return random.choice(flatActionSpace)
                        
            
           
class MCTSAgent(Agent):
    def __init__(self, name, agentIndex, team, game = None, pygame = None):
        super().__init__(name, agentIndex, team, game, pygame)
        self.featureInitValues()
        self.d = 3

    def selectAction(self, game, waitingUnits, allActions, flatActionSpace, debugStr=None):
        gamma = 0.6
        if self.d > 0:
            problem = MCTS.MDP(gamma, None, game.getCurrentStateActionsMDP, None, self.getReward, self.getTransitionReward)
            d = self.d
            m = 10 #num simulations
            c = 1 #exploration
            solver = MCTS.MonteCarloTreeSearch(problem, {}, {}, d, m, c, self.getValue)
            out = solver(game.clone())
        else:
            out = random.choice(flatActionSpace)
        return out
    def getReward(self, state):
        return random.randint(0, 10)
    def getValue(self, state, debugStr=None):
        #Get self team
        # return random.randint(0, 10)
        self.agentIndex
        selfTeam = self.team
        nTeam = len(self.team)
        nOpp = 0
        oppTeam = []
        for agent in state.allAgents:
            if agent.agentIndex is not self.agentIndex:
                oppTeam = agent.team
                nOpp = len(oppTeam)
                break
        teamHP = 0
        for unit in self.team:
            teamHP += unit.HP
        oppHP = 0
        for unit in oppTeam:
            oppHP += unit.HP

        features = []
        features.append(-(oppHP/self.oppTeamInitHP))
        features.append(teamHP/self.teamInitHP)
        features.append(nTeam/self.nTeamInit)
        features.append(-nOpp/self.nOppInit)
        w = np.ones(len(features))
        features = np.array(features)
        return  np.sum(features*w)
        #Features - Team Total HP, Opponent team total HP, 


    def featureInitValues(self):
        self.teamInitHP = 0
        for unit in self.team:
            self.teamInitHP += unit.HP
        self.oppTeamInitHP = self.teamInitHP
        self.nTeamInit = len(self.team)
        self.nOppInit = len(self.team)


    def getTransitionReward(self, state, action):
        #Transition reward function will only ever be for Manager 0:
        Ucur = self.getValue(state, 'TR')
        sprime = state.clone()
        sprime.executeMove(action)
        sprime.progressToNextAgentTurn(self, False)
        Uprime = self.getValue(sprime, 'TR')
        return (sprime, Uprime - Ucur)

class GreedyAgent(MCTSAgent):
    def selectAction(self, game, waitingUnits, allActions, flatActionSpace, debugStr=None):
        gamma = 0.6
        problem = MCTS.MDP(gamma, None, game.getCurrentStateActionsMDP, None, self.getReward, self.getTransitionReward)
        d = 3 #Tree depth
        m = 100 #num simulations
        c = 1 #exploration
        solver = MCTS.MonteCarloTreeSearch(problem, {}, {}, d, m, c, self.getValue)
        out = solver(game)
        return out
        
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
    
    def selectAction(self, game, waitingUnits, allActions, flatActionSpace, debugStr=None):
        selectedUnit, actionDict = self.selectActionUI(game, waitingUnits, allActions, flatActionSpace)
        return (selectedUnit.ID, actionDict)

    def selectActionUI(self, game, waitingUnits, allActions, flatActionSpace):
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
                (unit, actionDict) = self.selectActionUI(game, waitingUnits, allActions, None)


            self.aPygame.getInput = False
            self.aPygame.getTarget = False
            return (unit, actionDict)
        else:
            return (None, None)
        

