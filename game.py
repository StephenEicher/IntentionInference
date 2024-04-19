


#Python script to define Game, Unit, Agent, and Board sub classes

import random


class GameObject:
    """
    In-game object class that manages symbols on the board representing agents,
    elements, obstacles, and movable points of space. It also tracks the statuses
    of elements (undiscovered vs. discovered, uncaptured vs. captured).
    """
    occupied = False

    def __init__(self, symbol):
        self.symbol = symbol
        self.occupied = symbol != '.'
        
   

#This is a "Fire" class - a child of GameObject 

class Elements(GameObject):
    elem_rand_multiplier_bounds = (1,4)
    discovered = False
    captured = None

class Fire(Elements):
    debugName = 'Fire'
    elem_rand_multiplier_bounds = (1,1)
    def __init__(self):
        #This is a call to the parent class constructor
        super().__init__('F')
        #The terminology "Super" here is referring to the "Super Class", GameObject
        #In this context, Fire is a subclass of the superclass GameObject

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

    def getObj(self, row, col):
        return self.grid[row][col]
    
    def drawBoard(self):
        for row in self.grid:
            row_to_print = ''
            for entry in row:
                if entry is not None:
                    #If the entry is not empty, append that game object's symbol
                    row_to_print = row_to_print + entry.symbol
                else:
                    #Otherwise, put the default "Empty" symbol
                    row_to_print = row_to_print + self.emptySymbol
            print(row_to_print)

    def genElems(self, elemTypes):
        print("\n--- Starting genElems ---")
        print(f'Input elem_types: {elemTypes}')
        
        if type(elemTypes) != list:
            #This is a check for if a singleton argument is passed in instead of a list
            elemTypes = [elemTypes]
        #Converting to a set removes duplicates
        elemTypes = list(set(elemTypes))
        for elem in elemTypes:
            ref_class_inst = elem()
            print(f'Processing element type {ref_class_inst.debugName} with symbol: {ref_class_inst.symbol}')
            rand_multiplier = random.randint(ref_class_inst.elem_rand_multiplier_bounds[0], ref_class_inst.elem_rand_multiplier_bounds[1])
            print(f'Multiplier for element type {ref_class_inst.debugName}: {rand_multiplier}')
            
            for _ in range(rand_multiplier): 
                while True:
                    rand_pos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
                    
                    if rand_pos not in self.all_elem_pos and self.getObj(rand_pos[0],rand_pos[1]) == None:
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
gb.genBoard(Fire)


       
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








