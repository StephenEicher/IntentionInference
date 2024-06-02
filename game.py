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

class GameManager:
    def __init__(self, p1Class, p2Class, teamComp, inclPygame = True):
        self.agentTurnIndex = 0
        self.gameOver = False
        self.inclPygame = inclPygame
        # self.gameLoopEvent = threading.Event()
        self.currentAgent = None
        self.inputReady = False
        self.p1Class = p1Class
        self.p2Class = p2Class
        if self.inclPygame:
            print('Including pygame...')
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

    def clone(self):
        cloned_game = GameManager.__new__(GameManager)
        cloned_game.agentTurnIndex = self.agentTurnIndex
        cloned_game.board = self.board.clone(cloned_game)
        team0 = []
        team1 = []
        for unit in self.p1.team:
            newUnit = copy.deepcopy(unit)
            newUnit.game = self
            newUnit.board = cloned_game.board
            team0.append(newUnit)
        
        for unit in self.p2.team:
            newUnit = copy.deepcopy(unit)
            newUnit.game = self
            newUnit.board = cloned_game.board
            team1.append(newUnit)
        cloned_game.p1 = ac.RandomAgent(self.p1.name, 0, team0, self, self.gPygame)
        cloned_game.p2 = self.p2Class(self.p2.name, 1, team1, self, self.gPygame)
        cloned_game.allAgents = [cloned_game.p1, cloned_game.p2]
        cloned_game.inclPygame = False
        cloned_game.gameOver = self.gameOver
        cloned_game.currentAgent = cloned_game.allAgents[cloned_game.agentTurnIndex]
        cloned_game.allUnits = team0
        cloned_game.allUnits.extend(team1)
        
        return cloned_game

    def start(self):
        if self.inclPygame:
            self.pygameThread = threading.Thread(target=self.gPygame.pygameLoop)
            self.pygameThread.daemon = True
            self.pygameThread.start()
            time.sleep(0.1)
        #self.gameLoop()
        self.queryAgentForMove()
    
    def executeMove(self, action):
        self.gameOverCheck()
        if not self.gameOver:
            changeTurnAgent = True
            selectedUnit, actionDict = action
            self.board.updateBoard(selectedUnit, actionDict)
            print(f"\nCurrent unit: {selectedUnit.ID}")
            print("===================================")
            print(f"Current movement: {selectedUnit.currentMovement}\nCurrent action points: {selectedUnit.currentActionPoints}")
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
            self.queryAgentForMove()

    def queryAgentForMove(self):
        self.gameOverCheck()
        if not self.gameOver:
            self.currentAgent = self.allAgents[self.agentTurnIndex] 
            print(f"\n-------- {self.currentAgent.name}'s turn --------")
            waitingUnits, allActions, flatActionSpace, noMovesOrAbilities = self.getCurrentStateActions()
            self.currentAgent.selectAction(self, waitingUnits, allActions, flatActionSpace)

    def gameOverCheck(self):
        if len(self.p1.team) == 0 or len(self.p2.team) == 0:
            self.gameOver = True
        if self.gameOver:
            if len(self.p1.team) == 0:
                print(f"\n{self.p2.name} wins")
            else:
                print(f"\n{self.p1.name} wins")

            if self.inclPygame:
                pygame.quit()

    def gameLoop(self):

        if self.inclPygame:      
            self.actionQueue = queue.Queue(maxsize = 1)    
            
        while self.gameOver is False:
            self.currentAgent = self.allAgents[self.agentTurnIndex]

            
            print(f"\n-------- {self.currentAgent.name}'s turn --------")
            #selectedUnit = self.currentAgent.selectUnit()
            #print(f"Selected {selectedUnit.ID}")   
            currentTurnActive= True
            while currentTurnActive:
                waitingUnits, allActions, flatActionSpace, noMovesOrAbilities = self.getCurrentStateActions()
                selectedUnit, actionDict = self.currentAgent.selectAction(self, waitingUnits, allActions, flatActionSpace)
                if actionDict is None:
                    break
                self.board.updateBoard(selectedUnit, actionDict)
                print(f"\nCurrent unit: {selectedUnit.ID}")
                print("===================================")
                print(f"Current movement: {selectedUnit.currentMovement}\nCurrent action points: {selectedUnit.currentActionPoints}")
            

                self.updateUnitStatus(self.allUnits)

                totalAvail = 0
                for unit in self.currentAgent.team:
                    if unit.Avail:
                        totalAvail += 1
                if totalAvail == 0:
                    currentTurnActive = False
            
            for unit in self.currentAgent.team: # Reset availability for next time that agent is up for turn
                if unit.Alive:
                    unit.resetForEndTurn()
            currentTurnActive = True
            self.agentTurnIndex ^= 1

            if len(self.p1.team) == 0 or len(self.p2.team) == 0:
                self.gameOver = True

        if self.gameOver:
            if len(self.p1.team) == 0:
                print(f"\n{self.p2.name} wins")
            if len(self.p2.team) == 0:
                print(f"\n{self.p1.name} wins")
            if self.inclPygame:
                pygame.quit()

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
                curUnit.dispose()

    def getCurrentStateActions(self):
        agent = self.allAgents[self.agentTurnIndex]
        waitingUnits = []
        allActions= {}
        noMovesOrAbilities = True
        endTurn = {'name' : 'End Unit Turn'}
        flatActionSpace = []
        for curUnit in agent.team:
            if curUnit.Alive and curUnit.Avail:
                waitingUnits.append(curUnit)
                allActions[curUnit.ID] = {}

        for curUnit in waitingUnits:
            curDict = {}
            if curUnit.canMove:
                curDict['moves'], flatValidDirections = self.board.getValidDirections(curUnit)
                flatActionSpace.extend(flatValidDirections)
            if curUnit.canAct:
                validAbilities, _, flatAbilities = self.board.getValidAbilities(curUnit)
                flatActionSpace.extend(flatAbilities)
                curDict['abilities'] = validAbilities
            flatEndTurn = (curUnit, {'type' : 'castAbility', 'abilityDict' : endTurn})
            flatActionSpace.extend([flatEndTurn])

            
            if bool(curDict.get('moves', None)) or bool(curDict.get('abilities', None)):
                noMovesOrAbilities = False
            if 'abilities' in curDict.keys():
                curDict['abilities'].append(endTurn)
            else:
                curDict['abilities'] = [endTurn]
            allActions[curUnit.ID] = curDict
            
        return waitingUnits, allActions, flatActionSpace, noMovesOrAbilities
    

team1 = [ [(0, 0), u.meleeUnit],
            [(0, 1), u.rangedUnit],]
team2 =  [  [(1,0), u.meleeUnit],
            [(1, 1), u.rangedUnit]]

teamComp = [team1, team2]
a = GameManager(ac.HumanAgent, ac.RandomAgent, teamComp, True)
a.start()
# b = a.clone()
# b.start()