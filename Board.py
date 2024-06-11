import pygame
import random
import numpy as np

import matplotlib.pyplot as plt

import GameObjectTree as got
# from skimage.morphology import disk
import queue
import SpriteClasses as sc
import GameObjectDict as god
import Units as u
import GameObjects as go
import RunPygame as rp
import config
import copy
import eventClasses as e
import noiseMaps as maps
from immutables import Map
import immutables  as im

class UnitsMap:
    def __init__(self, maxY, maxX, board):
        self.board = board
        self.map = [[None for _ in range(maxX)] for _ in range(maxY)]

    def clone(self):
        cloned_UM = UnitsMap.__new__(UnitsMap)
        cloned_UM.map = copy.deepcopy(self.map)
        return cloned_UM
        


class Board:
    defaultMinPoint = (0,0)
    GOT = None
    gameObjectDict = None
    instUM = None
    instZM = None
    instOM = None

    def __init__(self, maxY, maxX, game, pygame = None):
        self.maxY = maxY
        self.maxX = maxX
        self.maxPoint = (maxX, maxY)
        self.game = game
        self.bPygame = pygame
        # self.allElemPositions = set()
        # self.allSeedPositions = set()
        self.dispatcher = e.EventDispatcher(self)
        self.units_map = np.zeros([maxX, maxY])
        row_indices, col_indices = np.meshgrid(np.arange(self.maxX), np.arange(self.maxY), indexing='ij')
        self.coord_map = np.stack((row_indices, col_indices), axis=-1)

        # self.initializeUMap()
        # self.initializeGameObjectTree()
        # self.initializeObjectDict()
        # self.initializeZMap()
        # self.initializeOMap()

    def clone(self, game):
        cloned_board = Board.__new__(Board)
        cloned_board.maxX = self.maxY
        cloned_board.maxY = self.maxX
        cloned_board.game = game
        # cloned_board.dispatcher = e.EventDispatcher(cloned_board)
        # cloned_board.dispatcher.board = cloned_board
        cloned_board.instUM = self.instUM.clone()
        cloned_board.instUM.board = cloned_board
        # cloned_board.instUM.assignListeners(cloned_board.dispatcher)
        cloned_board.bPygame = False
        cloned_board.GOT = copy.deepcopy(self.GOT)
        cloned_board.GOT.board = cloned_board
        # cloned_board.GOT.addListeners(cloned_board.dispatcher)
        cloned_board.gameObjectDict = copy.deepcopy(self.gameObjectDict)
        # cloned_board.gameObjectDict.addListeners(cloned_board.dispatcher)


        cloned_board.instZM = copy.deepcopy(self.instZM)
        cloned_board.instZM.board = cloned_board
        # cloned_board.instZM.assignListeners(cloned_board.dispatcher)

        cloned_board.instOM = self.instOM.clone()
        cloned_board.instOM.board = cloned_board
        cloned_board.instOM.GOT = cloned_board.GOT
        return cloned_board

    def __deepcopy__(self, memo):
        return None
    def createDummyGameObjects(self):
        dummyObjects = []
        IDs = ['a']
        pos = (10, 10)
        temp = sc.Sprites()
        for ID in IDs:
            if self.bPygame:
                image = temp.spritesDictScaled["Charlie"]
                dummyObjects.append(go.Rapture(ID, pos, 0, image))
            else:
                dummyObjects.append(go.Rapture(ID, pos, 0))
        return dummyObjects

    def initializeGameObjectTree(self):
        self.GOT = got.GameObjectTree(self.defaultMinPoint, self.maxPoint, self)
        # self.GOT.addListeners(self.dispatcher)       

    def initializeObjectDict(self):
        self.gameObjectDict= god.GameObjectDict(self)
        # self.gameObjectDict.addListeners(self.dispatcher)
        return
        # dummyGOs = self.createDummyGameObjects()
        # for go in dummyGOs:
        #     self.gameObjectDict.insert(go)
        # if self.bPygame:
        #     for go in self.gameObjectDict.getAllGOs():
        #         pass
        #         self.bPygame.spriteGroup.add(go.sprite)

    def initializeUMap(self):
        self.instUM = UnitsMap(self.maxY, self.maxX, self)
        # self.instUM.assignListeners(self.dispatcher)
        
    def initializeUnits(self, teamComp):
        agentIndex = 0
        unitIndex = 1
        teams = []
        for team in teamComp:
            curTeam = []
            for entry in team:
                spawnLocation, unitClass = entry
                newUnit = unitClass(agentIndex, unitIndex, spawnLocation, self, self.game)
                curTeam.append(newUnit)
                if self.bPygame:
                    self.bPygame.spriteGroup.add(newUnit.sprite)
                unitIndex+=1
                self.units_map[spawnLocation[0], spawnLocation[1]] = newUnit.ID
            agentIndex+=1
            teams.append(curTeam)
        # self.drawMap(self.instUM.map)
        return (teams[0], teams[1])

    def initializeNoise(self):
        self.noise = maps.Noise(self.maxY, self.maxX)

    def initializeZMap(self):
        self.instZM = maps.ZMap(self.maxY, self.maxX, self)
        # self.instZM.assignListeners(self.dispatcher)
        self.zMap = self.instZM.map
        # self.drawMap(self.zMap)

    def initializeOMap(self):
        self.instOM = maps.OMap(self.maxY, self.maxX, self, self.GOT)
        # self.drawMap(self.instOM.map)


        
    def getValidMoveTargets(self, center):
        x, y = center

        # Check if there are any units in adjacent tiles
        xBounds = (np.max([0, x-1]), np.min([x + 2, self.maxX]))
        yBounds = (np.max([0, y-1]), np.min([y + 2, self.maxY]))
        coord_map_adj = self.coord_map[xBounds[0]:xBounds[1], yBounds[0]:yBounds[1]]
        unit_map_adj = self.units_map[xBounds[0]:xBounds[1], yBounds[0]:yBounds[1]]
        dirs = coord_map_adj[unit_map_adj == 0]
        
        return dirs
    

    
    def getUnitsInRadius(self, center, radius, excludeUnit=None):
        x, y = center

        # Check if there are any units in adjacent tiles
        xBounds = (np.max([0, x-radius]), np.min([x + radius+1, self.maxX]))
        yBounds = (np.max([0, y-radius]), np.min([y + radius+1, self.maxY]))
        unit_map_adj = self.units_map[xBounds[0]:xBounds[1], yBounds[0]:yBounds[1]]
        units = unit_map_adj[unit_map_adj != 0]
        if excludeUnit is not None:
            units = units[units != excludeUnit]
        return units
    def getValidAbilities(self, unit):
        validAbilities = []
        candidateAbilityClasses = unit.unitAbilities
        for abilityClass in candidateAbilityClasses:
            ability = abilityClass(unit)
            # candidateIDs = self.getUnitsInRadius(unit.position, ability.range)
            candidateIDs = self.getUnitsInRadius(unit.position, ability.range, unit.ID)
            for ID in candidateIDs:
                candidate = self.game.allUnits[ID]
                if ability.targeted:
                    ability.setTarget(candidate)
                    if ability.isValidToCast(self):
                        validAbilities.append((abilityClass, candidate.ID))
                else:
                    if ability.isValidToCast(self): 
                        validAbilities.append(abilityClass, None)
        validAbilities.append((-1, None))
        return validAbilities

    
    def updateBoard(self, actionTuple):
        unitID, actionType, info = actionTuple
        if actionType == "move":
            self.processMove(actionTuple)
        if actionType == "ability":
            self.processAbility(actionTuple)

    def processMove(self, actionTuple):
        unitID, _, info = actionTuple
        unit = self.game.allUnits[unitID]
        initialPosition = unit.position
        finalPosition = info
        self.units_map[initialPosition[0], initialPosition[1]] = 0 # (Y, X) format
        self.units_map[finalPosition[0], finalPosition[1]] = unitID
        unit.position = finalPosition

        if self.bPygame:
            unit.sprite.rect.topleft = unit.sprite.convertToRect(finalPosition)
        unit.currentMovement -= 1

        if unit.currentMovement == 0:
            unit.canMove = False

        # GOs = self.gameObjectDict.query(destination[1])
        # for go in GOs:
        #     go.invoke(entity, self.game)
        # self.drawMap(self.instUM.map)

    def processAbility(self, actionTuple):
        unitID, actionType, info = actionTuple
        abilityClass, target = info
        unit = self.game.allUnits[unitID]
        if abilityClass == -1:
            #-1 is code for end turn
            unit.Avail = False
        else:
            ability = abilityClass(unit)
            if target is not None:
                ability.setTarget(target)
            ability.activate()
        

        
    def drawMap(self, map):
            # cMap = plt.cm.terrain
            # coloredZMap = cMap(map)
            if isinstance(map, np.ndarray):
                for y in range(len(map)):
                    rowToPrint = ''
                    for x in range(len(map[y])):
                        if map[y][x] == None:
                            rowToPrint += '{: ^3}'.format(".")    
                        else:
                            rowToPrint += '{: ^3}'.format(f"{map[y][x]}")
                    self.game.fprint(rowToPrint)
            else:
                for y in range(len(map)):
                    rowToPrint = ''
                    for x in range(len(map[y])):
                        if map[y][x] == None:
                            rowToPrint += '{: ^3}'.format(".")    
                        else:
                            rowToPrint += '{: ^3}'.format(f"{map[y][x].ID}")
                    self.game.fprint(rowToPrint)
            
            # im = plt.imshow(coloredZMap, cmap = cMap)
            # fig = plt.gcf()
            # fig.colorbar(im)
            # plt.show()


