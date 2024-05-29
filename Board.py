import pygame
import random
import numpy as np
from  opensimplex import OpenSimplex
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, zoom
import GameObjectTree as got
# from skimage.morphology import disk
import queue
import SpriteClasses as sc

import Units as u
import GameObjects as go
import RunPygame as rp
import config

class UnitsMap:
    def __init__(self, maxY, maxX, board):
        self.board = board
        self.map = [[None for _ in range(maxX)] for _ in range(maxY)]

    def UMhandleEvent(self, event):
        if isinstance(event, eMove):
            adjUnits = {}
            adjUnits[(event.unit.position[0], event.unit.position[1])] = event.unit
            for direction, (adjY, adjX) in self.board.getAdjDirections(event.unit).items():
                # Check if the adjacent position is within bounds of the map
                if 0 <= adjY < len(self.map) and 0 <= adjX < len(self.map):
                    adjUnit = self.map[adjY][adjX]

                    if isinstance(adjUnit, u.Unit):
                        adjUnits[(direction, (adjY, adjX))] = adjUnit
                        
            return adjUnits

        if isinstance(event, eMeleeTargets):
            targets = []
            for direction, (adjY, adjX) in self.board.getAdjDirections(event.unit).items():
                    adjUnit = self.map[adjY][adjX]
                    if isinstance(adjUnit, u.Unit):
                        targets.append(adjUnit)

            return targets

        if isinstance(event, eTargetsInRange):
            targets = []
            rowBounds = np.array([event.unit.position[0] - event.range, event.unit.position[0] + event.range])
            colBounds = np.array([event.unit.position[1] - event.range, event.unit.position[1] + event.range])
            rowBounds = np.clip(rowBounds, 0, len(self.map)-1)
            colBounds = np.clip(colBounds, 0, len(self.map)-1)
            #xMax = self.unit.position[0] + self.range
            tilesToCheck = []
            for row in np.arange(rowBounds[0], rowBounds[1]+1):
                for col in np.arange(colBounds[0], colBounds[1]+1):
                    tilesToCheck.append(self.map[row][col]) # already appends all objects found at coordinates and excludes empty tiles

            for unit in tilesToCheck:
                if isinstance(unit, u.Unit):
                    if unit.ID is not event.unit.ID and unit.agentIndex is not event.unit.agentIndex:
                        if unit.position[0] == event.unit.position[0] or unit.position[1] == event.unit.position[1]:
                            if abs(unit.position[0] - event.unit.position[0]) <= event.range or abs(unit.position[1] - event.unit.position[1]) <= event.range:
                                targets.append(unit)
           
            self.board.GOT.incomingUM.put(targets)
            
            # unitsAndPaths = {}
            # for unit in tilesToCheck:
            #     path = []
            #     if isinstance(unit, u.Unit):
            #         if unit.ID is not event.unit.ID and unit.agentIndex is not event.unit.agentIndex:
            #             if unit.position[0] == event.unit.position[0]:
            #                 for col in range(event.position[1], unit.position[1]): # No need to include the potential target unit's position in the path
            #                     tile = (unit.position[0], col)
            #                     path.append(tile)
            #             elif unit.position[1] == event.unit.position[1]:
            #                 for row in range(event.position[0], unit.position[0]): # No need to include the potential target unit's position in the path
            #                     tile = (row, unit.position[1])
            #                     path.append(tile)
            #             unitsAndPaths[unit] = path
            
            return None # refer to GOT's response for final list of viable targets

