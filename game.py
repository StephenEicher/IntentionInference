import pygame
import queue
import threading
import random
import numpy as np
from  opensimplex import OpenSimplex
import matplotlib.pyplot as plt
import time
import AgentClasses as ac
import copy
import Units as u
import Board as b
import GameObjects as go
import SpriteClasses as sc
from immutables import Map
from mcts.base.base import BaseState, BaseAction
import sys

class GameManager(BaseState):
    def __init__(self, p1Class, p2Class, teamComp, inclPygame = True, seed=random.randint(0, 999999), verbose=True):
        random.seed(seed)
        self.verbose = verbose
        self.agentTurnIndex = 0
        self.gameOver = False
        self.inclPygame = inclPygame
        # self.gameLoopEvent = threading.Event()
        self.currentAgent = None
        self.inputReady = False
        self.p1Class = p1Class
        self.p2Class = p2Class
        if self.inclPygame:
            self.fprint('Including pygame...')
            import RunPygame as rp
            maxX = 8
            maxY = 8
            self.gPygame = rp.Pygame(self, maxX, maxY)            
            self.board = b.Board(maxX, maxY, self, self.gPygame)  
            self.pgQueue = queue.Queue(maxsize = 1)          
        else:
            self.board = b.Board(8, 8, self, None)
        team0, team1 = self.board.initializeUnits(teamComp)
        self.allUnits = {}
        for unit in team0:
            self.allUnits[unit.ID] = unit
        for unit in team1:
            self.allUnits[unit.ID] = unit
        self.allUnits = Map(self.allUnits)
        self.p1 = self.p1Class('P1', 0, team0, self, self.gPygame)
        self.p2 = self.p2Class('P2', 1, team1, self, self.gPygame)
        self.allAgents = []
        self.allAgents.extend([self.p1, self.p2])
        self.currentAgent = self.allAgents[self.agentTurnIndex]
        self.nTurns = 0
        self.winner = None
    def fprint(self, string):
        if self.verbose:
            print(string)
    def clone(self):
        cloned_game = GameManager.__new__(GameManager)
        cloned_game.agentTurnIndex = self.agentTurnIndex
        cloned_game.board = self.board.clone(cloned_game)
        self.gPygame = None
        team0 = []
        team1 = []
        cloned_game.allUnits = {}
        
        for unit in self.p1.team:
            newUnit = copy.deepcopy(unit)
            newUnit.game = cloned_game
            newUnit.board = cloned_game.board
            team0.append(newUnit)
            self.allUnits[newUnit.ID] = newUnit
        
        for unit in self.p2.team:
            newUnit = copy.deepcopy(unit)
            newUnit.game = cloned_game
            newUnit.board = cloned_game.board
            team1.append(newUnit)
            self.allUnits[newUnit.ID] = newUnit
        self.allUnits = Map(self.allUnits)
        # cloned_game.p1 = ac.RandomAgent(self.p1.name, 0, team0, self, None)
        # cloned_game.p2 = self.p2Class(self.p2.name, 1, team1, self, None)
        cloned_game.p1 = self.p1Class(self.p1.name, 0, team0, cloned_game, None)
        cloned_game.p2 = self.p2Class(self.p2.name, 1, team1, cloned_game, None)
        cloned_game.allAgents = [cloned_game.p1, cloned_game.p2]
        cloned_game.inclPygame = False
        cloned_game.gameOver = self.gameOver
        cloned_game.currentAgent = cloned_game.allAgents[cloned_game.agentTurnIndex]

        cloned_game.p1Class = self.p1Class
        cloned_game.p2Class = self.p2Class
        cloned_game.winner = self.winner
        cloned_game.verbose = False
        cloned_game.nTurns = self.nTurns
        
        return cloned_game

    def start(self):
        if self.inclPygame:
            self.pygameThread = threading.Thread(target=self.gPygame.pygameLoop)
            self.pygameThread.daemon = True
            self.pygameThread.start()
            # time.sleep(0.5)
        self.gameLoop()
        #self.queryAgentForMove()
    def take_action(self, action:any):
            newState = self.clone()
            newState.executeMove(action)
            if self.agentTurnIndex == 0:
                print('Human Turn')
            return newState
    
    def is_terminal(self):
        self.gameOverCheck()
        return self.gameOver

    def get_possible_actions(self):
        actions = self.getCurrentStateActionsMDP(self)
        random.shuffle(actions)
        # if len(actions) > 4:
        #     actions = actions[:4]
        return actions
    
    def get_current_player(self):
        if self.agentTurnIndex == 1:
            return 1
        else:
            return -1
    def get_action_reward(self, action):
        weights = self.p2.weights
        unitID, actionDict = action
        if actionDict.get('type', None) == 'castAbility':
            return 3 * weights['action']
        return weights['no_action'] 
    def get_reward(self):
        # value = self.p2.getValue(self)
        # return value * 10 - self.nTurns
        weights = self.p2.weights
        self.gameOverCheck()
        gameOverReward = 100 * weights['end_game']
        nTurnReward = self.nTurns * weights['n_turns']
        if self.gameOver:
            if self.winner == 0:
                return -gameOverReward + nTurnReward
            else:
                return gameOverReward + nTurnReward
        else:
            return nTurnReward

    def executeMove(self, action):
        self.gameOverCheck()
        if not self.gameOver:
            self.nTurns = self.nTurns + 1
            changeTurnAgent = True
            selectedUnitID, actionType, info = action
            # selectedUnit = self.getUnitByID(selectedUnitID)
            selectedUnit = self.allUnits[selectedUnitID]
            self.board.updateBoard(action)
            self.fprint(f"\nCurrent unit: {selectedUnitID}")
            self.fprint("===================================")
            self.fprint(f"Current movement: {selectedUnit.currentMovement}\nCurrent action points: {selectedUnit.currentActionPoints}")
            self.updateUnitStatus()
            totalAvail = 0
            for unit in self.currentAgent.team:
                if unit.Avail:
                    changeTurnAgent = False
                    break
            self.gameOverCheck()
            if changeTurnAgent:
                for unit in self.currentAgent.team: # Reset availability for next time that agent is up for turn
                    if unit.Alive:
                        unit.resetForEndTurn()
                self.agentTurnIndex ^= 1    
                self.currentAgent = self.allAgents[self.agentTurnIndex]       
                self.gameOverCheck()
                
    # def progressToNextAgentTurn(self, agent, queryAgentAfter=True):
    #     self.currentAgent = self.allAgents[self.agentTurnIndex] 
    #     if self.sameAgent(self.currentAgent, agent):
    #         if queryAgentAfter:
    #             self.queryAgentForMove()
    #     else:
    #         while not self.sameAgent(self.currentAgent, agent) and not self.gameOver:
    #             self.queryAgentForMove()

    # def sameAgent(self, agent1, agent2):
    #     return agent1.agentIndex == agent2.agentIndex
    
    # def queryAgentForMove(self):
    #     self.gameOverCheck()
    #     if not self.gameOver:
    #         self.currentAgent = self.allAgents[self.agentTurnIndex] 
    #         self.fprint(f"\n-------- {self.currentAgent.name}'s turn --------")
    #         flatActionSpace, waitingUnits, allActions, noMovesOrAbilities = self.getCurrentStateActions(self)
    #         action = self.currentAgent.selectAction(self, waitingUnits, allActions, flatActionSpace, 'queryAgent')
    #         self.executeMove(action)

    def gameOverCheck(self):
        if len(self.p1.team) == 0 or len(self.p2.team) == 0:
            self.gameOver = True
        if self.gameOver:
            if len(self.p1.team) == 0:
                self.fprint(f"\n{self.p2.name} wins")
                self.winner = 1
            else:
                self.fprint(f"\n{self.p1.name} wins")
                self.winner = 0
            self.quit()

    def quit(self):
        if self.inclPygame:
            time.sleep(0.5)
            try:
                self.pygameThread.join()
            except:
                pass
        self.gameOver = True
        if self.winner is not None:
            return self.winner

    def getUnitByID(self, ID):
        for unit in self.allUnits:
            if unit.ID == ID:
                return unit
    def gameLoop(self):
        while self.gameOver is False:
            self.currentAgent = self.allAgents[self.agentTurnIndex]

            
            self.fprint(f"\n-------- {self.currentAgent.name}'s turn --------")
            #selectedUnit = self.currentAgent.selectUnit()
            #print(f"Selected {selectedUnit.ID}")   
            currentTurnActive= True
            while currentTurnActive:
                actionSpace = self.getCurrentStateActions(self)
                tStart = time.time()
                action = self.currentAgent.selectAction(self, actionSpace, 'gameLoop')
                if action is None:
                    break
                selectedUnitID, actionType, info = action
                # self.fprint('Time to make move: ')
                # self.fprint(time.time() - tStart)
                selectedUnit = self.allUnits[selectedUnitID]
                self.board.updateBoard(action)
                self.nTurns = self.nTurns + 1
                self.fprint(f"\nCurrent unit: {selectedUnit.ID}")
                self.fprint("===================================")
                self.fprint(f"Current movement: {selectedUnit.currentMovement}\nCurrent action points: {selectedUnit.currentActionPoints}")
            

                self.updateUnitStatus()

                totalAvail = 0
                for unit in self.currentAgent.team:
                    if unit.Avail:
                        totalAvail += 1
                        break
                if totalAvail == 0:
                    currentTurnActive = False
            
            for unit in self.currentAgent.team: # Reset availability for next time that agent is up for turn
                if unit.Alive:
                    unit.resetForEndTurn()

            currentTurnActive = True
            self.agentTurnIndex ^= 1
            self.gameOverCheck()



    def updateUnitStatus(self, waitingUnits=None):
           if waitingUnits is None:
               waitingUnits = list(self.allUnits.values())
           for curUnit in waitingUnits:
            if curUnit.currentMovement <= 0:
                curUnit.canMove = False
            if curUnit.currentActionPoints <= 0:
                curUnit.canAct = False
            if not curUnit.canAct and not curUnit.canMove:
                curUnit.Avail = False
            if curUnit.currentHP <= 0:
                curUnit.Alive = False
                self.disposeUnit(curUnit)


    def getCurrentStateActions(self, state):
        """ For the current state, returns action space. Action Format: (unitID, actionMap) """

        agent = state.allAgents[state.agentTurnIndex]
        waitingUnits = []
        actionSpace = []
        for curUnit in agent.team:
            if curUnit.Alive and curUnit.Avail:
                waitingUnits.append(curUnit)

        for curUnit in waitingUnits:
            if curUnit.canMove:
                moveTargs = state.board.getValidMoveTargets(curUnit.position)
                for target in moveTargs:
                    actionSpace.append((curUnit.ID, 'move', target))
            if curUnit.canAct:
                validAbilities = state.board.getValidAbilities(curUnit)
                for ability in validAbilities:
                    actionSpace.append((curUnit.ID, 'ability', ability))

        return actionSpace

    def disposeUnit(self, unitToDispose):
        posessingAgent = self.allAgents[unitToDispose.agentIndex]
        # for unit in self.game.allAgents
        team = posessingAgent.team
        # for unit in self.allUnits:
        #     if unit.ID == unitToDispose.ID:
        #         self.allUnits.remove(unit)
        allUnits = dict(self.allUnits)
        del allUnits[unitToDispose.ID] 
        self.allUnits = allUnits

        for unit in team:
            if unit.ID == unitToDispose.ID:
                team.remove(unit)
                if unitToDispose.sprite is not None:
                    self.board.bPygame.spriteGroup.remove(unit.sprite)
                self.board.units_map[unit.position[0], unit.position[1]] = 0
                self.fprint(f"{unit.ID} is disposed")

    def __hash__(self):
        return hash(tuple(self.constructCompVars()))
    
    def __eq__(self, other):
        if isinstance(other, GameManager):
            return (self.constructCompVars() == other.constructCompVars())
        return False       
       
    def constructCompVars(self):
        IDList = []
        posList = []
        hpList = []
        APList = []
        movementList = []
        aliveList = []
        CMList = []
        CAList = []
        for unit in self.allUnits:
            IDList.append(unit.ID)
            posList.append(unit.position)
            hpList.append(unit.HP)
            APList.append(unit.currentActionPoints)
            movementList.append(unit.currentMovement)
            aliveList.append(unit.Alive)
            CMList.append(unit.canMove)
            CAList.append(unit.canAct)
        combined = list(zip(IDList, posList, hpList, APList, APList, movementList, aliveList, CMList, CAList))
        sorted_combined = sorted(combined, key=lambda x: x[0])
        sorted_combined = [tuple(item) for item in sorted_combined]
        return sorted_combined
    def getOpponentTeam(self, agentIndex):
        for agent in self.allAgents:
            if agent.agentIndex is not agentIndex:
                return agent.team

if __name__ == '__main__':
    team1 = [ [(3, 3), u.meleeUnit],
                [(0, 1), u.rangedUnit],]
    team2 =  [  [(6,6), u.meleeUnit],
                [(6, 7), u.rangedUnit]]

    teamComp = [team1, team2]
    a = GameManager(ac.HumanAgent, ac.HumanAgent, teamComp, True)
    a.start()
    # b = a.clone()
    # b.start()