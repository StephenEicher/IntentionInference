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
            self.gPygame = rp.Pygame(self)            
            self.buttonsToBlit = []
            self.board = b.Board(25, 25, self, self.gPygame)

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
                waitingUnits, allActions = self.getAgentWaitingUnitsAndAbilities(self.currentAgent)
                selectedUnit, actionDict = self.currentAgent.selectAction(waitingUnits, self.board, allActions)
                if actionDict is None:
                    break
                # actionDict = self.moveQueue.get()
                # if actionDict["type"] == "unit":
                #     self.moveQueue.put(actionDict) # Need to re-insert the dict so that .get() when called during unit selection can pull the dictionary too
                #     break
                self.board.updateBoard(selectedUnit, actionDict)
                print(f"Current unit: {selectedUnit.ID}")
                print("===================================")
                print(f"Current movement: {selectedUnit.currentMovement}\nCurrent action points: {selectedUnit.currentActionPoints}")
            
            # if selectedUnit.Avail is False:
            #     print("Unit is NOT Avail!")
            #     self.gPygame.unitToMove = None
            # else:
            #     continue
            
            totalUnavail = 0
            for unit in self.currentAgent.team:
                if unit.Avail:
                    break
                else:
                    totalUnavail += 1

            if len(self.currentAgent.team) == totalUnavail:
                for unit in self.currentAgent.team: # Reset availability for next time that agent is up for turn
                    if unit.Alive:
                        unit.Avail = True
                        unit.canMove = True
                        unit.canAct = True
                        unit.movement = 4
                        unit.actionPoints = 2
                currentTurnActive = True
                self.agentTurnIndex ^= 1
    def getAgentWaitingUnitsAndAbilities(self, agent):
        waitingUnits = []
        allActions= {}
        for curUnit in agent.team:
            if curUnit.Alive and curUnit.Avail:
                waitingUnits.append(curUnit)
                allActions[curUnit.ID] = {}

        for curUnit in waitingUnits:
            id = curUnit.ID
            curDict = {}
            curDict['moves'] = self.board.getValidDirections(curUnit)
            curUnit.canMove = bool(curDict['moves'])
            validAbilities, _ = self.board.getValidAbilities(curUnit)
            curDict['abilities'] = validAbilities
            curUnit.canAct = bool(curDict['abilities'])
            allActions[curUnit.ID] = curDict
            
        return waitingUnits, allActions

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
        # waitingUnits = []
        # waitingUnitsIDs = []
        # for unit in self.team:
        #     if unit.Alive and unit.Avail:
        #         waitingUnits.append(unit)
        #         waitingUnitsIDs.append(unit.ID)

        # print((f"\nSelect from avail Units: {waitingUnitsIDs}\n"))
        self.aPygame.drawSelectUnit(waitingUnits)
        self.aPygame.getInput = True
        time.sleep(0.1)
        unitDict = self.game.actionQueue.get()
        selectedUnit = unitDict["unit"]
        self.selectedUnit = selectedUnit
        return selectedUnit
        # for unit in waitingUnits:
        #     if unit.ID == int(selectedUnitStr):
                
        #         return unit

    def selectAction(self, waitingUnits, board, allActions):
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
            return (unit, actionDict)
        else:
            return (None, None)
        


    # def selectMove(self, unit, board):
    #     validDirections = board.getValidDirections(unit)
    #     allAbilities = board.getValidAbilities(unit)
    #     self.validAbilities = allAbilities[0] # Returns list of dictionaries
    #     invalidAbilities = allAbilities[1]

    #     if unit.canMove is False and len(self.validAbilities) == 0:
    #         unit.Avail = False
    #         return False

    #     if unit.canMove or unit.canAct:
    #         self.aPygame.getInput = True
    #         self.aPygame.validDirections = validDirections
    #         self.aPygame.drawButtons(self.validAbilities, unit)

    #     return True

    # def selectTarget(self, ability):
    #     self.game.getTarget = True
    #     self.game.gPygame.unitToMove = None
    #     if ability.get("range") == 1:
    #         self.validTargets = self.game.board.meleeRangeTargets
    #     # if ability.get("range") > 1:
    #     #     self.validTargets = self.board.rangedRangeTargets
    #     castTarget = self.game.targetQueue.get()
    #     self.validTargets = None
    #     self.game.getTarget = False
    #     return castTarget

a = GameManager(True)