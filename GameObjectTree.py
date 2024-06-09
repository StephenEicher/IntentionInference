import GameObjects as go
import queue
import numpy as np
import eventClasses as e
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
        # self.incomingUM = queue.Queue(maxsize=1)

    def addListeners(self, dispatcher):
        dispatcher.addListener(e.eMove, self.GOThandleEvent)
        dispatcher.addListener(e.eDisplace, self.GOThandleEvent, 2)
        
    def fprint(self, string):
        if self.board.game.verbose:
            print(string)

    def insert(self, gameObject):
        gameObjectTreeY = self.board.maxY - 1 - gameObject.position[0]
        stackPosition = (gameObject.position[1], gameObjectTreeY)

        # Check if gameObject position is within limits of current node
        if not self.isWithinBounds(stackPosition):
            return False

        # Prioritize inserting into child nodes if they exist
        if self.children:
            for child in self.children:
                if child.isWithinBounds(stackPosition) and child.insert(gameObject):
                    self.fprint(f"Inserted into child at ({stackPosition[0]},{stackPosition[1]})")
                    return True
            return False  # If insertion into all children fails, return False

        # If stackPosition is not in stacks and there is capacity, create a new stack
        if stackPosition not in self.stacks and len(self.stacks) < self.capacity:
            self.stacks[stackPosition] = []

        # If the node's stack is not full, insert GameObject
        stack = self.stacks.get(stackPosition)
        if stack is not None and len(stack) < self.defaultStackHeight:
            stack.append(gameObject)
            self.fprint(f'Inserting GameObject into stack at ({stackPosition[0]},{stackPosition[1]}) (X,Y) at depth {self.depth}')
            return True

        # If the stack is full and the node is a leaf, raise an error
        if stack is not None and len(stack) == self.defaultStackHeight and self.isLeaf:
            raise ValueError(f"Stack at position {stackPosition} is full. Could not insert game object {gameObject}.")

        # If the stack is full and the node is not a leaf, subdivide and try to insert into children
        if len(self.stacks) >= self.capacity:
            self.subdivide()
            for child in self.children:
                if child.insert(gameObject):
                    self.fprint(f"Inserted into child at ({stackPosition[0]},{stackPosition[1]})")
                    return True

        return False

    def subdivide(self):
        self.fprint(f"now subdividing {self.depth}")
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
            for existingGameObject in stack:
                inserted = False
                for child in self.children:
                    if child.insert(existingGameObject):
                        self.fprint(f"existingGameObject inserted successfully at ({stackPosition[0]},{stackPosition[1]}) at depth {child.depth}")
                        inserted = True
                        break
                if not inserted:
                    raise ValueError(f"Failed to insert existing game object {existingGameObject} into any child node.")

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
                if child.isOverlapping(None, minPoint, maxPoint):
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
        if isinstance(event, e.eMove):
            queriedStacks = self.propagateEvent(event)
            return queriedStacks
        

        
        if isinstance(event, e.eDisplace):
            """
            T represents the unit which displace is acting upon
            C represents the collateral units returned by UM
            O represents a game object which for now can only be an obstacle

            Possible scenarios for GOT to handle:
            
            1 collateral unit only:
            T - C
            T - C - O
            T - O - C -> not included

            multiple collateral units:
            T - C - C..
            T - C - C.. - O
            T - O - C - C.. -> not included

            collateralTargets is the list of collateralUnits which the displaced unit has direct LOS to
            """

            unitsAndDisplacement = self.incomingUM.get(False)
            if unitsAndDisplacement[0]:
                UMcollateralUnits = True
            else:
                UMcollateralUnits = False
        
            if UMcollateralUnits:
                # First, determine obstacle collision via LOS check
                newEvent = e.eTargetsInRange(event.castTarget, None)
                collateralTargets = self.GOThandleEvent(newEvent)
                if collateralTargets is None: # Implies that an impassable obstacle exists in between the displacing unit and collateralTargets
                    # Determine obstacle collision for displacing unit...obstacle scenario:
                    maxDisplacementPoint = self.convertToGOT(unitsAndDisplacement[1])
                    displacingUnitPosition = self.convertToGOT(event.castTarget)
                    collisionDict = self.determineObstacleCollisionAndSurfaces(displacingUnitPosition, maxDisplacementPoint)
                else: # Implies that between potential obstacle and displacing unit, there exist other collateral units
                # Determine collision first with units along the path of displacement
                # Upon 'collision' with collateral units, move them as a group if they have 'momentum'
                # If 'momentum' still exists by the time the group reaches an obstacle, determine damage of impact
                
                    self.board.instUM.determineUnitCollision(event.castTarget, collateralTargets, event.displaceDistance, unitsAndDisplacement[2])





                    # Determine obstacle collision 'displaceDistance' distance away for the furthest collateralTarget via LOS check
                    # The last element in the units list should be the "last in line" and closest to any potential obstacle
                    lastCollateralUnitIndex = len(UMcollateralUnits) - 1
                    delta = unitsAndDisplacement[2]
                    displacementAlongAxis = np.array(list(delta)) * np.array(list(event.displaceDistance, event.displaceDistance))
                    newMaxDisplacementPoint = self.convertToGOT(tuple(np.array(list(UMcollateralUnits[lastCollateralUnitIndex].position)) + displacementAlongAxis))
                    displacingUnitPosition = self.convertToGOT(UMcollateralUnits[lastCollateralUnitIndex])
                    collisionDict = self.determineObstacleCollisionAndSurfaces(displacingUnitPosition, maxDisplacementPoint)

                    # Then 
            else:
                # Determine obstacle collision
                pass

    def determineObstacleCollisionAndSurfaces(self, displacingUnitPosition, maxDisplacementPoint):
        """
        I think due to the fact that subdivision will always empty parent nodes of stacks, I have to create a new event
        to be propagated down to the deepest level of nodes which overlap with the query. Otherwise I think the attempt
        to access stacks at higher level nodes will result in some kind of unboundLocalError?

        Since the event involved is not one that requires passage through the dispatcher, I decided to prefix it with
        'me' meaning 'mini event' lol. This architecture as well as the instance above of creating another eTargetsInRange
        event without passing it first through the dispatcher doesn't feel very clean but whatever for now I guess.
        """
        newmEvent = e.meCollision(displacingUnitPosition, maxDisplacementPoint)
        queriedStacks = self.propagateEvent(newmEvent) # keys: stack position, stackZ, surfaces, obstructing bool
        orderedStacks = []
        for stack in queriedStacks:
            deltaCoord= abs(np.array(list(event.castTarget.position)) - np.array(list(stack.get("position"))))
            deltaInt = deltaCoord[0] + deltaCoord[1]
            orderedStacks.append((stack, deltaInt))
        orderedStacks.sort(key=lambda x: x[1])
        queuedSurfaces = []
        for stack in orderedStacks:
            if stack.get("obstructing"):
                displacementEndPoint = stack.get("position")
                break
            else:
                for surface in stack.get("surfaces"): # compile all surfaces to parse through later to inflict status conditions if applicable
                    queuedSurfaces.append(surface)
        collisionDict = {}
        collisionDict["displacementEndPoint"] = displacementEndPoint
        collisionDict["surfaces"] = queuedSurfaces

        return collisionDict

    def convertToGOT(self, position):
        newY = len(self.board.instUM.map) - 1 - position[0]
        return (position[1], newY)

    def propagateEvent(self, event):
        # Check if the event affects the current node
        if self.isOverlapping(None, event.minPoint, event.maxPoint): # NOT SURE IF THIS CHECK IS NECESSARY! But maybe necessary due to the recursiveness of this method?
            # Handle the event at the current node level
            return self.processEvent(event)
        
        # If there are children, propagate the event down
        if self.children:
            for child in self.children:
                child.propagateEvent(event)
                self.fprint("propagate!\n")


    def processEvent(self, event):           
        if isinstance(event, e.eMove):
            queriedStacks = []
            stacks = self.querySpace(event.minPoint, event.maxPoint)
            for stack in stacks:
                for direction, position in self.board.getAdjDirections(event.unit).items():
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

                if event.unit.position == stack[0].position:
                    stackDict = {}
                    stackDict["direction"] = "UNIT"                        
                    stackDict["position"] = event.unit.position
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


        if isinstance(event, e.meCollision):
            queriedStacks = []
            stacks = self.querySpace(event.minPoint, event.maxPoint)
            for stack in stacks:
                stackZ = 0
                surfaces = []
                for gameObject in stack:
                    if isinstance(gameObject, go.Surface):
                        surfaces.append(gameObject)
                    else:
                        stackZ += gameObject.z

                stackDict["position"] = stack[0].position
                stackDict["stackZ"] = stackZ
                stackDict["surfaces"] = surfaces
                if stackZ > 0:
                    stackDict["obstructing"] = True
                else:
                    stackDict["obstructing"] = False

                queriedStacks.append(stackDict)

            return queriedStacks
        
        if isinstance(event, e.eTargetsInRange):      
            stacks = self.querySpace(event.minPoint, event.maxPoint)
            pathInvalid = False
            for stack in stacks: # ASSUMING only stacks within the same row/col are returned!
                # in the future, if casting unit and target unit are on same z-level of map, may decide to implement height of units as being factor for determining target validity (for deciding if 'taking cover' is possible)
                totalZ = 0 
                for object in stack:
                    totalZ += object.z
                if totalZ > 0: # for now will make target invalid if there is anything with z > 0 in the path
                    pathInvalid = True
                    break
            
            if pathInvalid:
                return None
            
            else:
                return event.checkUnit
            
    def checkforObstructions(self, event, validUnits):
                viableTargets = []
                castingUnitPosition = self.convertToGOT(event.unit.position)
                event.minPoint = (castingUnitPosition[0], castingUnitPosition[1])
                for unit in validUnits:
                    targetUnitPosition = self.convertToGOT(unit.position)
                    event.maxPoint = (targetUnitPosition[0], targetUnitPosition[1])
                    event.checkUnit = unit
                    validTarget = self.propagateEvent(event)
                    if validTarget:
                        viableTargets.append(validTarget)

                return viableTargets # a list of units

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


