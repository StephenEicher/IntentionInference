import Board as b

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

        # Check if gameObject position is within limits of current node
        if not self.isWithinBounds(stackPosition):
            return False

        if stackPosition not in self.stacks:
            if len(self.stacks) < self.capacity:
                # Initialize a new stack (list) at the key stackPosition if it does not exist
                self.stacks[stackPosition] = []                
            elif self.children:
                for child in self.children:
                    if child.insert(gameObject): # maybe replace with try..
                        return True
                    else:
                        child.subdivide(gameObject) # .. and except?
            else:
                self.subdivide(gameObject)

        # If current node's stack is not full, insert GameObject
        if stackPosition in self.stacks:
            stack = self.stacks[stackPosition]
            if len(stack) < self.defaultStackHeight:
                stack.append(gameObject)
                print(f'Inserting GameObject into stack at ({stackPosition[0]},{stackPosition[1]}) (X,Y) at depth {self.depth}')
                return True

        # if len(stack) == self.defaultStackHeight and not self.isLeaf:
        #     if not self.children:
        #         self.subdivide(gameObject)
        
        # # Attempt to insert the game object into child nodes
        # if self.children:
        #     for child in self.children:
        #         if child.insert(gameObject):
        #             return True

        if len(stack) == self.defaultStackHeight and self.isLeaf:
            raise ValueError(f"Stack at position {stackPosition} is full. Could not insert game object {gameObject}.")
        
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
            for existingGameObject in stack:
                inserted = False
                for child in self.children:
                    if child.insert(existingGameObject):
                        inserted = True
                        break
                if not inserted:
                    raise ValueError(f"Failed to insert existing game object {existingGameObject} into any child node.")

        inserted = False
        for child in self.children:
            if child.insert(gameObject):
                inserted = True
                break
        if not inserted:
            raise ValueError(f"Failed to insert new game object {existingGameObject} into any child node.")

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
        if isinstance(event, b.eMove):
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
        if isinstance(event, b.eMove):
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


