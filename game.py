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
        self.getInput = False
        self.getTarget = False
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
        print('Starting gameLoop...')
        if len(self.p1.team) == 0 and len(self.p2.team) == 0:
            self.gameOver = True

        if self.inclPygame:
            self.moveQueue = queue.Queue(maxsize=1)
            self.targetQueue = queue.Queue(maxsize=1)            
            
        while self.gameOver is False:
            self.currentAgent = self.allAgents[self.agentTurnIndex]
            print(f"-------- {self.currentAgent.name}'s turn --------")
            selectedUnit = self.currentAgent.selectUnit()
            print(f"Selected {selectedUnit.ID}")
            while selectedUnit.unitValidForTurn():
                self.currentAgent.selectMove(selectedUnit, self.board)
                moveDict = self.moveQueue.get()
                if moveDict["type"] == "unit":
                    self.moveQueue.put(moveDict) # Need to re-insert the dict so that .get() when called during unit selection can pull the dictionary too
                    break
                self.board.updateBoard(selectedUnit, moveDict)
                self.getInput = False
            
            if selectedUnit.Avail is False:
                print("Unit is NOT Avail!")
                self.gPygame.unitToMove = None
            else:
                continue
            
            totalUnavail = 0
            for unit in self.currentAgent.team:
                if unit.Avail:
                    break
                else:
                    totalUnavail += 1

            if len(self.currentAgent.team) == totalUnavail:
                self.agentTurnIndex ^= 1

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
    def selectUnit(self):
        waitingUnits = []
        for unit in self.team:
            if unit.Alive and unit.Avail:
                waitingUnits.append(unit)

        waitingUnitsIDs = []
        for unit in waitingUnits:
            waitingUnitsIDs.append(unit.ID)

        print((f"\nSelect from avail Units: {waitingUnitsIDs}\n"))
        
        # selectedUnitStr = input()
        # print(selectedUnitStr)
        self.aPygame.drawSelectUnit(waitingUnitsIDs, waitingUnits)
        time.sleep(0.1)
        unitDict = self.game.moveQueue.get()
        selectedUnitStr = unitDict["unit"]
        for unit in waitingUnits:
            if unit.ID == int(selectedUnitStr):
                return unit

    def selectMove(self, unit, board):
        validDirections = board.getValidDirections(unit)
        print(validDirections)
        allAbilities = board.getValidAbilities(unit)
        self.validAbilities = allAbilities[0] # Returns list of dictionaries
        invalidAbilities = allAbilities[1]
        if len(self.validAbilities) == 0:
            unit.canAct = False

        if unit.canMove or unit.canAct:
            self.game.getInput = True
            self.aPygame.drawButtons(validDirections, self.validAbilities, unit)

    def selectTarget(self, ability):
        self.getTarget = True
        castTarget = self.game.targetQueue.get()
        return castTarget

a = GameManager(True)