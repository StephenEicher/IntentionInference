import random
import numpy as np
from  opensimplex import OpenSimplex
import matplotlib.pyplot as plt

import Units as u
import GameObjects as go

class UnitsMap:
    def __init__(self, maxY, maxX, board):
        self.board = board
        self.map = [[None for _ in range(maxX)] for _ in range(maxY)]

    def UMhandleEvent(self, event):
        if isinstance(event, eMove):

            adjUnits = {}
            adjUnits[(event.unit.position[0], event.unit.position[1])] = event.unit
            for direction, (adjY, adjX) in self.board.validAdjPositions.items():
                # Check if the adjacent position is within bounds of the map
                if 0 <= adjY < len(self.map) and 0 <= adjX < len(self.map):
                    adjUnit = self.map[adjY][adjX]
                                    
                    if isinstance(adjUnit, u.Unit):
                        adjUnits[(direction, (adjY, adjX))] = adjUnit

            return adjUnits

class Noise:
    def __init__(self, maxY, maxX):
        self.maxY = maxY
        self.maxX = maxX

    def genNoise(self, scales, amplis):
        simplex = OpenSimplex(seed = 0)
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
                if y > x and y + x > self.maxY - 1:  # Points within lower half of left triangular half
                    newY = self.maxY - y - 1
                    newX = self.maxX - x - 1
                    noiseMap[newY, newX] = noiseMap[y, x]
        
        # Mirror the upper half of the left triangular half across center of grid
        for y in range(self.maxY):
            for x in range(self.maxX):
                if y > x and y + x < self.maxY - 1: # Points within upper half of left triangular half
                    newY = self.maxY - y - 1
                    newX = self.maxX - x - 1
                    noiseMap[newY, newX] = noiseMap[y, x]
                    
        # Normalize the mirrored map
        noiseMapNormalized = (noiseMap - noiseMap.min()) #Make smallest value 0
        noiseMapNormalized = noiseMapNormalized/ noiseMapNormalized.max() #Scale all values from 0 to 1
        print(f"minZ = {noiseMap.min()} maxZ = {noiseMap.max()}")
        minZ = 0
        maxZ = 10
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

        return scaledNoiseMapInt

class ZMap(Noise):
    def __init__(self, maxY, maxX, board):
        super().__init__(maxY, maxX)
        self.board = board
        self.map = self.genNoise(0.1, 1)

    def ZMhandleEvent(self, event):
        if isinstance(event, eMove):

            adjZs = {}
            for direction, (adjY, adjX) in self.board.validAdjPositions.items():
                adjZ = self.map[adjY, adjX]
                unitZ = self.map[event.unit.position[0], event.unit.position[1]]

                adjZs[(event.unit.position[0], event.unit.position[1])] = unitZ
                adjZs[(direction, (adjY, adjX))] = adjZ

            return adjZs
            
class EventDispatcher:
    def __init__(self):
        self.listeners = {}

    def addListener(self, eventType, listener):
        if eventType not in self.listeners:
            self.listeners[eventType] = []
        self.listeners[eventType].append(listener)

    def dispatch(self, event):
        eventType = type(event)
        responseList = []

        if eventType in self.listeners:
            for listener in self.listeners[eventType]:
                listenerName = listener.__name__
                response = listener(event)
                listenerTuple = (listenerName, response)
                responseList.append(listenerTuple)

        else:
                return []

        return responseList

class eMove:
    def __init__(self, unit, minPoint, maxPoint):
        self.unit = unit
        self.minPoint = minPoint
        self.maxPoint = maxPoint

