import abc
import time
import random
import policies as p
import numpy as np
import MCTS as mcts
# from mcts.searcher.mcts import MCTS
import pickle
from immutables import Map
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
                        
            
class MCTSTestAgent(Agent):
    def __init__(self, name, agentIndex, team, game = None, pygame = None):
        super().__init__(name, agentIndex, team, game, pygame)
        self.featureInitValues()
        self.d = 10
        self.assignWeights([1, -1, 1, -1])
        self.time_limit = 6000
        self.record = False
    

    def selectAction(self, game, waitingUnits, allActions, flatActionSpace, debugStr=None):
        # searcher = MCTS(iteration_limit=20)

        searcher = mcts.MCTS(time_limit=self.time_limit, rollout_policy=lambda state: p.depth_limited_policy(state, max_depth=self.d))
        if game.gameOver:
            bestAction = random.choice(flatActionSpace)
        else:
            s = game.clone()
            turn = s.nTurns
            if self.record:
                with open(f'./GameHistories/1/Pre/turn_{turn}.pkl', 'wb') as file:
                    pickle.dump(s, file)
            bestAction, reward = searcher.search(initial_state = s, need_details=True)
            # print(reward)
            if bestAction is None:
                return random.choice(flatActionSpace)
            else:
                s.executeMove(bestAction)
                if self.record:
                    with open(f'./GameHistories/1/Post/turn_{turn}.pkl', 'wb') as file:
                        pickle.dump(s, file)
        return bestAction
    def assignWeights(self, x):
        weights = {}
        weights['action'] = x[0]
        weights['no_action'] = x[1]
        weights['end_game'] = x[2]
        weights['n_turns'] = x[3]
        self.weights = Map(weights)

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
        w = np.array([1, 1, 5, 5])
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


class HumanAgent(Agent):
    selectedUnit = None
    def selectUnit(self, waitingUnits):
        self.aPygame.drawButtons({}, None)
        
        self.aPygame.getInput = True
        time.sleep(0.1)
        unitDict = self.game.pgQueue.get()
        if unitDict is not None:
            selectedUnit = unitDict["unit"]
            self.selectedUnit = selectedUnit
            return selectedUnit
        else:
            return self.selectUnit(waitingUnits)
    
    def selectAction(self, game, actionSpace, debugStr=None):
        selectedUnit, actionDict = self.selectActionRecursive(game, actionSpace)
        return (selectedUnit.ID, actionDict)

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
        self.aPygame.drawSelectUnit(waitingUnits)

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
            return (None, None)
        if unit.canMove or unit.canAct:
            self.aPygame.getInput = True
        
        
        self.aPygame.validDirections = validMoveDirections
        
        self.aPygame.drawButtons(validAbilities, unit)
        action = self.game.pgQueue.get()

        if action is not None:
            if action["type"] == "unit":
                self.selectedUnit = action["unit"]
                self.aPygame.getTarget = False
                (unit, action) = self.selectActionRecursive(self, game, actionSpace)


            self.aPygame.getInput = False
            self.aPygame.getTarget = False
            return (unit, action)
        else:
            return (None, None)
        

