import random


class GameObject:
    """
    In-game object class that represents a generic "game object" from which child classes
    for elements, obstacles, units manage corresponding symbols, behavior/interactions. 
    """
    occupied = False

    def __init__(self, symbol, pos):
        self.symbol = symbol
        self.pos = pos
        self.occupied = symbol != '.'


class Elements(GameObject):
    elem_rand_multiplier_bounds = (1, 4)
    

class Terrain(GameObject):
    placeHolder = None

class Water(Elements):
    debugName = 'Water'
    def __init__(self, pos):
        super().__init__('W', pos)


class Earth(Elements):
    debugName = 'Earth'
    def __init__(self):
        super().__init__('E')


class Fire(Elements):
    debugName = 'Fire'
    def __init__(self):
        super().__init__('F')


class Air(Elements):
    debugName = 'Air'
    def __init__(self):
        super().__init__('A')


class Obstacles(Terrain):
    debugName = 'Obstacle'
    def __init__(self):
        super().__init__('[]')


    def genNeighbors(self):
        pass
    #def genNeighbors(gb where gb is the game board that self lives on)
        #Note: you may want to consider storing on GameObjects or children the location of each game object (row, col)
        #Otherwise, you may need to pass in row, col as an input
        #Query neighboring tiles to determine if the neighbors are valid points to insert new obstacles
            #For the points that are valid, insert new Obstacle instances into the neighboring row, col
                #Insert the obstances by assigning gb.grid[row][col]

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
        print(f'Input elem_types: {elemTypes}')
        
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
                    newObstacle = Obstacles()
                    self.all_seed_pos.add(rand_seed_pos)
                    self.grid[rand_seed_pos[0]][rand_seed_pos[1]] = newObstacle
                    break

            print(f'Placed seed at position {rand_seed_pos}')
        
        print(f'Current element positions: {self.all_seed_pos}')
            
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
gb = Board(10, 10)
gb.drawBoard()
gb.genElems([Water])
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








