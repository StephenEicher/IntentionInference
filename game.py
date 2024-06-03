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

class GameManager:
    def __init__(self, p1Class, p2Class, teamComp, inclPygame = True):
        self.verbose = True
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
            maxX = 25
            maxY = 25
            self.gPygame = rp.Pygame(self, maxX, maxY)            
            self.board = b.Board(maxX, maxY, self, self.gPygame)  
            self.actionQueue = queue.Queue(maxsize = 1)          
        else:
            self.board = b.Board(25, 25, self, None)
        team0, team1 = self.board.initializeUnits(teamComp)
        self.allUnits = []
        self.allUnits.extend(team1)
        self.allUnits.extend(team0)
        self.p1 = self.p1Class('P1', 0, team0, self, self.gPygame)
        self.p2 = self.p2Class('P2', 1, team1, self, self.gPygame)
        self.allAgents = []
        self.allAgents.extend([self.p1, self.p2])
        self.currentAgent = self.allAgents[self.agentTurnIndex]
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
        for unit in self.p1.team:
            newUnit = copy.deepcopy(unit)
            newUnit.game = cloned_game
            newUnit.board = cloned_game.board
            team0.append(newUnit)
        
        for unit in self.p2.team:
            newUnit = copy.deepcopy(unit)
            newUnit.game = cloned_game
            newUnit.board = cloned_game.board
            team1.append(newUnit)
        
        # cloned_game.p1 = ac.RandomAgent(self.p1.name, 0, team0, self, None)
        # cloned_game.p2 = self.p2Class(self.p2.name, 1, team1, self, None)
        cloned_game.p1 = ac.MCTSAgent(self.p1.name, 0, team0, cloned_game, None)
        cloned_game.p2 = self.p2Class(self.p2.name, 1, team1, cloned_game, None)
        if isinstance(self.p2, ac.MCTSAgent):
            cloned_game.p1.d =  self.p2.d - 1
            cloned_game.p2.d =  self.p2.d - 1
        cloned_game.allAgents = [cloned_game.p1, cloned_game.p2]
        cloned_game.inclPygame = False
        cloned_game.gameOver = self.gameOver
        cloned_game.currentAgent = cloned_game.allAgents[cloned_game.agentTurnIndex]
        cloned_game.allUnits = list(team0)
        cloned_game.allUnits.extend(team1)
        cloned_game.p1Class = self.p1Class
        cloned_game.p2Class = self.p2Class
        cloned_game.verbose = False
        
        return cloned_game

    def start(self):
        if self.inclPygame:
            self.pygameThread = threading.Thread(target=self.gPygame.pygameLoop)
            self.pygameThread.daemon = True
            self.pygameThread.start()
            # time.sleep(0.5)
        self.gameLoop()
        #self.queryAgentForMove()
    
    def executeMove(self, action):
        self.gameOverCheck()
        if not self.gameOver:
            changeTurnAgent = True
            selectedUnitID, actionDict = action
            selectedUnit = self.getUnitByID(selectedUnitID)
            self.board.updateBoard(selectedUnit, actionDict)
            self.fprint(f"\nCurrent unit: {selectedUnit.ID}")
            self.fprint("===================================")
            self.fprint(f"Current movement: {selectedUnit.currentMovement}\nCurrent action points: {selectedUnit.currentActionPoints}")
            self.updateUnitStatus(self.allUnits)
            totalAvail = 0
            for unit in self.currentAgent.team:
                if unit.Avail:
                    changeTurnAgent = False
                    break

            if changeTurnAgent:
                for unit in self.currentAgent.team: # Reset availability for next time that agent is up for turn
                    if unit.Alive:
                        unit.resetForEndTurn()
                self.agentTurnIndex ^= 1    
                self.currentAgent = self.allAgents[self.agentTurnIndex]       
                self.gameOverCheck()
                
    def progressToNextAgentTurn(self, agent, queryAgentAfter=True):
        self.currentAgent = self.allAgents[self.agentTurnIndex] 
        if self.sameAgent(self.currentAgent, agent):
            if queryAgentAfter:
                self.queryAgentForMove()
        else:
            while not self.sameAgent(self.currentAgent, agent) and not self.gameOver:
                self.queryAgentForMove()

    def sameAgent(self, agent1, agent2):
        return agent1.agentIndex == agent2.agentIndex
    
    def queryAgentForMove(self):
        self.gameOverCheck()
        if not self.gameOver:
            self.currentAgent = self.allAgents[self.agentTurnIndex] 
            self.fprint(f"\n-------- {self.currentAgent.name}'s turn --------")
            flatActionSpace, waitingUnits, allActions, noMovesOrAbilities = self.getCurrentStateActions(self)
            action = self.currentAgent.selectAction(self, waitingUnits, allActions, flatActionSpace, 'queryAgent')
            self.executeMove(action)

    def gameOverCheck(self):
        if len(self.p1.team) == 0 or len(self.p2.team) == 0:
            self.gameOver = True
        if self.gameOver:
            if len(self.p1.team) == 0:
                self.fprint(f"\n{self.p2.name} wins")
            else:
                self.fprint(f"\n{self.p1.name} wins")

            if self.inclPygame:
                pygame.quit()
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
                flatActionSpace, waitingUnits, allActions, noMovesOrAbilities = self.getCurrentStateActions(self)
                selectedUnitID, actionDict = self.currentAgent.selectAction(self, waitingUnits, allActions, flatActionSpace, 'gameLoop')
                selectedUnit = self.getUnitByID(selectedUnitID)
                if actionDict is None:
                    break
                self.board.updateBoard(selectedUnit, actionDict)
                self.fprint(f"\nCurrent unit: {selectedUnit.ID}")
                self.fprint("===================================")
                self.fprint(f"Current movement: {selectedUnit.currentMovement}\nCurrent action points: {selectedUnit.currentActionPoints}")
            

                self.updateUnitStatus(self.allUnits)

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



    def updateUnitStatus(self, waitingUnits):
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
    def getCurrentStateActionsMDP(self, state):
        if state.gameOver:
            return []
        else:
            flatActionSpace, _, _, _ = self.getCurrentStateActions(state)
            return flatActionSpace
    def getCurrentStateActions(self, state):
        agent = state.allAgents[state.agentTurnIndex]
        waitingUnits = []
        allActions= {}
        noMovesOrAbilities = True
        endTurn = Map({'name' : 'End Unit Turn'})
        flatActionSpace = []
        for curUnit in agent.team:
            if curUnit.Alive and curUnit.Avail:
                waitingUnits.append(curUnit)
                allActions[curUnit.ID] = {}

        for curUnit in waitingUnits:
            curDict = {}
            if curUnit.canMove:
                curDict['moves'], flatValidDirections = state.board.getValidDirections(curUnit)
                flatActionSpace.extend(flatValidDirections)
            if curUnit.canAct:
                validAbilities, _, flatAbilities = state.board.getValidAbilities(curUnit)
                flatActionSpace.extend(flatAbilities)
                curDict['abilities'] = validAbilities
            flatEndTurn = (curUnit.ID, Map({'type' : 'castAbility', 'abilityDict' : endTurn}))
            flatActionSpace.extend([flatEndTurn])

            
            if bool(curDict.get('moves', None)) or bool(curDict.get('abilities', None)):
                noMovesOrAbilities = False
            if 'abilities' in curDict.keys():
                curDict['abilities'].append(endTurn)
            else:
                curDict['abilities'] = [endTurn]
            allActions[curUnit.ID] = curDict
            
        return flatActionSpace, waitingUnits, allActions, noMovesOrAbilities

    def disposeUnit(self, unitToDispose):
        posessingAgent = self.allAgents[unitToDispose.agentIndex]
        # for unit in self.game.allAgents
        team = posessingAgent.team
        for unit in self.allUnits:
            if unit.ID == unitToDispose.ID:
                self.allUnits.remove(unit)

        for unit in team:
            if unit.ID == unitToDispose.ID:
                team.remove(unit)
                if unitToDispose.sprite is not None:
                    self.board.bPygame.spriteGroup.remove(unit.sprite)
                self.board.instUM.map[unit.position[0]][unit.position[1]] = None
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
    team1 = [ [(0, 0), u.meleeUnit],
                [(0, 1), u.rangedUnit],]
    team2 =  [  [(6,6), u.meleeUnit],
                [(7, 6), u.rangedUnit]]

    teamComp = [team1, team2]
    a = GameManager(ac.HumanAgent, ac.MCTSAgent, teamComp, True)
    a.start()
    # b = a.clone()
    # b.start()