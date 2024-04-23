import random
import numpy as np
from  opensimplex import OpenSimplex
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

def boolWithProb(p):
    return random.random() < p

class GameObject:
    """
    In-game object class that represents a generic "game object" from which child classes
    for elements, obstacles, units manage corresponding symbols, behavior/interactions. 
    """
    occupied = False
    symbol = None

    def __init__(self, position, z):
        self.position = position
        self.z = z
        self.occupied = self.symbol != '.'

class Elements(GameObject):
    elemRandMultiplierBounds = (1, 4)

class Terrain(GameObject):
    pass
    
class Obstacles(Terrain):
    pass

class Water(Elements):
    debugName = 'Water'
    symbol = 'W'
    
    def __init__(self, position):
        super().__init__(position)

class Earth(Elements):
    debugName = 'Earth'
    symbol = 'E'
    
    def __init__(self, position):
        super().__init__(position)

class Fire(Elements):
    debugName = 'Fire'
    symbol = 'F'
   
    def __init__(self, position):
        super().__init__(position)

class Air(Elements):
    debugName = 'Air'
    symbol = 'A'
    
    def __init__(self, position):
        super().__init__(position)

class Seed(Obstacles):
    debugName = 'Seed'
    symbol = '[ ]'
    pGrow = 0.2
    
    def __init__(self, position, boardClassInstance):
        super().__init__(position)
        self.position = position
        self.boardClassInstance = boardClassInstance

    def proliferate(self):
        seedPosition = self.position
        directions = [
            (-1, 0),  # Top
            (1, 0),   # Bottom
            (0, -1),  # Left
            (0, 1),   # Right
        ]

        for dRow, dCol in directions:
            newRow = seedPosition[0] + dRow
            newCol = seedPosition[1] + dCol
            
            if 0 <= newRow < self.boardClassInstance.rows and 0 <= newCol < self.boardClassInstance.cols:
                newSeedPosition = (newRow, newCol)
                adjacentObject = self.boardClassInstance.grid[newRow][newCol]
                
                if (adjacentObject is None or not adjacentObject.occupied) and boolWithProb(self.pGrow):
                    newSeed = Seed(newSeedPosition, self.boardClassInstance)
                    newSeed.symbol = '~'
                    self.boardClassInstance.grid[newRow][newCol] = newSeed
                    newSeed.proliferate()

class Surface(Terrain):
    debugName = 'Surface'
    pass

class HashTable:
    def __init__(self, maxX, maxY):
        self.maxX = maxX
        self.maxY = maxY
        self.area = maxX * maxY
        self.table = [[] for _ in range(self.area)]
    
    def __setitem__(self, key, value):
        h = self.getHash(key)
        found = False
        for index, element in enumerate(self.table[h]):
            if len(element) == 2 and element[0] == key:
                found = True
                self.table[h][index] = (key, value)

        if found == False:
            self.table[h][index].append((key, value))

    def __getitem__(self, key):
        h = self.getHash(key)
        for index in self.table[h]:
            if index[0] == key:
                return index[1]
            
    def __delitem__(self,key):
        h = self.getHash(key)
        for index in self.table[h]:
            if index[0] == key:
                del self.table[h][index]     
        
    def getHash(self, coord):
        return hash(coord) % self.area