class BoardDirector:
    """
    Board Director class which interface with ObjectTree to place GameObject seeds
    """
    emptySymbol = '.'
    defaultMinPoint = (0,0)

    def __init__(self, maxY, maxX):
        self.maxY = maxY
        self.maxX = maxX
        self.maxPoint = (maxX, maxY)
        # self.allElemPositions = set()
        # self.allSeedPositions = set()
        self.dispatcher = EventDispatcher()
        self.createDummyGameObjects()
        self.initializeObjectTree()
        self.initializeZMap()
        
    

    def createDummyGameObjects(self):
        self.dummya = go.GameObject('a', (0,1), 0)
        self.dummyb = go.GameObject('b', (0,1), 0)
        self.dummyc = go.GameObject('c', (0,1), 0)
        self.dummyd = go.GameObject('d', (0,1), 0)

    def initializeObjectTree(self):
        self.gameObjectTree = GameObjectTree(self.defaultMinPoint, self.maxPoint, self)
        self.dispatcher.addListener(eMove, self.gameObjectTree.GOThandleEvent)
        self.gameObjectTree.insert(self.dummya)
        self.gameObjectTree.insert(self.dummyb)
        self.gameObjectTree.insert(self.dummyc)
        self.gameObjectTree.insert(self.dummyd)

    def initializeUnits(self):
        self.instUM = UnitsMap(self.maxY, self.maxX, self)
        self.dispatcher.addListener(eMove, self.instUM.UMhandleEvent)
        self.unitsMap = self.instUM.map

        p1a = u.Unit(0, 1, (0,0))
        p1b = u.Unit(0, 2, (1,0))
        p2a = u.Unit(1, 3, (49,49))
        p2b = u.Unit(1, 4, (48,49))
        
        self.unitsMap[0][0] = p1a
        self.unitsMap[1][0] = p1b
        self.unitsMap[49][49] = p2a
        self.unitsMap[48][49] = p2b

        self.drawMap(self.unitsMap)

        return [p1a, p1b, p2a, p2b]

    def initializeNoise(self):
        self.noise = Noise(self.maxY, self.maxX)

    def initializeZMap(self):
        self.instZM = ZMap(self.maxY, self.maxX, self)
        self.dispatcher.addListener(eMove, self.instZM.ZMhandleEvent)
        self.zMap = self.instZM.map
     


    def getValidDirections(self, unit):
        unitY, unitX = unit.position
        validDirections = {}

        self.adjPositions = {
            "NW": (unitY - 1, unitX - 1),
            "N": (unitY - 1, unitX),
            "NE": (unitY - 1, unitX + 1),
            "E": (unitY, unitX + 1),
            "SE": (unitY + 1, unitX + 1),
            "S": (unitY + 1, unitX),
            "SW": (unitY + 1, unitX - 1),
            "W": (unitY, unitX - 1)
        }

        self.validAdjPositions = self.filterValidDirections(self.adjPositions)

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
            maxPointX = 49 
        
        if maxPointY > (len(self.unitsMap) - 1):
            maxPointY = 49

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
        gameObjectTreeR = listenerResponses[0][1]
        zMapR = listenerResponses[1][1]
        unitsMapR = listenerResponses[2][1]

        takeFallDamage = False
        addSurfaces = []
        for direction, position in self.validAdjPositions.items():

            # Check if adjacent Unit exists
            if (direction, position) in unitsMapR:
                if unitsMapR[(direction, position)] != None:
                    continue

            # Calculate elevation difference and check if it's too great
            if gameObjectTreeR != []:
                for dict in gameObjectTreeR:
                    if position == dict.get("position"):
                        stackZ = dict.get("stackZ")
                        surfaces = dict.get("surfaces")
                totalZ = zMapR[(direction, position)] + stackZ
                if surfaces != None:
                    addSurfaces.append(surfaces)

            totalZ = zMapR[direction, position]
            unitZ = zMapR[unit.position]

            if (totalZ - unitZ) > unit.jump:
                continue

            # Check for fall damage
            if (totalZ - unitZ) < -abs(unit.jump):
                takeFallDamage = True

            # If the position is valid, add it to the validDirections dictionary
            validDirections[(direction, position)] = (takeFallDamage, addSurfaces)

        return validDirections
        
    def getValidAbilities(self, unit):
        unitAbilities = unit.abilities()
        # Access dictionary of class actions and their action points cost
        # Return all, but denote which are actually allowed by current action points
        # Highest level keys are 'name,''cost,' and 'events' which consists of type of events (dictionaries) involved in constructing the ability

        affordableAbilities = []
        invalidAbilities = {}
        for ability in unitAbilities:
            if ability.get("cost") <= unit.currentActionPoints:
                affordableAbilities.append(ability)
            if ability.get("cost") <= unit.currentActionPoints:
                invalidAbilities[ability["name"]] = ability.get("cost")

        # for ability in affordableAbilities:
        #     if affordableAbilities.get("range") > 1:
                


        return affordableAbilities, invalidAbilities

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

    def move(self, entity, dict):
        if isinstance(entity, u.Unit):
            destination = list(dict.keys())
            self.unitsMap[destination[1][1][0]][destination[1][1][1]] = self.unitsMap[entity.position[0]][entity.position[1]] # (Y, X) format
            self.unitsMap[entity.position[0]][entity.position[1]] = None
            entity.position = destination[1][1][0], destination[1][1][1]
            self.drawMap(self.unitsMap)

            # Apply fall damage
            # Apply surfaces

    def drawMap(self, map):
            # cMap = plt.cm.terrain
            # cMapMin = 0
            # cMapMax = 10
            # coloredZMap = cMap(matrix)
            for y in range(len(map)):
                rowToPrint = ''
                for x in range(len(map[y])):
                    if map[y][x] == None:
                        rowToPrint += '{: ^3}'.format(".")    
                    else:
                        rowToPrint += '{: ^3}'.format(f"{map[y][x].unitID}")
                print(rowToPrint)
            
            # Supposed to adjust colors according to the range of possible noise values but not sure if working
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

