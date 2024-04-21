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

    def __init__(self, pos):
        self.pos = pos
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
    
    def __init__(self, pos):
        super().__init__(pos)


class Earth(Elements):
    debugName = 'Earth'
    symbol = 'E'
    
    def __init__(self, pos):
        super().__init__(pos)


class Fire(Elements):
    debugName = 'Fire'
    symbol = 'F'
   
    def __init__(self, pos):
        super().__init__(pos)


class Air(Elements):
    debugName = 'Air'
    symbol = 'A'
    
    def __init__(self, pos):
        super().__init__(pos)


#1D prolif obstacles
class Seed(Obstacles):
    debugName = 'Seed'
    symbol = '[ ]'
    pGrow = 0.2
    
    def __init__(self, pos, boardClassInstance):
        self.pos = pos
        self.boardClassInstance = boardClassInstance
        super().__init__(pos)

    def proliferate(self):
        seedPos = self.pos
        directions = [
            (-1, 0),  # Top
            (1, 0),   # Bottom
            (0, -1),  # Left
            (0, 1),   # Right
        ]

        for dRow, dCol in directions:
            newRow = seedPos[0] + dRow
            newCol = seedPos[1] + dCol
            
            if 0 <= newRow < self.boardClassInstance.rows and 0 <= newCol < self.boardClassInstance.cols:
                newSeedPos = (newRow, newCol)
                adjacentObject = self.boardClassInstance.grid[newRow][newCol]
                
                if (adjacentObject is None or not adjacentObject.occupied) and boolWithProb(self.pGrow):
                    newSeed = Seed(newSeedPos, self.boardClassInstance)
                    newSeed.symbol = '~'
                    self.boardClassInstance.grid[newRow][newCol] = newSeed
                    newSeed.proliferate()


class Surface(Terrain):
    debugName = 'Surface'
    pass


class Board:
    #Check tile for all GameObjects co-existing on given x,y
    #Modifier/accessor class for appending GameObjects, not modifying

    """
    Board class which stores the map representation
    genBoard() - Procedural generation of game board at initial state
    genBoardForAgent() - Create a copy of the game board for the agent
    """
    emptySymbol = '.'
    maxSymbolLen = 3 

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.allElemPos = set()
        self.allSeedPos = set()
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        print(f'Created an empty Board instance with dimensions {self.rows} x {self.cols}')

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
                    # if len(entry.symbol) < self.maxSymbolLen:
                    #     row_to_print += entry.symbol
                    # else:
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
                    randElemPos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
                    
                    if randElemPos not in self.allElemPos and self.getObject(randElemPos[0], randElemPos[1]) == None:
                        self.allElemPos.add(randElemPos)
                        self.grid[randElemPos[0]][randElemPos[1]] = elem(randElemPos)
                        break
                
                print(f'Placed element type {elem(None).symbol} at position {randElemPos}')
            
            print(f'Current element positions: {self.allElemPos}')
            
        print('--- Finished genElems ---\n')

    def genObstacles(self, seedMultiplier):
        print('\n--- Starting genObstacles ---')
        print(f'Input seedMultiplier: {seedMultiplier}')
        for _ in range(seedMultiplier):
           
            while True:
                randSeedPos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
               
                if self.getObject(randSeedPos[0], randSeedPos[1]) == None:
                    newSeed = Seed(randSeedPos, self)
                    newSeed.pGrow = 1
                    self.allSeedPos.add(randSeedPos)
                    self.grid[randSeedPos[0]][randSeedPos[1]] = newSeed
                    newSeed.proliferate()
                    break
                
            print(f'Placed seed at position {randSeedPos}')
        
        print(f'Current seed positions: {self.allSeedPos}')
            
        print('--- Finished genObstacles ---\n')



print("Constructing Gameboard as gb...")
gb = Board(20, 20)
gb.genElems([Water, Fire, Air, Earth])
gb.genObstacles(6)
gb.drawBoard()