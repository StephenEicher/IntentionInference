import pygame
import queue
import threading
import random
import numpy as np
from  opensimplex import OpenSimplex
import matplotlib.pyplot as plt
import time
import agentClasses as ac
import copy
import unitClasses as u
import boardClasses as b
import gameObjectClasses as go
import spriteClasses as sc
from immutables import Map
#from mcts.base.base import BaseState, BaseAction
import sys
import pygameUI as rp

class GameManager():

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
            maxX = 8
            maxY = 8
            self.pygameUI = rp.Pygame(self, maxX, maxY)            
            self.board = b.Board(maxX, maxY, self)  
            self.pgQueue = queue.Queue(maxsize = 1)          
        else:
            self.board = b.Board(8, 8, self)
            self.pgQueue = None
        self.allUnits = {}
        self.initializeTeams(teamComp)
        self.allAgents = []
        self.allAgents.extend([self.p1, self.p2])
        self.currentAgent = self.allAgents[self.agentTurnIndex]
        self.nTurns = 0
        self.winner = None
        self.gameLoopComplete = False


    def fprint(self, string):
        if self.verbose:
            print(string)

    def clone(self):
        cloned_game = GameManager.__new__(GameManager)
        cloned_game.agentTurnIndex = self.agentTurnIndex
        cloned_game.board = self.board.clone(cloned_game)
        cloned_game.pygameUI = None
        team0 = []
        team1 = []
        cloned_game.allUnits = {}
        
        for unit in self.p1.team:
            newUnit = unit.clone()
            team0.append(newUnit)
            cloned_game.allUnits[newUnit.ID] = newUnit
        
        for unit in self.p2.team:
            newUnit = unit.clone()
            team1.append(newUnit)
            cloned_game.allUnits[newUnit.ID] = newUnit
        cloned_game.allUnits = Map(cloned_game.allUnits)

        cloned_game.p1 = self.p1Class(self.p1.name, 0, team0)
        cloned_game.p2 = self.p2Class(self.p2.name, 1, team1)

        cloned_game.allAgents = [cloned_game.p1, cloned_game.p2]
        cloned_game.inclPygame = False
        cloned_game.gameOver = self.gameOver
        cloned_game.currentAgent = cloned_game.allAgents[cloned_game.agentTurnIndex]

        cloned_game.p1Class = self.p1Class
        cloned_game.p2Class = self.p2Class
        cloned_game.winner = self.winner
        cloned_game.verbose = False
        cloned_game.nTurns = self.nTurns
        cloned_game.pgQueue = None
        
        return cloned_game

    def start(self):
        """Launch game user interface through pygame by starting pygame loop on a different thread"""
        if self.inclPygame:
            self.pygameThread = threading.Thread(target=self.pygameUI.pygameLoop)
            self.pygameThread.daemon = True
            self.pygameThread.start()
            while self.pygameUI.run == False:
                time.sleep(0.01)
        self.gameLoop()
        #self.queryAgentForMove()

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
            for unit in self.currentAgent.team:
                if unit.Avail:
                    changeTurnAgent = False
                    break
            self.gameOverCheck()
            executedTurnStillActive = ~changeTurnAgent
            if changeTurnAgent:
                for unit in self.currentAgent.team: # Reset availability for next time that agent is up for turn
                    if unit.Alive:
                        unit.resetForEndTurn()
                self.agentTurnIndex ^= 1    
                self.currentAgent = self.allAgents[self.agentTurnIndex]       
                self.gameOverCheck()
            return executedTurnStillActive

    def gameOverCheck(self):
        """Check if the game is over- if so, assign winner"""
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
        
    def terminateGameLoop(self):
        #This is just to get past the waiting for input portion in the game loop
        if self.pgQueue is not None:
            self.pgQueue.put(None) 
        self.gameLoopComplete = True
        
    def quit(self):
        """Quit and return winner. If pygame, then join thread."""
        self.gameOver = True
        if self.inclPygame:
            self.pygameUI.quit()
            time.sleep(0.01)
            del self.pygameUI
            try:
                self.pygameThread.join()
            except:
                pass
        self.terminateGameLoop()
        if self.winner is not None:
            return self.winner
        
        
    def gameLoop(self):
        """Alternate querying agents for turn"""
        
        while self.gameOver is False:
            self.currentAgent = self.allAgents[self.agentTurnIndex]
            self.fprint(f"\n-------- {self.currentAgent.name}'s turn --------")
            currentTurnActive= True
            while currentTurnActive:
                if self.gameOver:
                    break
                actionSpace = self.getCurrentStateActions(self)
                action = self.currentAgent.selectAction(self, actionSpace, 'gameLoop')
                if action is None:
                    break
                currentTurnActive = self.executeMove(action)
            currentTurnActive = True

        while self.gameLoopComplete == False:
            time.sleep(0.01)
        print("Game Loop Complete!")



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
        """ For the current state, returns action space. Action Format: (unitID, type, info) """

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
            actionSpace.append((curUnit.ID, 'ability', (-1, None)))
        return actionSpace

    def disposeUnit(self, unitToDispose):
        posessingAgent = self.allAgents[unitToDispose.agentIndex]
        team = posessingAgent.team
        allUnits = dict(self.allUnits)
        del allUnits[unitToDispose.ID] 
        self.allUnits = allUnits

        for unit in team:
            if unit.ID == unitToDispose.ID:
                team.remove(unit)
                if unitToDispose.sprite is not None:
                    self.pygameUI.spriteGroup.remove(unit.sprite)
                self.board.units_map[unit.position[0], unit.position[1]] = 0
                self.fprint(f"{unit.ID} is disposed")

    def __hash__(self):
        return hash(tuple(self.constructCompVars()))
    
    def __eq__(self, other):
        if isinstance(other, GameManager):
            for unit in self.allUnits.values():
                compUnit = other.allUnits.get(unit.ID, None)
                if compUnit is None:
                    return False
                else:
                    if compUnit != unit:
                        return False
            if self.board != other.board:
                return False
        return True
       
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
    def initializeTeams(self, teamComp):
        agentIndex = 0
        unitIndex = 1
        teams = []
        for team in teamComp:
            curTeam = []
            for entry in team:
                x, y, unitClass = entry
                newUnit = unitClass(agentIndex, unitIndex, (x, y))
                curTeam.append(newUnit)
                if self.pygameUI:
                    self.pygameUI.spriteGroup.add(newUnit.sprite)
                unitIndex+=1
                self.board.units_map[x, y] = newUnit.ID
                self.allUnits[newUnit.ID] = newUnit
            agentIndex+=1
            teams.append(curTeam)
        self.allUnits = Map(self.allUnits)
        self.p1 = self.p1Class('P1', 0, teams[0])
        self.p2 = self.p2Class('P2', 1, teams[1])


if __name__ == '__main__':
    # team1 = [(3, 3, u.meleeUnit),
    #         (0, 1, u.rangedUnit)]
    # team2 =  [(6,6, u.meleeUnit),
    #         (6, 7, u.rangedUnit)]
    
    team1 = [(5, 5, u.meleeUnit), (5, 6, u.meleeUnit)]
    team2 =  [(6,6, u.meleeUnit),]

    teamComp = [team1, team2]
    a = GameManager(ac.HumanAgent, ac.RandomAgent, teamComp, inclPygame = True, seed=10)
    b = a.clone()
    a.start()
   
    # b.start()