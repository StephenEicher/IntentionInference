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


        # if self.bPygame:
        #     p1a = u.meleeUnit(0, 1, (0,0), self, self.game)
        #     self.bPygame.spriteGroup.add(p1a.sprite)
        #     p1b = u.rangedUnit(0, 2, (0,1), self, self.game)
        #     self.bPygame.spriteGroup.add(p1b.sprite)
        #     p2a = u.meleeUnit(1, 3, (1,0), self, self.game)
        #     self.bPygame.spriteGroup.add(p2a.sprite)
        #     p2b = u.rangedUnit(1, 4, (1,1), self, self.game)
        #     self.bPygame.spriteGroup.add(p2b.sprite)
        #     print(f"p2a rect: {p2a.sprite.rect.topleft}")
        #     print(f"p2b rect: {p2b.sprite.rect.topleft}")
        # else:

        # self.instUM.map[0][0] = p1a
        # self.instUM.map[0][1] = p1b
        # self.instUM.map[1][0] = p2a
        # self.instUM.map[1][1] = p2b

        

        # return [p1a, p1b, p2a, p2b]

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

    def getAdjDirections(self, unit):
        unitY, unitX = unit.position
        adjPositions = { 
            "NW": (unitY - 1, unitX - 1),
            "N": (unitY - 1, unitX),
            "NE": (unitY - 1, unitX + 1),
            "E": (unitY, unitX + 1),
            "SE": (unitY + 1, unitX + 1),
            "S": (unitY + 1, unitX),
            "SW": (unitY + 1, unitX - 1),
            "W": (unitY, unitX - 1)
        }

        return self.filterValidDirections(adjPositions)   
        
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

    

    def rayCast(self, origin, target, castingUnit, targetUnit, gameObjectTree, unitsMap, zMap):
        
        line = self.bresenhamLine(origin, target)

        # Define query box size which captures line (quadtree order of axes is X, Y not Y, X)
        queryBoxMin = ()
        queryBoxMax = ()
        queryBoxStartX, initStartY = line[0]
        queryBoxEndX, initEndY = line[-1]

        # Convert numpy Y value to quadtree Y value
        queryBoxStartY = unitsMap.shape[0] - 1 - initStartY
        queryBoxEndY = unitsMap.shape[0] - 1 - initEndY

        len = queryBoxEndX - queryBoxStartX
        wid = queryBoxEndY - queryBoxStartY

        if len < 0 and wid < 0:
            queryBoxMin = (line[-1])
            queryBoxMax = (line[0])

        if len < 0:
            queryBoxMin = (queryBoxEndX, queryBoxStartY)
            queryBoxMax = (queryBoxStartX, queryBoxEndY)

        if wid < 0:
            queryBoxMin = (queryBoxStartX, queryBoxEndY)
            queryBoxMax = (queryBoxEndX, queryBoxStartY)

        # Return ALL gameObjectStacks found in that box 
        allGameObjectStacks = gameObjectTree.querySpace(queryBoxMin, queryBoxMax)

        # Include gameObjectStacks which fall on a point in the line
        lineStacks = {}
        for stack in allGameObjectStacks:
            if stack[0].position in line:
                lineStacks[stack[0].position] = stack

        # Get overall height of GameObjects on each point
        newLineStacks = {}
        totalGameObjectsZ = 0
        for position, stack in lineStacks.items():
            for gameObject in stack:
                totalGameObjectsZ += gameObject.height
            newLineStacks[position] = totalGameObjectsZ

        for point in line:
            y, x =  point

            # Check if other Units in line
            if unitsMap[y, x] is not None:
                return False
            
            # Combine totalGameObjectsZ with zMap values
            z = zMap[y, x]
            effectiveZ = z + newLineStacks[y, x]
            if targetUnit.height > castingUnit.height:
                targetUnit.height - castingUnit.height < effectiveZ
                return False
            if targetUnit.height < castingUnit.height:    
                castingUnit.height - targetUnit.height < effectiveZ
                return False
        
        # If no units found, or view obstructed by terrain or obstacles with clearance of target in mind, return True for clear LOS
        return True

    def bresenhamLine(start, end):
        # Bresenham's line algorithm to return a list of points from start to end
        points = []
        x1, y1 = start
        x2, y2 = end
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = -1 if x1 > x2 else 1
        sy = -1 if y1 > y2 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                points.append((y, x))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                points.append((y, x))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        points.append((y2, x2))

        return points

    def updateBoard(self, selectedUnit, actionDict):
        if actionDict.get("type") == "move":
            self.move(selectedUnit, actionDict["directionDict"])
        if actionDict.get("type") == "castAbility":
            if actionDict['abilityDict'].get("name") == "End Unit Turn":
                selectedUnit.Avail = False
                return
            else:
                self.cast(selectedUnit, actionDict["abilityDict"])

    def move(self, entity, dict):
            if isinstance(entity, u.Unit):
                destination = list(dict.keys())
                destination = destination[0]
                self.instUM.map[destination[1][0]][destination[1][1]] = self.instUM.map[entity.position[0]][entity.position[1]] # (Y, X) format
                self.instUM.map[entity.position[0]][entity.position[1]] = None
                entity.position = (destination[1][0], destination[1][1])

                if self.bPygame:
                    entity.sprite.rect.topleft = entity.sprite.convertToRect((destination[1][0], destination[1][1]))
                entity.currentMovement -= 1

                if entity.currentMovement == 0:
                    entity.canMove = False

                GOs = self.gameObjectDict.query(destination[1])
                for go in GOs:
                    go.invoke(entity, self.game)
                

            self.drawMap(self.instUM.map)

    def cast(self, entity, ability):
        targetType = ability["events"][0].get("target")
        if targetType == "targetunit":
            #castTarget = self.game.currentAgent.selectTarget(ability)
            castTargetID = ability["targetedUnit"]
            castTarget = self.game.getUnitByID(castTargetID)
        for event in ability.get("events"):
            for k, v in event.items():
                if v == "changeHP":
                    castTarget.currentHP += event["value"]
                    castTarget.currentHP = np.min([castTarget.currentHP, castTarget.HP])


                if v == "displace":
                    displaceDistance = event.get("distance")
                    castTarget.currentMomentum = displaceDistance * castTarget.massConstant
                    event = eDisplace(entity, castTarget, displaceDistance)
                    self.dispatcher.dispatch(event)

                    castTarget.position = event["value"]


                if v == "changeActionPoints":
                    entity.currentActionPoints += event["value"]
                if v == "changeMaxActionPoints":
                    delta = event["value"]
                    entity.actionPoints += delta
                if v == "changeMovement":
                    delta = event["value"]
                    entity.actionPoints += delta
        
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

    def filterValidDirections(self, directions):
        """Filter and return only valid directions within the grid bounds."""
        validDirections = {}
        for direction, (y, x) in directions.items():
            # Check if the coordinates are within the grid bounds
            if 0 <= y < self.maxY and 0 <= x < self.maxX:
                validDirections[direction] = (y, x)
        return validDirections