class Noise:
    def __init__(self, maxY, maxX):
        self.maxY = maxY
        self.maxX = maxX

    def genNoise(self, scales, amplis, minZ, maxZ):
        simplex = OpenSimplex(random.randint(0,10000000))
        noiseMap = np.zeros((self.maxY, self.maxX))

        # Generate noise for the left triangular half of the grid (grid split across main diagonal)
        s = scales
        a = amplis
        for y in range(self.maxY):
            for x in range(self.maxX):
                if y - x > 0:
                    noise = simplex.noise2(x * s, y * s) * a
                    noiseMap[y, x] += noise

        # Calculate minimum noise value in the noiseMap
        minNoise = noiseMap.min()
        # Shift the entire noiseMap up by adding the absolute of the minimum value to exclude negative values
        noiseMap += abs(minNoise)

        # Mirror the lower half of the left triangular half across the center of grid
        for y in range(self.maxY):
            for x in range(self.maxX):
                if y > x and y + x >= self.maxY - 1:  # Points within lower half of left triangular half
                    newY = self.maxY - y - 1
                    newX = self.maxX - x - 1
                    noiseMap[newY, newX] = noiseMap[y, x]
        
        # Mirror the upper half of the left triangular half across center of grid
        for y in range(self.maxY):
            for x in range(self.maxX):
                if y > x and y + x <= self.maxY - 1: # Points within upper half of left triangular half
                    newY = self.maxY - y - 1
                    newX = self.maxX - x - 1
                    noiseMap[newY, newX] = noiseMap[y, x]
 
        self.smoothen(noiseMap)
                    
        # Normalize the mirrored map
        noiseMapNormalized = (noiseMap - noiseMap.min()) #Make smallest value 0
        noiseMapNormalized = noiseMapNormalized/ noiseMapNormalized.max() #Scale all values from 0 to 1
        # print(f"minZ = {noiseMap.min()} maxZ = {noiseMap.max()}")
        scaledNoiseMapFloat = noiseMapNormalized * (maxZ - minZ)
        scaledNoiseMapInt = np.round(scaledNoiseMapFloat).astype(int)
        # borderWidth = 3

        # for y in range(self.maxY):
        #     for x in range(self.maxX):
        #         # Calculate the distance from the diagonal and antidiagonal lines
        #         distFromDiag = abs(y - x)
        #         distFromAntidiag = abs((y + x) - (self.maxY - 1))
                
        #         # Check if the point is within the border width of the diagonal or antidiagonal lines
        #         if (
        #             distFromDiag <= borderWidth or
        #             distFromAntidiag <= borderWidth
        #         ):
        #             # Set the value to zero to create a border zone
        #             scaledNoiseMapInt[y, x] = 0

        return [scaledNoiseMapInt, noiseMapNormalized]

    def smoothen(self, map):
        # GENERALIZE FUNCTION SO AS TO MASK -> THRESHOLD -> SMOOTHEN
        # Create a mask that includes the seam and adjacent tiles up to a certain distance (seam_width)
        mask = np.zeros_like(map, dtype=bool)
        length = len(map)
        
        sigma = 1
        seamWidth = 1

        # Define the area around the seam
        for i in range(length):
            # Apply the mask along the main diagonal and its adjacent tiles up to seam_width
            for j in range(max(0, i - seamWidth), min(length, i + seamWidth + 1)):
                mask[i, j] = True
                mask[j, i] = True  # Add adjacent tiles along the diagonal
        
        # Apply Gaussian blur to the entire map
        blurredMap = gaussian_filter(map, sigma=sigma)
        
        # Blend the blurred map back into the original map using the mask
        map[mask] = blurredMap[mask]
        
        return map

