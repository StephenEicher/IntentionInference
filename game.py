import random
import numpy as np
from  opensimplex import OpenSimplex
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import abc

def boolWithProb(p):
    return random.random() < p

class GameManager:
    def __init__(self):
        self.agentTurnIndex = 0
        self.gameState = 0 # gameState increases per completion of each agent's turn
        self.gameOver = False
        self.start()
        self.dispatcher = EventDispatcher()

    def start(self):
        self.Board = BoardDirector(50, 50)
        self.allUnits = self.Board.initializeUnits()
        self.team0 = []
        self.team1 = []
        self.team0.extend([self.allUnits[0], self.allUnits[1]])
        self.team1.extend([self.allUnits[2], self.allUnits[3]])
        self.p1 = humanAgent(0, self.team0)
        self.p2 = humanAgent(1, self.team1)
        
    def gameLoop(self):

        if len(self.p1.team) == 0 or len(self.p2.team) == 0:
            self.gameOver = True

        while self.gameOver == False:
    
            if self.agentTurnIndex == 0:
                print("-------- Player 1's turn --------")
                selectedUnit = self.p1.selectUnit()
                while selectedUnit.unitValidForTurn():
                    agentInput = self.getInput(selectedUnit)
                    self.createEvents(agentInput, selectedUnit)
                    self.dispatcher.dispatch(pendingEvents)

            self.gameState += 0.5

            if turnFinished == True:
                self.agentTurnIndex = 1

            if self.agentTurnIndex == 1:
                self.team0.extend(self.allUnits[2], self.allUnits[3])
    

    def getInput(self, unit):
        # This kind of code should really live on the humanPlayer agent- only a human player needs to interface with the terminal for the input.
        self.validDirections = self.Board.getValidDirections(unit)
        self.validActions = self.Board.getValidActions(unit)[0]
        invalidActions = self.Board.getValidActions(unit)[1]

        while True:
            print(f"--- {unit.unitID} ---")
            print(f"Available directions:\n".join([f"{direction}: fall damage = {value[1]}, surface = {value[2]}" for direction, value in self.validDirections.items()]))
            print(f"Available actions:\n".join([f"{name}: {cost}" for name, cost in self.validActions.items()]))
            print("---")
            print(f"Unavailable actions:\n".join([f"{name}: {cost}" for name, cost in invalidActions.items()]))
            agentInput = input("\n\n\nTo move in a available direction, type the direction. To choose an action, type the name of the action. To swap, type 'swap'")

            if agentInput in self.validDirections:
                return ["move", input]

            # if agentInput in self.validActions.items():
            #     allActions = unit.actions()

            #     for _, actionDict in allActions.items():
            #         if agentInput in actionDict:
            #             for eventDict in actionDict["events"]:
            #                 if "targetunit" in eventDict:     
            #     return ["action", input]

            if agentInput == "swap":
                return ["None"]

            print("\n\n!!!! Invalid input !!!!")

    def createEvents(self, agentInput, unit):
        if "move" in agentInput:
            direction = agentInput[1]
            destination = self.validDirections[direction]
            moveEvent = eMove(unit, destination)
            return moveEvent

        if "action" in agentInput:
            actionName = agentInput[1]
            subevents = []
            allActions = unit.actions()
            for _, actionDict in allActions.items():
                if actionName in actionDict:
                    subevents.extend(actionDict["events"])

        if "swap" in agentInput:
            # Do not create event, call loo

            return pendingEvents
 
class Agent(metaclass=abc.ABCMeta):
    def __init__(self, agentIndex, team):       
        self.agentIndex = agentIndex
        self.team = team
    @abc.abstractmethod
    def selectUnit(self):
        pass


class humanAgent(Agent):
    def selectUnit(self):
        waitingUnits = []
        for unit in self.team:
            if unit.Alive == True and unit.Avail == True:
                waitingUnits.append(unit)

        selectedUnit = input(f"Select from avail Units: {waitingUnits}")
    
        return selectedUnit

class Unit:
    position = None
    currentHp = None
    currentMovement = None
    currentActionPoints = None
    currentJump = None
    def __init__(self, agentIndex, unitID):
        self.agentIndex = agentIndex
        self.unitID = unitID

        

        self.Alive = True
        self.Avail = True # Available to select from team of units to move/act with

        self.startHp = 100
        self.movement = 5
        
        self.jump = 2
        

        self.actionPoints = 2
       

    def actions(self):
        
        uniqueActions = [
            
            {"name": "Unarmed Strike",
           "cost": "1 action point",
            "events": [
                {"type": "changeHP", "target": "targetunit", "value": -1},
                {"type": "changeActionPoints", "target": "targetunit", "value": -1},
            ]},

            {"name": "Shove",
           "cost": "1 action point",
            "events": [
                {"type": "move", "target": "targetunit", "distance": 1},
                {"type": "changeActionPoints", "target": "targetunit", "value": -1},
            ]},
            
            {"name": "Hide",
           "cost": "1 action point",
            "events": [
                {"type": "hide", "target": "self"}
            ]}

            ]

        return uniqueActions # Return different combinations of events that GameManager can access and send on behalf of the unit in play
    def unitValidForTurn(self):
        #Put this into an accessor function because you may modify it with special "statuses" like "stunned"
        return self.currentHP > 0 or self.currentMovement > 0 or self.currentActionPoints > 0
