import pygame
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
        self.gameOver = False
        pygame.init()
        self.start()

    def start(self):
        self.Board = b.BoardDirector(25, 25)
        allUnits = self.Board.initializeUnits()
        team0 = []
        team1 = []
        team0.extend([allUnits[0]]) #, self.allUnits[1]
        # self.team1.extend([self.allUnits[2], self.allUnits[3]])
        self.p1 = HumanAgent('Ally', 0, team0)
        self.p2 = HumanAgent('Bob', 1, team1)
        self.allAgents = []
        self.allAgents.extend([self.p1, self.p2])
        # self.gameLoop()
        
    def gameLoop(self):
        clock = pygame.time.Clock()

        if len(self.p1.team) == 0 and len(self.p2.team) == 0:
            self.gameOver = True

        while self.gameOver == False:

            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameOver = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.gameOver = True

            currentAgent = self.allAgents[self.agentTurnIndex]
            print(f"-------- {currentAgent.name}'s turn --------")
            
            selectedUnit = currentAgent.selectUnit()
            while selectedUnit.unitValidForTurn():
                moveDict = currentAgent.selectMove(selectedUnit, self.Board)
                if moveDict.get("type") == "swap":
                    break
                self.Board.updateBoard(selectedUnit, moveDict)
                self.Board.updateScreen()

            # self.gameState += 0.5

            # if turnFinished == True:
            #     self.agentTurnIndex = 1

            # if self.agentTurnIndex == 1:

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
            if unit.Alive and unit.Avail:
                waitingUnits.append(unit)

        waitingUnitsIDs = []
        for unit in waitingUnits:
            waitingUnitsIDs.append(unit.unitID)

        print((f"\nSelect from avail Units: {waitingUnitsIDs}\n"))
        time.sleep(0.1)
        selectedUnitStr = input()
        print(selectedUnitStr)

        for unit in waitingUnits:
            if unit.unitID == int(selectedUnitStr):
                return unit

    def selectMove(self, unit, board):
        validDirections = board.getValidDirections(unit)
        allAbilities = board.getValidAbilities(unit)
        validAbilities = allAbilities[0] # Returns list of dictionaries
        invalidAbilities = allAbilities[1]

        while True:
            print(f"Current HP: {unit.currentHP}")
            if unit.canMove:
                print(f"\nMovement = {unit.currentMovement}. Available directions:\n")
                for direction, value in validDirections.items():
                    fallDamage = value[0]
                    surfacesList = value[1]
                    allNames = []
                    for surface in surfacesList:
                        if surface != []:
                            surfaceName = surface.debugName
                            allNames.append(surfaceName)

                    print("".join(f"{direction}: fall damage = {fallDamage}, surfaces = {allNames}\n"))

                validDirectionNames = [direction[0] for direction in validDirections.keys()]

            if not unit.canMove:
                print("\nOut of movement!\n")

            if unit.canAct:
                print(f"\nAction Points = {unit.currentActionPoints}. Valid abilities:\n")
                for ability in validAbilities:
                    name = ability.get("name")
                    cost = ability.get("cost")
                    print("".join([f"{name}: {cost}\n"]))
                print("--------------------------")
                print("Unavailable abilities:\n")
                print("\n".join([f"{name}: {cost}" for name, cost in invalidAbilities.items()]))
            
            if unit.canMove or unit.canAct:
                agentInput = input("\nTo move in an available direction, type the direction. To cast ability, type the ability. To swap, type 'swap'\n")

                if agentInput == "swap":
                    returnDict = {"type" : "swap"}
                    return returnDict
                if unit.canMove:
                    if agentInput in validDirectionNames:
                        returnDict = {"type" : "move"}
                        for direction, value in validDirections.items():
                            if agentInput == direction[0]:
                                returnDict[direction] = value

                if unit.canAct:
                    for ability in validAbilities:
                        if agentInput in ability.get("name"):
                            returnDict = {"type" : "castAbility"}
                            target = board.getTarget(ability)
                            returnDict["target"] = target
                            returnDict["ability"] = ability

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