class ZMap(Noise):
    def __init__(self, maxY, maxX, board):
        super().__init__(maxY, maxX)
        self.board = board
        comboMap = self.genNoise(0.1, 1, 0, 0)
        self.map = comboMap[0]

    def ZMhandleEvent(self, event):
        if isinstance(event, eMove):

            adjZs = {}
            for direction, (adjY, adjX) in self.board.getAdjDirections(event.unit).items():
                adjZ = self.map[adjY, adjX]
                unitZ = self.map[event.unit.position[0], event.unit.position[1]]

                adjZs[(event.unit.position[0], event.unit.position[1])] = unitZ
                adjZs[(direction, (adjY, adjX))] = adjZ

            return adjZs
        
    def applyMasks(self, map, mask):
        yScale = self.maxY/10
        xScale = self.maxX/10
        
        masks = {
        "twirl" :  [[1,0,0,0,0,0,0,0,0,0],
                    [1,0,0,0,0,0,0,0,0,0],
                    [0,1,0,0,0,0,0,0,0,0],
                    [0,0,1,0,1,1,0,0,0,0],
                    [0,0,0,1,0,0,1,0,0,0],
                    [0,0,0,1,0,0,1,0,0,0],
                    [0,0,0,0,1,1,0,1,0,0],
                    [0,0,0,0,0,0,0,0,1,0],
                    [0,0,0,0,0,0,0,0,0,1],
                    [0,0,0,0,0,0,0,0,0,1]],
        "ravine" : [[0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0]],
        "woods" :  [[0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0]],
        "delta" :  [[0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0]]
        }

        selectedMask = masks.get("twirl")
        scaledMask = zoom(selectedMask, (yScale, xScale), order = 0)

    
    def applyThresholds(self, type):
        thresholds = {
            "erode" : [],
            "makepeaks" : [],
            "flatten" : [],
            "fracture" : []                
        }

class OMap(Noise):
    def __init__(self, maxY, maxX, board, GOT):
        super().__init__(maxY, maxX)
        self.board = board
        self.GOT = GOT
        
        comboMap = self.genNoise(0.5, 0.1, 0, 2)
        self.map = comboMap[0]
        self.map[self.map < 2] = 0
        self.map[self.map == 2] = 1 # Convert to bool
        self.createObstacles(self.map)

    def createObstacles(self, map): # Should this function exist on the class or should the board pass the instance to the GameObjectTree?
        coordArrays = np.where(map)
        rows, cols = coordArrays
        obstacleCoords = list(zip(rows, cols))
        temp = sc.Sprites()
        for i in range(len(obstacleCoords)):
            row, col = obstacleCoords[i]
            newObstacle = go.Obstacles(None, (row, col), 1, temp.spritesDictScaled["obstacle"])
            self.board.bPygame.obstacleGroup.add(newObstacle.sprite)
            self.GOT.insert(newObstacle)

class EventDispatcher:
    def __init__(self, board):
        self.board = board
        self.genericListeners = {}
        self.indexedListeners = {}
        self.orderSensitiveEvents = []

    def addListener(self, event, listener, index = None, allListenersAdded = False):
        listenerEstablished = False
        if index:
            if event not in self.orderSensitiveEvents:
                self.orderSensitiveEvents.append(event)
                self.indexedListeners[event] = []
            self.indexedListeners.get(event).append((listener, index))

            if allListenersAdded:
                self.indexedListeners.get(event).sort(key=lambda x: x[1]) # During initialization after all listeners have been added, reorganize the listeners according to their indices
                return True
            
            return True
            
        if event not in self.genericListeners:
            self.genericListeners[event] = []
        
        list = self.genericListeners.get(event)
        list.append(listener)

    def dispatch(self, event):
        eventType = type(event)
        responseList = []

        if eventType in self.genericListeners:
            for listener in self.genericListeners[eventType]:
                listenerName = listener.__name__
                response = listener(event)
                # self.board.manageScreen(None, None, response)
                listenerTuple = (listenerName, response)
                responseList.append(listenerTuple)

        else:
            for listener, _ in self.indexedListeners[eventType]:
                listenerName = listener.__name__
                response = listener(event)
                # self.board.manageScreen(None, None, response)
                listenerTuple = (listenerName, response)
                responseList.append(listenerTuple)

        return responseList

class eMove:
    def __init__(self, unit, minPoint, maxPoint):
        self.unit = unit
        self.minPoint = minPoint
        self.maxPoint = maxPoint

class eMeleeTargets:
    def __init__(self, unit):
        self.unit = unit