class BoardDirector:
    """
    Board Director class which interface with BoardMap to place GameObject seeds
    """
    emptySymbol = '.'
    maxSymbolLen = 3
    defaultMinPoint = (0,0)

    def __init__(self, maxY, maxX):
        self.maxY = maxY
        self.maxX = maxX
        self.allElemPositions = set()
        self.allSeedPositions = set()
        
    def initializeObjectTree(self):
        ObjectTree(self.defaultMinPoint, self.maxPoint)
        print(f'Intializing single node BoardMap with size {self.maxPoint[0]} x {self.maxPoint[1]}')

    def genZMap(self):
        simplex = OpenSimplex(seed = 0)
        scale = 0.1
        zMap = np.zeros((self.maxY, self.maxX))
        for y in range(self.maxY):
            for x in range(self.maxX):
                noise = simplex.noise2(x * scale, y * scale)
                zMap[y, x] = noise

        zMap = (zMap - zMap.min())/(zMap.max() - zMap.min())
        minHeight = 0
        maxHeight = 10
        scaledZMapFloat = zMap * (maxHeight - minHeight) + minHeight
        scaledZMapInt = np.round(scaledZMapFloat).astype(int)

    def genBoard(self, elemTypes):
        self.genElems(elemTypes)
        
    def clearBoard(self):
        for row in self.grid:
            for currentGameObject in row:
                currentGameObject.reset()

    def getObject(self, row, col):
        return self.grid[row][col]

    def printObjectAttr(self, row, col):
        object = self.grid[row][col]
        print(f'\n--- Getting attributes for {object.debugName} ---') 
        objectVars = object.__dict__
        for varName, value in objectVars.items():
            print(f'{varName} = {value}')

    def drawMatrix(self, matrix):
        if matrix.genZMap:
            colorMap = plt.cm.terrain
            coloredZMap = colorMap(matrix)
            for y in len(range(matrix)):
                rowToPrint = ''
                for x in len(matrix[y]):
                        rowToPrint += '{: ^3}'.format(matrix[y][x])
                print(rowToPrint)
            plt.imshow(coloredZMap)
            plt.colorbar()  
            plt.show()    

    def genElems(self, elemTypes):
        print('\n--- Starting genElems ---')
        elemDebugName = ''
        for elem in elemTypes:
            elemDebugName += elem.debugName + ' '
        print(f'Input elemTypes: {elemDebugName}')
        
        if not isinstance(elemTypes, list):
            elemTypes = [elemTypes]
            
        elemTypes = list(set(elemTypes))

        for elem in elemTypes:
            refClassInst = elem(None)
            print(f'Processing element type {refClassInst.debugName} with symbol: {refClassInst.symbol}')
            randMultiplier = random.randint(refClassInst.elemRandMultiplierBounds[0], refClassInst.elemRandMultiplierBounds[1])
            print(f'Multiplier for element type {refClassInst.debugName}: {randMultiplier}')

            for _ in range(randMultiplier): 
                while True:
                    randElemPosition = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
                    
                    if randElemPosition not in self.allElemPositions and self.getObject(randElemPosition[0], randElemPosition[1]) == None:
                        self.allElemPositions.add(randElemPosition)
                        self.grid[randElemPosition[0]][randElemPosition[1]] = elem(randElemPosition)
                        break
                
                print(f'Placed element type {elem(None).symbol} at position {randElemPosition}')
            
            print(f'Current element positions: {self.allElemPositions}')
            
        print('--- Finished genElems ---\n')

    def genObstacles(self, seedMultiplier):
        print('\n--- Starting genObstacles ---')
        print(f'Input seedMultiplier: {seedMultiplier}')
        
        for _ in range(seedMultiplier):
            while True:
                randSeedPosition = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
                
                if self.getObject(randSeedPosition[0], randSeedPosition[1]) == None:
                    newSeed = Seed(randSeedPosition, self)
                    newSeed.pGrow = 1
                    self.allSeedPositions.add(randSeedPosition)
                    self.grid[randSeedPosition[0]][randSeedPosition[1]] = newSeed
                    newSeed.proliferate()
                    break
                
            print(f'Placed seed at position {randSeedPosition}')
        
        print(f'Current seed positions: {self.allSeedPositions}')
        print('--- Finished genObstacles ---\n')

    def spawnUnits(self):
        pass


import random
import numpy as np
from  opensimplex import OpenSimplex
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

class BoardDirector:
    """
    Board Director class which interface with BoardMap to place GameObject seeds
    """
    emptySymbol = '.'
    maxSymbolLen = 3
    defaultMinPoint = (0,0)

    def __init__(self, maxY, maxX):
        self.maxY = maxY
        self.maxX = maxX
        self.allElemPositions = set()
        self.allSeedPositions = set()
        
    def initializeObjectTree(self):
        ObjectTree(self.defaultMinPoint, self.maxPoint)
        print(f'Intializing single node BoardMap with size {self.maxPoint[0]} x {self.maxPoint[1]}')

    def genTerrainNoise(self, scales, amplis):
        simplex = OpenSimplex(0)
        noiseMap = np.zeros((self.maxY, self.maxX))

        # Generate noise for the left triangular half of the grid (grid split across main diagonal)
        for s, a in zip(scales, amplis):
            for y in range(self.maxY):
                for x in range(self.maxX):
                    if y - x > 0:
                        noise = simplex.noise2(x * s, y * s) * a
                        noiseMap[y, x] += noise

        # Calculate minimum noise value in the noiseMap
        minNoise = noiseMap.min()
        # Shift the entire noiseMap up by adding the absolute of the minimum value to exclude negative values
        noiseMap += abs(minNoise)
        print(f'After shifting, minZ = {noiseMap.min()}, maxZ = {noiseMap.max()}')

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
        noiseMapNormalized = (noiseMap - noiseMap.min()) / (noiseMap.max() - noiseMap.min())
        print(f'minZ = {noiseMap.min()} maxZ = {noiseMap.max()}')
        minZ = 0
        maxZ = 10
        scaledNoiseMapFloat = noiseMapNormalized * (maxZ - minZ)
        scaledNoiseMapInt = np.round(scaledNoiseMapFloat).astype(int)
        borderWidth = 3

        for y in range(self.maxY):
            for x in range(self.maxX):
                # Calculate the distance from the diagonal and antidiagonal lines
                distFromDiag = abs(y - x)
                distFromAntidiag = abs((y + x) - (self.maxY - 1))
                
                # Check if the point is within the border width of the diagonal or antidiagonal lines
                if (
                    distFromDiag <= borderWidth or
                    distFromAntidiag <= borderWidth
                ):
                    # Set the value to zero to create a border zone
                    scaledNoiseMapInt[y, x] = 0

        return scaledNoiseMapInt

    def drawMatrix(self, matrix):
            cMap = plt.cm.terrain
            cMapMin = 0
            cMapMax = 10
            norm = Normalize(vmin = cMapMin, vmax = cMapMax)
            coloredZMap = cMap(matrix)
            for y in range(len(matrix)):
                rowToPrint = ''
                for x in range(len(matrix[y])):
                        rowToPrint += '{: ^3}'.format(matrix[y][x])
                print(rowToPrint)
            plt.imshow(coloredZMap, cmap = cMap, norm = norm) 
            plt.show()

    def genTerrain(self, terrainType, maskSize):
        
        # Generating knolls and hills environment
        baseTerrain = self.genTerrainNoise([0.1],[0.07])


        cliffThreshold = 8
        plateauThresholds = 4
        dropOffThresholds = (0,8)

        baseTerrain = self.genTerrainNoise([0.1], [0.05])
        # Apply masking
        baseTerrain

