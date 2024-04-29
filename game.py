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
    def __init__(self):
        self.agentTurnIndex = 0
        self.allAgents = []
        self.gameState = 0 # gameState increases per completion of each agent's turn
        self.gameOver = False
        self.start()

    def start(self):
        self.Board = b.BoardDirector(50, 50)
        self.allUnits = self.Board.initializeUnits()
        self.team0 = []
        self.team1 = []
        self.team0.extend([self.allUnits[0], self.allUnits[1]])
        self.team1.extend([self.allUnits[2], self.allUnits[3]])
        self.p1 = HumanAgent('Ally', 0, self.team0)
        self.p2 = HumanAgent('Bob', 1, self.team1)
        self.allAgents.extend([self.p1, self.p2])
        self.gameLoop()
        
    def gameLoop(self):

        if len(self.p1.team) == 0 or len(self.p2.team) == 0:
            self.gameOver = True

        while self.gameOver == False:
    
            currentAgent = self.allAgents[self.agentTurnIndex]

            print(f"-------- {currentAgent.name}'s turn --------")
            selectedUnit = currentAgent.selectUnit()
            while selectedUnit.unitValidForTurn():
                moveDict = currentAgent.selectMove(selectedUnit, self.Board)
                if moveDict.get("type") == "move":
                    self.Board.move(selectedUnit, moveDict)
                # else:
                #     pendingEvents = self.createEvents(moveDict, selectedUnit)
                #     self.dispatcher.dispatch(pendingEvents)

            # self.gameState += 0.5

            # if turnFinished == True:
            #     self.agentTurnIndex = 1

            # if self.agentTurnIndex == 1:

    # def createEvents(self, agentInput, unit):
    #     if "move" in agentInput:
    #         direction = agentInput[1]
    #         destination = self.validDirections[direction]
    #         moveEvent = eMove(unit, destination)
    #         return moveEvent

        # if "action" in agentInput:
        #     actionName = agentInput[1]
        #     subevents = []
        #     allActions = unit.actions()
        #     for _, actionDict in allActions.items():
        #         if actionName in actionDict:
        #             subevents.extend(actionDict["events"])

        # if "swap" in agentInput:
        #     # Do not create event, call loo
 
class Agent(metaclass=abc.ABCMeta):
    def __init__(self, name, agentIndex, team):       
        self.name = name
        self.agentIndex = agentIndex
        self.team = team
    @abc.abstractmethod
    def selectUnit(self):
        pass

class HumanAgent(Agent):
    def selectUnit(self):
        waitingUnits = []
        for unit in self.team:
            if unit.Alive == True and unit.Avail == True:
                waitingUnits.append(unit)

        waitingUnitsNames = []
        for unit in waitingUnits:
            waitingUnitsNames.append(unit.unitID)

        print((f"\nSelect from avail Units: {waitingUnitsNames}\n"))
        time.sleep(0.1)
        selectedUnitStr = input()
        print(selectedUnitStr)
        
        for unit in waitingUnits:
            if unit.unitID == int(selectedUnitStr):
                return unit

    def selectMove(self, unit, board):
        validDirections = board.getValidDirections(unit)
        # validAbilities = board.getValidAbilities(unit)[0]
        # invalidActions = board.getValidAbilities(unit)[1]

        while True:
            print(f"\nAvailable directions:\n")
            for direction, value in validDirections.items():
                fallDamage = value[0]
                surfacesList = value[1]
                allNames = []
                for surface in surfacesList:
                    if surface != []:
                        surfaceName = surface.debugName
                        allNames.append(surfaceName)

                print("".join(f"{direction}: fall damage = {fallDamage}, surfaces = {allNames}\n"))

            # print("Affordable actions:\n")
            # for ability in validAbilities:
            #     name = ability.get("name")
            #     cost = ability.get("cost")
            #     print("".join([f"{name}: {cost}\n"]))
            # print("---")
            # print(f"Unavailable actions:\n".join([f"{name}: {cost}" for name, cost in invalidActions.items()]))
            agentInput = input("\n\nTo move in a available direction, type the direction. To swap, type 'swap'\n")

            validDirectionNames = [direction[0] for direction in validDirections.keys()]

            if agentInput in validDirectionNames:
                returnDict = {"type" : "move"}
                for direction, value in validDirections.items():
                    if agentInput == direction[0]:
                        returnDict[direction] = value

                return returnDict

            # if agentInput in self.validActions.items():
            #     allActions = unit.actions()

            #     for _, actionDict in allActions.items():
            #         if agentInput in actionDict:
            #             for eventDict in actionDict["events"]:
            #                 if "targetunit" in eventDict:     
            #     return ["action", input]

            # if agentInput == "swap":
            #     return ["swap"]

            print("\n\n!!!! Invalid input !!!!")

a = GameManager()