class GameObjectTree:
    def __init__(self, minPoint, maxPoint, board, capacity = 4, depth = 0, maxDepth = 5):
        self.minPoint = minPoint
        self.maxPoint = maxPoint
        self.board = board
        self.capacity = capacity  # Maximum number of game objects per stack
        self.depth = depth
        self.maxDepth = maxDepth
        self.defaultStackHeight = 4
        self.stacks = {}  # Dictionary of stacks: keys are positions, values are lists of game objects
        self.children = None
        self.isLeaf = (depth == maxDepth)

    def insert(self, gameObject):
        gameObjectTreeY = self.board.maxY - 1 - gameObject.position[0]
        stackPosition = (gameObject.position[1], gameObjectTreeY)
        if stackPosition not in self.stacks and len(self.stacks) < self.capacity:
            # Initialize a new stack (list) at the key stackPosition if it does not exist
            self.stacks[stackPosition] = []

        # Check if gameObject position is within limits of current node
        if not self.isWithinBounds(stackPosition):
            return False

        # If current node's stack is not full, insert GameObject
        stack = self.stacks[stackPosition]
        if len(stack) < self.defaultStackHeight:
            stack.append(gameObject)
            print(f'Inserting GameObject into stack at ({stackPosition[0]},{stackPosition[1]} (X,Y)')
            return True

        if len(stack) == self.defaultStackHeight and not self.isLeaf:
            if not self.children:
                self.subdivide()
        
        # Attempt to insert the game object into child nodes
        for child in self.children:
            if child.insert(gameObject):
                return True

        if len(stack) == self.defaultStackHeight and self.isLeaf:
            raise ValueError(f"Stack at position {stackPosition} is full. Could not insert game object {gameObject}.")
        return False
        
    def subdivide(self, gameObject):
        midX = (self.minPoint[0] + self.maxPoint[0]) / 2
        midY = (self.minPoint[1] + self.maxPoint[1]) / 2

        self.children = [
            GameObjectTree([self.minPoint[0], self.minPoint[1]], [midX, midY], self.board, depth = self.depth + 1, maxDepth = self.maxDepth),
            GameObjectTree([midX, self.minPoint[1]], [self.maxPoint[0], midY], self.board, depth = self.depth + 1, maxDepth = self.maxDepth),
            GameObjectTree([self.minPoint[0], midY], [midX, self.maxPoint[1]], self.board, depth = self.depth + 1, maxDepth = self.maxDepth),
            GameObjectTree([midX, midY], [self.maxPoint[0], self.maxPoint[1]], self.board, depth = self.depth + 1, maxDepth = self.maxDepth),
        ]

        # Redistribute game objects from the current node to child nodes
        for stackPosition, stack in self.stacks.items():
            # Try to insert each game object from the stack into the child nodes
            for gameObject in stack:
                inserted = False
                for child in self.children:
                    if child.insert(gameObject):
                        inserted = True
                        break
                if not inserted:
                    raise ValueError(f"Failed to insert game object {gameObject} into any child node.")
        
        # Clear the current node's list of game objects after redistributing them
        self.stacks = {}
        
        # Since the current node now has children, it is no longer a leaf node
        self.isLeaf = False

    def querySpace(self, minPoint, maxPoint):
        foundStacks = []
        # Return empty list if current node does not overlap with query bounds
        if not self.isOverlapping(None, minPoint, maxPoint):
            return foundStacks

        for stackPosition, stack in self.stacks.items():
            # Check if the stack position overlaps with the query bounds
            if self.isOverlapping(stackPosition, minPoint, maxPoint):
                foundStacks.append(stack)
    
        # If the current node has children, recursively query each child
        if self.children:
            for child in self.children:
                if child.isOverlapping(stackPosition, minPoint, maxPoint):
                    foundStacks.extend(child.querySpace(minPoint, maxPoint))
        
        return foundStacks

    def isOverlapping(self, stackPosition, minPoint, maxPoint):
        
        if stackPosition != None:
            return (
                maxPoint[0] >= self.minPoint[0] and minPoint[0] <= self.maxPoint[0] and
                maxPoint[1] >= self.minPoint[1] and minPoint[1] <= self.maxPoint[1] and
                maxPoint[0] >= stackPosition[0] and minPoint[0] <= stackPosition[0] and
                maxPoint[1] >= stackPosition[1] and minPoint[1] <= stackPosition[1]
            )
        
        if stackPosition == None:
            return (
                maxPoint[0] >= self.minPoint[0] and minPoint[0] <= self.maxPoint[0] and
                maxPoint[1] >= self.minPoint[1] and minPoint[1] <= self.maxPoint[1]
            )

    def isWithinBounds(self, position):
        minX, minY = self.minPoint
        maxX, maxY = self.maxPoint

        return minX <= position[0] <= maxX and minY <= position[1] <= maxY
    
    def GOThandleEvent(self, event):
        if isinstance(event, eMove):
            queriedStacks = self.propagateEvent(event)
            return queriedStacks

    def propagateEvent(self, event):
        # Check if the event affects the current node
        if self.isOverlapping(None, event.minPoint, event.maxPoint):
            # Handle the event at the current node level
            return self.processEvent(event)
        
        # If there are children, propagate the event down
        if self.children:
            for child in self.children:
                child.propagateEvent(event)
                print("propagate!\n")

    def processEvent(self, event):           
        if isinstance(event, eMove):
            queriedStacks = []
            stacks = self.querySpace(event.minPoint, event.maxPoint)
            for stack in stacks:
                for direction, position in self.board.validAdjPositions.items():
                    if position == stack[0].position:
                        stackDict = {}
                        stackDict["direction"] = direction                        
                        stackDict["position"] = position
                        stackDict["stack"] = stack
                        
                        stackZ = 0
                        surfaces = []
                        for gameObject in stack:
                            if isinstance(gameObject, go.Surface):
                                surfaces.append(gameObject)
                            else:
                                stackZ += gameObject.z

                        stackDict["stackZ"] = stackZ
                        stackDict["surfaces"] = surfaces

                        queriedStacks.append(stackDict)

            return queriedStacks





