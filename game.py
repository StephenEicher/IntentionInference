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
        self.getInput = False
        self.inputReady = False
        self.start()

    def start(self):
        if self.inclPygame:
            print('Including pygame...')
            import RunPygame as rp
            self.gPygame = rp.Pygame(self)
            self.board = b.Board(25, 25, self.gPygame)
            self.pygameThread = threading.Thread(target=self.gPygame.pygameLoop)
            self.pygameThread.daemon = True
            self.pygameThread.start()

        else:
            self.board = b.Board(25, 25, None)
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
            
        while not self.gameOver:
            currentAgent = self.allAgents[self.agentTurnIndex]
            print(f"-------- {currentAgent.name}'s turn --------")
            
            selectedUnit = currentAgent.selectUnit()
            while selectedUnit.unitValidForTurn():
                currentAgent.selectMove(selectedUnit, self.board)
                moveDict = self.moveQueue.get()
                print(moveDict)
                if moveDict.get("type") == "swap":
                    break
                self.board.updateBoard(selectedUnit, moveDict)
                self.getInput = False

            # self.gameState += 0.5

            # if turnFinished == True:
            #     self.agentTurnIndex = 1

            # if self.agentTurnIndex == 1:

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
        time.sleep(0.1)
        selectedUnitStr = input()
        print(selectedUnitStr)

        for unit in waitingUnits:
            if unit.ID == int(selectedUnitStr):
                return unit

    def selectMove(self, unit, board):
        validDirections = board.getValidDirections(unit)
        allAbilities = board.getValidAbilities(unit)
        validAbilities = allAbilities[0] # Returns list of dictionaries
        invalidAbilities = allAbilities[1]

        # rely on queue system to communicate pygame input directly to the game loop
        # probably just make more variables on agents assigned by Board operations instance-wide and accessible to pygame class somehow..
        # this seems it would require both instances of the agent classes to be passed to pygame at initialization?
        # the issue then is added complexity in terms of first parsing which agent to call on? maybe not so difficult to implement..

        # also troubleshoot incorrect mouse coordinates during click input event

        # print(f"Current HP: {unit.currentHP}")
        # if unit.canMove:
        #     print(f"\nMovement = {unit.currentMovement}. Available directions:\n")
        #     for direction, value in validDirections.items():
        #         fallDamage = value[0]
        #         surfacesList = value[1]
        #         allNames = []
        #         for surface in surfacesList:
        #             if surface != []:
        #                 surfaceName = surface.debugName
        #                 allNames.append(surfaceName)

        #         print("".join(f"{direction}: fall damage = {fallDamage}, surfaces = {allNames}\n"))

        #     validDirectionNames = [direction[0] for direction in validDirections.keys()]

        # if not unit.canMove:
        #     print("\nOut of movement!\n")

        # if unit.canAct:
        #     print(f"\nAction Points = {unit.currentActionPoints}. Valid abilities:\n")
        #     for ability in validAbilities:
        #         name = ability.get("name")
        #         cost = ability.get("cost")
        #         print("".join([f"{name}: {cost}\n"]))
        #     print("--------------------------")
        #     print("Unavailable abilities:\n")
        #     print("\n".join([f"{name}: {cost}" for name, cost in invalidAbilities.items()]))

        # while True:            
        if unit.canMove or unit.canAct:
            self.game.getInput = True
            self.aPygame.drawButtons(validDirections, validAbilities)
            # pReturnDict = self.agentQueue.get()
                # if pReturnDict["type"] == "move":
                #     return pReturnDict["directionDict"]                    
                # if pReturnDict["type"] == "castAbility":
                #     return pReturnDict["abilityDict"]
                # else:
                #     continue

                # agentInput = input("\nTo move in an available direction, type the direction. To cast ability, type the ability. To swap, type 'swap'\n")

                # if agentInput == "swap":
                #     returnDict = {"type" : "swap"}
                #     return returnDict
                # if unit.canMove:
                #     if agentInput in validDirectionNames:
                #         returnDict = {"type" : "move"}
                #         for direction, value in validDirections.items():
                #             if agentInput == direction[0]:
                #                 returnDict[direction] = value

                # if unit.canAct:
                #     for ability in validAbilities:
                #         if agentInput in ability.get("name"):
                #             returnDict = {"type" : "castAbility"}
                #             target = board.getTarget(ability)
                #             returnDict["target"] = target
                #             returnDict["ability"] = ability

            # return returnDict
        
a = GameManager(True)