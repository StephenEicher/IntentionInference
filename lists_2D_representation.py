import random

def boolWithProb(p):
    return random.random() < p

class GameObject:
    """
    In-game object class that represents a generic "game object" from which child classes
    for elements, obstacles, units manage corresponding symbols, behavior/interactions. 
    """
    occupied = False
    symbol = None

    def __init__(self, position):
        self.position = position
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

class Board:
    """
    Board class which stores the map representation.
    genBoard() - Procedural generation of game board at initial state.
    genBoardForAgent() - Create a copy of the game board for the agent.
    """
    emptySymbol = '.'
    maxSymbolLen = 3 

    def __init__(self, rows, cols, stack = 4):
        self.rows = rows
        self.cols = cols
        self.stack = stack
        self.allElemPositions = set()
        self.allSeedPositions = set()
        self.grid = [[[None for _ in range(self.stack)] for _ in range (self.cols)] for _ in range(self.rows)]
        print(f'Created an empty Board instance with dimensions {self.rows} x {self.cols} x {self.stack}')

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

    def drawBoard(self):
        for row in self.grid:
            rowToPrint = ''
            for entry in row:
                if entry is not None:
                    rowToPrint += '{: ^{}}'.format(entry.symbol, self.maxSymbolLen)
                else:
                    rowToPrint += '{: ^{}}'.format(self.emptySymbol, self.maxSymbolLen)
            print(rowToPrint)

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

print("Constructing Gameboard as gb...")
gb = Board(20, 20)
gb.genElems([Water, Fire, Air, Earth])
gb.genObstacles(6)
gb.drawBoard()






class BoardRectangle:

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
        BoardRectangle([self.minPoint[0], self.minPoint[1]], [midX, midY]),
        BoardRectangle([midX, self.minPoint[1]], [self.maxPoint[0], midY]),
        BoardRectangle([self.minPoint[0], midY], [midX, self.maxPoint[1]]),
        BoardRectangle([midX, midY], [self.maxPoint[0], self.maxPoint[1]]),
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