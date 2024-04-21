import random



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
    elem_rand_multiplier_bounds = (1, 4)
    

class Terrain(GameObject):
    pass


class Obstacles(Terrain):
    pass
  #def genNeighbors(gb where gb is the game board that self lives on)
        #Note: you may want to consider storing on GameObjects or children the location of each game object (row, col)
        #Otherwise, you may need to pass in row, col as an input
        #Query neighboring tiles to determine if the neighbors are valid points to insert new obstacles
            #For the points that are valid, insert new Obstacle instances into the neighboring row, col
                #Insert the obstances by assigning gb.grid[row][col]


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


class Seed(Obstacles):
    debugName = 'Seed'
    symbol = '[]'
    def __init__(self, pos, board_class_instance):
        self.pos = pos
        self.board_class_instance = board_class_instance
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
            
            # Check if the new position is within the grid bounds
            if 0 <= newRow < self.board_class_instance.rows and 0 <= newCol < self.board_class_instance.cols:
                new_root_pos = (newRow, newCol)
                adjacentObject = self.board_class_instance.grid[newRow][newCol]
                
                # If the adjacent tile is unoccupied, create a new Root object
                if adjacentObject is None or not adjacentObject.occupied:
                    newRoot = Root(new_root_pos, self.board_class_instance)
                    self.board_class_instance.grid[newRow][newCol] = newRoot


class Root(Seed):
    debugName = 'Root'
    symbol = '~'
    def __init__(self, new_root_pos, board_class_instance):
        super().__init__(new_root_pos, None)
        self.board_class_instance = board_class_instance

    # def weightedProliferate(self):


class Surface(Terrain):
    debugName = 'Surface'
    pass


class Board:
    """
    Board class which stores the map representation
    genBoard() - Procedural generation of game board at initial state
    genBoardForAgent() - Create a copy of the game board for the agent
    """
    emptySymbol = '.' 

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.all_elem_pos = set()
        self.all_seed_pos = set()
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        print(f'Created an empty Board instance with dimensions {self.rows} x {self.cols}')

    def genBoard(self, elemTypes):
        self.genElems(elemTypes)

    def clearBoard(self):
        for row in self.grid:
            for current_game_object in row:
                current_game_object.reset()

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
            row_to_print = ''
            for entry in row:
                if entry is not None:
                    row_to_print += entry.symbol
                else:
                    row_to_print += self.emptySymbol
            print(row_to_print)
    
    def genElems(self, elemTypes):
        print('\n--- Starting genElems ---')
        elem_debug_name = ''
        for elem in elemTypes:
            elem_debug_name += elem.debugName + ' '
        print(f'Input elemTypes: {elem_debug_name}')
        if not isinstance(elemTypes, list):
            elemTypes = [elemTypes]
        elemTypes = list(set(elemTypes))

        for elem in elemTypes:
            ref_class_inst = elem(None)
            print(f'Processing element type {ref_class_inst.debugName} with symbol: {ref_class_inst.symbol}')
            randMultiplier = random.randint(ref_class_inst.elem_rand_multiplier_bounds[0], ref_class_inst.elem_rand_multiplier_bounds[1])
            print(f'Multiplier for element type {ref_class_inst.debugName}: {randMultiplier}')

            for _ in range(randMultiplier): 
                while True:
                    rand_elem_pos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
                    
                    if rand_elem_pos not in self.all_elem_pos and self.getObject(rand_elem_pos[0], rand_elem_pos[1]) == None:
                        self.all_elem_pos.add(rand_elem_pos)
                        self.grid[rand_elem_pos[0]][rand_elem_pos[1]] = elem(rand_elem_pos)
                        break
                
                print(f'Placed element type {elem(None).symbol} at position {rand_elem_pos}')
            
            print(f'Current element positions: {self.all_elem_pos}')
            
        print('--- Finished genElems ---\n')

    def genObstacles(self, seedMultiplier):
        print('\n--- Starting genObstacles ---')
        print(f'Input seedMultiplier: {seedMultiplier}')
        for _ in range(seedMultiplier):
            while True:
                rand_seed_pos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
               
                if self.getObject(rand_seed_pos[0], rand_seed_pos[1]) == None:
                    newSeed = Seed(rand_seed_pos, self)
                    self.all_seed_pos.add(rand_seed_pos)
                    self.grid[rand_seed_pos[0]][rand_seed_pos[1]] = newSeed
                    newSeed.proliferate()
                    break

            print(f'Placed seed at position {rand_seed_pos}')
        
        print(f'Current seed positions: {self.all_seed_pos}')
            
        print('--- Finished genObstacles ---\n')

        #Choose some points to function as "centers" for the barriers
        #  Make sure the points we've chosen are not occupied
        #   For the points that are valid, insert a Obstacle instance at that Row, Col
                #On the obstacle instance we just created, call newObstacle.genNeighbors(self (where self is this board class))
                    #The newObstacle.genNeighbor function will modify in place the current grid
                    #You may be able to modify the board in place but I"m not totally sure
                    #If you cannot modify the board in place the output will look like this:
                    #self.grid = newObstacle.genNeighbor(self.grid)


    #Index becomes the prev value + 1
    #index = index + 1 #Normal modification

    #Index becomes the prev value +1
    #incrementIndex(go.index) #Modification in place

    #on your go:
    # def incrementIndex(self.index)
    #   self.index = self.index + 1


    # def boardStats(self):
                

        

           
print("Constructing Gameboard as gb...")
gb = Board(20, 20)
gb.drawBoard()
gb.genElems([Water, Fire])
gb.genObstacles(3)
gb.drawBoard()

       
# class Agent:
#   """
#     Methods: selectAction()
#     getActionSpace()
#   """
# def __init__(self, index=0):
#     self.index = index

# def selectAction(self, board):
#     """
#     The Agent will receive a GameState (from either) and
#     must return an action from the direction space
#     """
#     raiseNotDefined()

# def getActionSpace(self, board):
#    """
#     Return a list of all possible actions for the agent
#    """



# class Game:
#    """
#    Manager class which oversees turns and game
#    startGame()
#    """



# class Unit:
#     """
#     Manager class which oversees turns and game
#     """  








