import pygame
import queue
import threading
import random
import numpy as np
from  opensimplex import OpenSimplex
import matplotlib.pyplot as plt
import time
import abc

import Units as u
import Board as b
import GameObjects as go
import SpriteClasses as sc

class GameManager:
    def __init__(self, inclPygame = True):
        self.agentTurnIndex = 0
        self.gameOver = False
        self.inclPygame = inclPygame
        # self.gameLoopEvent = threading.Event()
        self.currentAgent = None
        self.inputReady = False
        
        self.start()

    def start(self):
        if self.inclPygame:
            print('Including pygame...')
            import RunPygame as rp
            maxX = 25
            maxY = 25
            self.gPygame = rp.Pygame(self, maxX, maxY)            
            self.board = b.Board(maxX, maxY, self, self.gPygame)
            self.pygameThread = threading.Thread(target=self.gPygame.pygameLoop)
            self.pygameThread.daemon = True
            self.pygameThread.start()

        else:
            self.board = b.Board(25, 25, self, None)
        time.sleep(1)
        allUnits = self.board.initializeUnits()
        team0 = []
        team1 = []
        team0.extend([allUnits[0], allUnits[1]])
        team1.extend([allUnits[2], allUnits[3]])
        self.allUnits = allUnits
        self.p1 = HumanAgent('Ally', 0, team0, self, self.gPygame)
        self.p2 = HumanAgent('Bob', 1, team1, self, self.gPygame)
        self.allAgents = []
        self.allAgents.extend([self.p1, self.p2])
        self.gameLoop()
          
    def gameLoop(self):
        if len(self.p1.team) == 0 and len(self.p2.team) == 0:
            self.gameOver = True

        if self.inclPygame:      
            self.actionQueue = queue.Queue(maxsize = 1)    
            
        while self.gameOver is False:
            self.currentAgent = self.allAgents[self.agentTurnIndex]

            
            print(f"\n-------- {self.currentAgent.name}'s turn --------")
            #selectedUnit = self.currentAgent.selectUnit()
            #print(f"Selected {selectedUnit.ID}")   
            currentTurnActive= True
            while currentTurnActive:
                waitingUnits, allActions, noMovesOrAbilities = self.getAgentWaitingUnitsAndAbilities(self.currentAgent)
                selectedUnit, actionDict = self.currentAgent.selectAction(waitingUnits, self.board, allActions)
                if actionDict is None:
                    break
                self.board.updateBoard(selectedUnit, actionDict)
                print(f"Current unit: {selectedUnit.ID}")
                print("===================================")
                print(f"Current movement: {selectedUnit.currentMovement}\nCurrent action points: {selectedUnit.currentActionPoints}")
            

                self.updateUnitStatus(self.allUnits)

                totalUnavail = 0
                for unit in self.currentAgent.team:
                    if unit.Avail:
                        if noMovesOrAbilities:
                            unit.Avail = False
                        else:
                            break
                    else:
                        totalUnavail += 1
                if len(self.currentAgent.team) == totalUnavail:
                    currentTurnActive = False
            
            for unit in self.currentAgent.team: # Reset availability for next time that agent is up for turn
                if unit.Alive:
                    unit.resetForEndTurn()
            currentTurnActive = True
            self.agentTurnIndex ^= 1
    def updateUnitStatus(self, waitingUnits):
           for curUnit in waitingUnits:
            if curUnit.currentMovement <= 0:
                curUnit.canMove = False
            if curUnit.currentActionPoints <= 0:
                curUnit.canAct = False
            if curUnit.currentHP <= 0:
                curUnit.Alive = False
            

    def getAgentWaitingUnitsAndAbilities(self, agent):
        waitingUnits = []
        allActions= {}
        noMovesOrAbilities = True
        endTurn = {'name' : 'End Unit Turn'}

        for curUnit in agent.team:
            if curUnit.Alive and curUnit.Avail:
                waitingUnits.append(curUnit)
                allActions[curUnit.ID] = {}
 
        for curUnit in waitingUnits:
            curDict = {}
            curDict['moves'] = self.board.getValidDirections(curUnit)
            validAbilities, _ = self.board.getValidAbilities(curUnit)
            curDict['abilities'] = validAbilities
            if bool( curDict['moves']) or bool(curDict['abilities']):
                noMovesOrAbilities = False
            curDict['abilities'].append(endTurn)
            allActions[curUnit.ID] = curDict
            
        return waitingUnits, allActions, noMovesOrAbilities

class Agent(metaclass=abc.ABCMeta):
    def __init__(self, name, agentIndex, team, game = None, pygame = None):       
        self.name = name
        self.agentIndex = agentIndex
        self.team = team
        self.game = game
        self.aPygame = pygame
        self.inputReady = False
    @abc.abstractmethod
    def selectUnit(self):
        pass

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
    
    def selectAction(self, waitingUnits, board, allActions):
        self.aPygame.drawSelectUnit(waitingUnits)
        if self.selectedUnit is None:
            unit = self.selectUnit(waitingUnits)
        else:
            if self.selectedUnit.ID not in allActions.keys():
                unit = self.selectUnit(waitingUnits)
            unit = self.selectedUnit
        unitAbilitiesDict = allActions[unit.ID]
        validAbilities = unitAbilitiesDict['abilities']
        validMoveDirections = unitAbilitiesDict['moves']
        if unit.canMove is False and unit.canAct is False:
            print("Warning! This should never happen, unit that cannot act and cannot move in waitingUnits List")
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
                (unit, actionDict) = self.selectAction(waitingUnits, board, allActions)


            self.aPygame.getInput = False
            self.aPygame.getTarget = False
            return (unit, actionDict)
        else:
            return (None, None)
        

a = GameManager(True)