class eMove:
    def __init__(self, unit, destination):
        self.unit = unit
        self.destination = destination

class EventDispatcher:
    def __init__(self):
        self.listeners = {}

    def addListener(self, eventType, listener):
        if eventType not in self.listeners:
            self.listeners[eventType] = []
        self.listeners[eventType].append(listener)

    def dispatch(self, event):
        eventType = type(event)
        if eventType in self.listeners:
            for listener in self.listeners[eventType]:
                listener(event)

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
        ObjectTree([self.minPoint[0], self.minPoint[1]], [midX, midY]),
        ObjectTree([midX, self.minPoint[1]], [self.maxPoint[0], midY]),
        ObjectTree([self.minPoint[0], midY], [midX, self.maxPoint[1]]),
        ObjectTree([midX, midY], [self.maxPoint[0], self.maxPoint[1]]),
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

class Noise:
    def __init__(self, maxY, maxX):
        self.maxY = maxY
        self.maxX = maxX

    def genNoise(self, scales, amplis):
        simplex = OpenSimplex(seed = 0)
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

class zMap(Noise):
    def __init__(self):
        super().__init__()
        self.genNoise(self, 0.1, 1)

    def handleEvent(event):
        pass

class UnitsMap:
    def __init__(self, maxY, maxX):
        np.zeros((maxY, maxX))

    def getDist(self):
        pass

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
        self.allElemPositions = set()
        self.allSeedPositions = set()

    def initializeObjectTree(self):
        self.GOtree = ObjectTree(self.defaultMinPoint, self.maxPoint)

    def initializeUnits(self):
        self.unitsMap = UnitsMap(self.maxY, self.maxX)

        p1a = Unit(0, 0)
        p1b = Unit(0, 1)
        p2a = Unit(1, 0)
        p2b = Unit(1, 1)
        
        return [p1a, p1b, p2a, p2b]

    def initializeNoise(self):
        self.noise = Noise(self.maxY, self.maxX)

    def initializeZMap(self):
        self.zMap = zMap()

    def getValidDirections(self, unit):
        unitY, unitX = unit.position
        validDirections = {}
        adjGOStacks = {}

        adjPositions = {
            "N": (unitY - 1, unitX - 1),
            "NE": (unitY - 1, unitX),
            "E": (unitY - 1, unitX + 1),
            "SE": (unitY, unitX + 1),
            "S": (unitY + 1, unitX + 1),
            "SW": (unitY + 1, unitX),
            "W": (unitY + 1, unitX - 1),
            "NW": (unitY, unitX - 1)
        }

        # Populate adjGOStacks with direction as key and the GOStack found at that position as value
        minPoint = (unitX - 1, unitY - 1)
        maxPoint = (unitX + 1, unitY + 1)
        foundGOStacks = self.GOtree.querySpace(minPoint, maxPoint)
        
        # Organize found GO stacks by direction
        for stack in foundGOStacks:
            for direction, position in adjPositions:
                if position == stack[0].position:
                    adjGOStacks[direction] = stack

        for direction, (adjY, adjX) in adjPositions.items():
            # Check if the adjacent position is within bounds of the map
            if 0 <= adjY < self.unitsMap.shape[0] and 0 <= adjX < self.unitsMap.shape[1]:
                adjObject = self.unitsMap[adjY, adjX]
                
                # Skip direction if there is a Unit in the adjacent position
                if isinstance(adjObject, Unit):
                    continue
                
                # Calculate elevation difference and check if it's too great
                adjZ = self.zMap[adjY, adjX]
                unitZ = self.zMap[unitY, unitX]            
                takeFallDamage = False
                surfaceModifier = []

                for GO in adjGOStacks.get(direction, []):
                    if isinstance(GO, Obstacles):
                        obstZ = GO.height
                    # Evaluate elevation differences with zMap z value and obstacle height
                        if (adjZ + obstZ - unitZ) > unit.jump:
                            continue

                    # Check for fall damage
                    if (adjZ + obstZ - unitZ) < -abs(unit.jump):
                        takeFallDamage = True

                # Check for surface modifications
                if isinstance(GO, Surface):
                    surfaceModifier.append(GO.type)

            # If the position is valid, add it to the validDirections dictionary
            validDirections[direction] = ((adjY, adjX), takeFallDamage, surfaceModifier)

        return validDirections
    
    def getValidActions(self, unit):
        currentActionsPoints = unit.currentActionPoints
        unitActions = unit.actions()
        # Access dictionary of class actions and their action points cost
        # Return all, but denote which are actually allowed by current action points
        # Highest level keys are 'name,''cost,' and 'events' which consists of type of events (dictionaries) involved in constructing the ability

        validActions = {}
        invalidActions = {}
        for ability in unitActions:
            for cost in unitActions.get("cost", ""):
                if cost <= unit.currentActionPoints:
                    validActions[ability["name"]] = cost
                if cost <= unit.currentActionPoints:
                    invalidActions[ability["name"]] = cost

        return validActions, invalidActions

    # def bresenham_line(origin, target):
    #     return 0
    # def rayCast(self, origin, target, ObjectTree, unitsMap, zMap):
    #     line = bresenham_line(origin, target)

 

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
                

            # Supposed to adjust colors according to the range of possible noise values but not sure if working
            im = plt.imshow(coloredZMap, cmap = cMap, norm = norm)
            fig = plt.gcf()
            fig.colorbar(im)
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


a = GameManager()