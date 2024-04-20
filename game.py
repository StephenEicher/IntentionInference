import random


class GameObject:
    """
    In-game object class that represents a generic "game object" from which child classes
    for elements, obstacles, units manage corresponding symbols, behavior/interactions. 
    """
    occupied = False

    def __init__(self, symbol):
        self.symbol = symbol
        self.occupied = symbol != '.'


class Elements(GameObject):
    elem_rand_multiplier_bounds = (1, 4)
    

class Terrain(GameObject):
    placeHolder = None

class Water(Elements):
    debugName = 'Water'
    def __init__(self):
        super().__init__('W')


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
    def __init__(self, obstacleScale):
        super().__init__('[]')
        self.obstacleScale = obstacleScale
    """
    Shape generation
        Randomly select a grid area on the board for obstacle generation
        Determine which positions are already occupied by a instance of GameObject
        Randomly select positions within grid area not already occupied
        Store positions in a set
    Placement
        Send stored positions set to Board class for placement
    
    Choose seed which contains a class containing a function for "growing" from the seed
    
    """


class Surface(Terrain):
    placeHolder = None


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
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        print(f'Created a Board instance with dimensions {rows} x {cols}')

    def genBoard(self, elemTypes):
        self.genElems(elemTypes)

    def clearBoard(self):
        for row in self.grid:
            for current_game_object in row:
                current_game_object.reset()

    def getObject(self, row, col):
        return self.grid[row][col]

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
        print("\n--- Starting genElems ---")
        print(f'Input elem_types: {elemTypes}')
        
        if not isinstance(elemTypes, list):
            elemTypes = [elemTypes]
        elemTypes = list(set(elemTypes))

        for elem in elemTypes:
            ref_class_inst = elem()
            print(f'Processing element type {ref_class_inst.debugName} with symbol: {ref_class_inst.symbol}')
            rand_multiplier = random.randint(ref_class_inst.elem_rand_multiplier_bounds[0], ref_class_inst.elem_rand_multiplier_bounds[1])
            print(f'Multiplier for element type {ref_class_inst.debugName}: {rand_multiplier}')

            for _ in range(rand_multiplier): 
                while True:
                    rand_pos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
                    
                    if rand_pos not in self.all_elem_pos and self.getObject(rand_pos[0], rand_pos[1]) is None:
                        self.all_elem_pos.add(rand_pos)
                        self.grid[rand_pos[0]][rand_pos[1]] = elem()
                        break
                
                print(f'Placed element type {elem().symbol} at position {rand_pos}')
            
            print(f'Current element positions: {self.all_elem_pos}')
            
        print("--- Finished genElems ---\n")



    # def boardStats(self):
                

        

           
print("Constructing Gameboard as gb...")
gb = Board(10, 10)
gb.drawBoard()
gb.genBoard([Fire, Water, Air, Earth])
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