# def genElems(self, elemTypes):
    #     print('\n--- Starting genElems ---')
    #     elemDebugName = ''
    #     for elem in elemTypes:
    #         elemDebugName += elem.debugName + ' '
    #     print(f'Input elemTypes: {elemDebugName}')
        
    #     if not isinstance(elemTypes, list):
    #         elemTypes = [elemTypes]
            
    #     elemTypes = list(set(elemTypes))

    #     for elem in elemTypes:
    #         refClassInst = elem(None)
    #         print(f'Processing element type {refClassInst.debugName} with symbol: {refClassInst.symbol}')
    #         randMultiplier = random.randint(refClassInst.elemRandMultiplierBounds[0], refClassInst.elemRandMultiplierBounds[1])
    #         print(f'Multiplier for element type {refClassInst.debugName}: {randMultiplier}')

    #         for _ in range(randMultiplier): 
    #             while True:
    #                 randElemPosition = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
                    
    #                 if randElemPosition not in self.allElemPositions and self.getObject(randElemPosition[0], randElemPosition[1]) == None:
    #                     self.allElemPositions.add(randElemPosition)
    #                     self.grid[randElemPosition[0]][randElemPosition[1]] = elem(randElemPosition)
    #                     break
                
    #             print(f'Placed element type {elem(None).symbol} at position {randElemPosition}')
            
    #         print(f'Current element positions: {self.allElemPositions}')
            
    #     print('--- Finished genElems ---\n')

    # def genObstacles(self, seedMultiplier):
    #     print('\n--- Starting genObstacles ---')
    #     print(f'Input seedMultiplier: {seedMultiplier}')
        
    #     for _ in range(seedMultiplier):
    #         while True:
    #             randSeedPosition = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
                
    #             if self.getObject(randSeedPosition[0], randSeedPosition[1]) == None:
    #                 newSeed = go.Seed(randSeedPosition, self)
    #                 newSeed.pGrow = 1
    #                 self.allSeedPositions.add(randSeedPosition)
    #                 self.grid[randSeedPosition[0]][randSeedPosition[1]] = newSeed
    #                 newSeed.proliferate()
    #                 break
                
    #         print(f'Placed seed at position {randSeedPosition}')
        
    #     print(f'Current seed positions: {self.allSeedPositions}')
    #     print('--- Finished genObstacles ---\n')