class eTargetsInRange:
    def __init__(self, unit, abilityRange):
        self.unit = unit
        self.checkUnit = None
        self.range = abilityRange
        self.minPoint = None
        self.maxPoint = None

class eRangeTargets:
    def __init__(self, unit):
        self.unit = unit

class Board:
    defaultMinPoint = (0,0)

    def __init__(self, maxY, maxX, game, pygame = None):
        self.maxY = maxY
        self.maxX = maxX
        self.maxPoint = (maxX, maxY)
        self.game = game
        self.bPygame = pygame
        # self.allElemPositions = set()
        # self.allSeedPositions = set()
        self.dispatcher = EventDispatcher(self)
        self.initializeObjectTree()
        self.initializeObjectDict()
        self.initializeZMap()
        self.initializeOMap()

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

    def initializeObjectTree(self):
        self.GOT = got.GameObjectTree(self.defaultMinPoint, self.maxPoint, self)
        self.dispatcher.addListener(eMove, self.GOT.GOThandleEvent)
        self.dispatcher.addListener(eTargetsInRange, self.GOT.GOThandleEvent, 2)

    def initializeObjectDict(self):
        self.gameObjectDict= GameObjectDict(self)
        self.dispatcher.addListener(eMove, self.gameObjectDict.GODhandleEvent)
        dummyGOs = self.createDummyGameObjects()
        for go in dummyGOs:
            self.gameObjectDict.insert(go)
        if self.bPygame:
            for go in self.gameObjectDict.getAllGOs():
                pass
                self.bPygame.spriteGroup.add(go.sprite)


    def initializeUnits(self):
        self.instUM = UnitsMap(self.maxY, self.maxX, self)
        self.dispatcher.addListener(eMove, self.instUM.UMhandleEvent)
        self.dispatcher.addListener(eMeleeTargets, self.instUM.UMhandleEvent)
        self.dispatcher.addListener(eRangeTargets, self.instUM.UMhandleEvent)
        self.dispatcher.addListener(eTargetsInRange, self.instUM.UMhandleEvent, 1, True)
        self.unitsMap = self.instUM.map

        if self.bPygame:
            p1a = u.meleeUnit(0, 1, (0,0), self, self.game)
            self.bPygame.spriteGroup.add(p1a.sprite)
            p1b = u.rangedUnit(0, 2, (0,1), self, self.game)
            self.bPygame.spriteGroup.add(p1b.sprite)
            p2a = u.meleeUnit(1, 3, (1,0), self, self.game)
            self.bPygame.spriteGroup.add(p2a.sprite)
            p2b = u.rangedUnit(1, 4, (1,1), self, self.game)
            self.bPygame.spriteGroup.add(p2b.sprite)
            print(f"p2a rect: {p2a.sprite.rect.topleft}")
            print(f"p2b rect: {p2b.sprite.rect.topleft}")

        self.unitsMap[0][0] = p1a
        self.unitsMap[0][1] = p1b
        self.unitsMap[1][0] = p2a
        self.unitsMap[1][1] = p2b

        self.drawMap(self.unitsMap)

        return [p1a, p1b, p2a, p2b]

    def initializeNoise(self):
        self.noise = Noise(self.maxY, self.maxX)

    def initializeZMap(self):
        self.instZM = ZMap(self.maxY, self.maxX, self)
        self.dispatcher.addListener(eMove, self.instZM.ZMhandleEvent)
        self.zMap = self.instZM.map
        # self.drawMap(self.zMap)

    def initializeOMap(self):
        self.instOM = OMap(self.maxY, self.maxX, self, self.GOT)
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

    def getValidDirections(self, unit):
        validAdjPositions = self.getAdjDirections(unit)

        GOY = len(self.unitsMap) - 1 - unit.position[0]
        UX = unit.position[1]

        # Initialize minPoint to the desired values
        minPointX = max(UX - 1, 0)  # Ensure minPointX is at least 0
        minPointY = max(GOY - 1, 0)  # Ensure minPointY is at least 0

        # Set minPoint based on computed values
        minPoint = (minPointX, minPointY)

        # Set maxPoint
        maxPointX = minPointX + 2
        maxPointY = minPointY + 2  # maxPoint is calculated based on a 3x3 region

        if maxPointX > (len(self.unitsMap) - 1):
            maxPointX = self.maxX
        
        if maxPointY > (len(self.unitsMap) - 1):
            maxPointY = self.maxY

        maxPoint = (maxPointX, maxPointY)

        moveEvent = eMove(unit, minPoint, maxPoint)
        
        listenerResponses = self.dispatcher.dispatch(moveEvent)
        # A list of tuples (listener name, its response)
        # Each response always occurs in the same order in the list:
            # Within UnitsMap response: dictionary
                # first key is unit's position as a tuple and its value is the unit object
                # remaining keys are tuples containing the direction string, position tuple and their values are the adjacent unit object if any
            # Within ZMap response: dictionary 
                # first key is unit's position as a tuple and its value is the z value the unit is standing on 
                # remaining keys are tuples containing the direction string, position tuple and their value are the z value of that adjacent spot
            # Within GameObjectTree response: list of dictionaries
                # each dictionary contains keys "direction," "position," "stack," "stackZ," and "surfaces"
                # first 2 self-explanatory
                # key "stack"'s value is the stack of GameObjects for a given position
                # key "stackZ"'s value is the int total height (z) of the stack
                # key "surfaces"'s value is the list of surface GameObjects for a given position
  
        # Unpack listenerResponses
        #gameObjectTreeR = listenerResponses[0][1]
        gameObjectTreeR = listenerResponses[0][1]

        zMapR = listenerResponses[2][1]

        unitsMapR = listenerResponses[3][1]

        takeFallDamage = False
        addSurfaces = []
        validDirections = {}
        flatValidDirections = []
        
        for direction, position in validAdjPositions.items():
    
            # Check if adjacent Unit exists
            if (direction, position) in unitsMapR:
                if unitsMapR[(direction, position)] is not None:
                    continue

            # Calculate elevation difference and check if it's too great, parse out gameObjectTreeR
            if gameObjectTreeR:
                for dict in gameObjectTreeR:
                    if position == dict.get("position"):
                        stackZ = dict.get("stackZ")
                        surfaces = dict.get("surfaces")
                        totalZ = zMapR[(direction, position)] + stackZ
                        if surfaces:
                            addSurfaces.append(surfaces)

                        unitZ = zMapR[unit.position]
                        break  # Break the loop once we have found and assigned totalZ and unitZ
                else:
                    # If we do not break the loop, it means no matching position was found
                    totalZ = zMapR[direction, position]
                    unitZ = zMapR[unit.position]
            else:
                totalZ = zMapR[direction, position]
                unitZ = zMapR[unit.position]

            if (totalZ - unitZ) > unit.jump:
                continue

            # If the position is valid, add it to the validDirections dictionary
            validDirections[(direction, position)] = (takeFallDamage, addSurfaces)
            flatValidDirections.append((unit, {"type" : "move", "directionDict" : {(direction, position) : (takeFallDamage, addSurfaces)}}))

        return validDirections, flatValidDirections
    
    def getValidAbilities(self, unit):
        unitAbilities = unit.unitAbilities
        # Access dictionary of class actions and their action points cost
        # Return all, but denote which are actually allowed by current action points
        # Highest level keys are 'name,''cost,' and 'events' which consists of type of events (dictionaries) involved in constructing the ability

        affordableAbilities = []
        validAbilities = []
        invalidAbilities = {}
        flatAbilities = []

        if unit.canAct is False:
            invalidAbilities=unitAbilities
            return (validAbilities, invalidAbilities, flatAbilities)

        for ability in unitAbilities:
            if ability.get("cost") <= unit.currentActionPoints:
                affordableAbilities.append(ability)
            if ability.get("cost") > unit.currentActionPoints:
                invalidAbilities[ability["name"]] = ability.get("cost")

        for ability in affordableAbilities:
            for event in ability.get("events"):
                
                if "target" in event:
                    if event.get("target") == "targetunit":
                        range = ability.get("range")
                        event = eTargetsInRange(unit, range)
                        responseList = self.dispatcher.dispatch(event)
                        viableTargets = responseList[1][1] # for first index: 0 for UMHandleEvent's response, 1 for ZMHandleEvent's response, 2 for GOTHandleEvent's response

                        if viableTargets:
                            validAbilities.append(ability)
                        if viableTargets is None:
                            invalidAbilities[ability["name"]] = ability.get("cost")

                        for target in viableTargets:
                            abilityWithTarget = dict(ability)
                            abilityWithTarget["targetedUnit"] = target
                            flatAbilities.append((unit, {"type" : "castAbility", "abilityDict" : abilityWithTarget}))
                else:
                    flatAbilities.append((unit, {"type" : "castAbility", "abilityDict" : ability}))

        for ability in affordableAbilities: # If affordable but no targeting required add to valid abilities
            if ability not in validAbilities and ability.get("range") == 0:
                validAbilities.append(ability)
                

        return (validAbilities, invalidAbilities, flatAbilities)
    

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
                self.unitsMap[destination[1][0]][destination[1][1]] = self.unitsMap[entity.position[0]][entity.position[1]] # (Y, X) format
                self.unitsMap[entity.position[0]][entity.position[1]] = None
                entity.position = (destination[1][0], destination[1][1])

                if self.bPygame:
                    entity.sprite.rect.topleft = entity.sprite.convertToRect((destination[1][0], destination[1][1]))
                    entity.currentMovement -= 1

                if entity.currentMovement == 0:
                    entity.canMove = False

                GOs = self.gameObjectDict.query(destination[1])
                for go in GOs:
                    go.invoke(entity, self.game)
                

            self.drawMap(self.unitsMap)

    def cast(self, entity, ability):
        targetType = ability["events"][0].get("target")
        if targetType == "targetunit":
            #castTarget = self.game.currentAgent.selectTarget(ability)
            castTarget = ability["targetedUnit"]

        for event in ability.get("events"):
            for k, v in event.items():
                if v == "changeHP":
                    castTarget.currentHP += event["value"]
                    castTarget.currentHP = np.min([castTarget.currentHP, castTarget.HP])
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
                    print(rowToPrint)
            else:
                for y in range(len(map)):
                    rowToPrint = ''
                    for x in range(len(map[y])):
                        if map[y][x] == None:
                            rowToPrint += '{: ^3}'.format(".")    
                        else:
                            rowToPrint += '{: ^3}'.format(f"{map[y][x].ID}")
                    print(rowToPrint)
            
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



class GameObjectDict:
    def __init__(self, board):
        self.GOmap = {}

    def insert(self, gameObject):
        if self.GOmap.get(gameObject.position, None) is None:
            self.GOmap[gameObject.position] = [gameObject]
        else:
            self.GOmap[gameObject.position].append(gameObject)

    def query(self, positions):
        if not isinstance(positions, list):
            positions = [positions]
        allObjs = []
        for position in positions:
            if self.GOmap.get(position, None) is not None:
                for entry in self.GOmap.get(position, None):
                    if entry is not None:
                        allObjs.append(entry)
        return allObjs
    def GODhandleEvent(self, event):
        if isinstance(event, eMove):

            
            pass
            
    def getAllGOs(self):
        allGOs = []
        for key in self.GOmap.keys():
            for go in self.GOmap[key]:
                if go is not None:
                    allGOs.append(go)
        return allGOs
    def removeGO(self, GO):
        key = GO.position
        if self.GOmap.get(key, None) is not None:
            self.GOmap[key].remove(GO)
            GO.deactivate()