a = BoardDirector(51,51)
b = a.genTerrainNoise([0.1], [0.1])
print(a)
a.drawMatrix(b)
        
class ObjectTree:

    defaultStackHeight = 4
    defaultStackLen = 1
    defaultStackWid = 1

    def __init__(self, minPoint, maxPoint, capacity = 1):
        self.minPoint = minPoint
        self.maxPoint = maxPoint
        self.capacity = capacity
        self.stack = [None for _ in range(self.defaultStackHeight)]
        self.children = None
        self.isLeaf = self.defaultStackLen == (self.maxPoint[0] - self.minPoint[0]) and self.defaultStackWid == (self.maxPoint[1] - self.minPoint[1])

    def insert(self, gameObject):
        """
        Will fill stacks from bottom up with GameObjects regardless of identity. 
        Rules of stacking order per GameObject identiy defined by BoardDirector.
        """

        # Check if gameObject position is within limits of current node
        if not self.isWithinBounds(gameObject.position):
            return False

        # Check if current node is a leaf node
        if self.isLeaf:
            # If current node's stack is not full, insert GameObject
            if len(self.stack) < self.defaultStackHeight:
                self.stack.append(gameObject)
                print(f'Inserting GameObject into stack at ({gameObject.position[0]},{gameObject.position[1]}')
        
        else:
            self.subdivide(gameObject)
        
    def subdivide(self, gameObject):
        midX = (self.minPoint[0] + self.maxPoint[0]) / 2
        midY = (self.minPoint[1] + self.maxPoint[1]) / 2

        self.children = [
        BoardMap([self.minPoint[0], self.minPoint[1]], [midX, midY]),
        BoardMap([midX, self.minPoint[1]], [self.maxPoint[0], midY]),
        BoardMap([self.minPoint[0], midY], [midX, self.maxPoint[1]]),
        BoardMap([midX, midY], [self.maxPoint[0], self.maxPoint[1]]),
        ]

        # Relocate stack to iteration 0 of self.children
        for existingGameObject in self.stack:
            inserted = False
            for child in self.children:
                if child.insert(existingGameObject):
                    inserted = True
                    break
            
            # If the game object could not be inserted into any child node, handle the case appropriately
            if not inserted:
                raise ValueError(f"Failed to insert game object {gameObject} into any child node.")
                
        # Clear the current node's list of game objects after redistributing them
        self.stack = []

    def querySpace(self, minPoint, maxPoint):
        foundStacks = []
        # Return empty list if current node does not overlap with query bounds
        if not self.isOverlapping(minPoint, maxPoint):
            return foundStacks

        if self.isOverlapping and self.isLeaf:
            foundStacks.append(self.stack)
        
        if self.children:
            for child in self.children:
                if child.isOverlapping(minPoint, maxPoint):
                    self.querySpace(child)

        return foundStacks

    def isOverlapping(self, minPoint, maxPoint):
        return (
            maxPoint[0] >= self.minPoint[0] and minPoint[0] <= self.maxPoint[0] and
            maxPoint[1] >= self.minPoint[1] and minPoint[1] <= self.maxPoint[1]
        )

    def isWithinBounds(self, position):
        minX, minY = self.minPoint
        maxX, maxY = self.maxPoint

        return minX <= position[0] <= maxX and minY <= position[1] <= maxY