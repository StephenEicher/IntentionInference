


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
        self.discovered = False
        self.captured = False
        self.occupied = symbol != '.'

    def reset(self):
        self.symbol = '.'
        self.discovered = False
        self.captured = False
        self.occupied = False

#This is a "Fire" class - a child of GameObject 
class Fire(GameObject):
    debugName = 'Fire'
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
        # self.p1_row = 0
        # self.p1_col = 0
        # self.p2_row = 1
        # self.p2_col = 1
        # self.p1_pos = (self.p1_row, self.p1_col)
        # self.p2_pos = (self.p2_row, self.p2_col)
        self.all_elem_pos = set()
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        print(f'Created a Board instance with dimensions {rows} x {cols}')

    def genBoard(self, elem_types):
        self.genElems(elem_types)

    # def genRandBoard(self):
    #     relem_type_total = 
    #     relem_total = 
    #     robstacle_total = 
    #     robstacle_type_total = 
        # self.genElem(relem_type_total, relem_total)
        # self.genObstacle(robstacle_type_total, robstacle_total)
    def clearBoard(self):
        for row in self.grid:
            for currGO in row:
                currGO.reset()
    def getObj(self, row, col):
        return self.grid[row][col]
    def drawBoard(self):
        for row in self.grid:
            rowToPrint = ''
            for entry in row:
                if entry is not None:
                    #If the entry is not empty, append that game object's symbol
                    rowToPrint = rowToPrint + entry.symbol
                else:
                    #Otherwise, put the default "Empty" symbol
                    rowToPrint = rowToPrint + self.emptySymbol
            print(rowToPrint)

    def genElems(self, elem_types):
        print("\n--- Starting genElems ---")
        print(f'Input elem_types: {elem_types}')

        """
        Leaving this code for you to reference in case you weren't done with it - 


        elem_types = set(elem_types)
        included_elems = {
            'water': False,
            'earth': False,
            'fire': False,
            'air': False,
        }
        included_elems_symbols = {
            0: 'W',
            1: 'E',
            2: 'F',
            3: 'A',
        }
        
        for elem in elem_types:
            if elem == 0:
                included_elems['water'] = True
            elif elem == 1:
                included_elems['earth'] = True
            elif elem == 2:
                included_elems['fire'] = True
            elif elem == 3:
                included_elems['air'] = True
            
            elem_gameObject = GameObject(included_elems_symbols[elem])
            print(f'Processing element type {elem} with symbol: {elem_gameObject.symbol}')
            
            rand_multiplier = random.randint(1, 3)
            print(f'Multiplier for element type {elem}: {rand_multiplier}')
            
            for _ in range(rand_multiplier): 
                while True:
                    rand_row = random.randint(0, self.rows - 1)
                    rand_col = random.randint(0, self.cols - 1)
                    rand_pos = (rand_row, rand_col)
                    
                    if rand_pos not in self.all_elem_pos and self.grid[rand_pos[0]][rand_pos[1]]== None:
                        self.all_elem_pos.add(rand_pos)
                        self.grid[rand_pos[0]][rand_pos[1]] = elem_gameObject
                        break
                
                print(f'Placed element type {elem} at position {rand_pos}')
            
            print(f'Current element positions: {self.all_elem_pos}')
            
        # print("--- Finished genElems ---\n")
        """
        
        if type(elem_types) != list:
            #This is a check for if a singleton argument is passed in instead of a list
            elem_types = [elem_types]
        #Converting to a set removes duplicates
        elem_types = list(set(elem_types))
        for elem in elem_types:
            print(f'Processing element type {elem().debugName} with symbol: {elem().symbol}')
            rand_multiplier = random.randint(1, 3)
            print(f'Multiplier for element type {elem().debugName}: {rand_multiplier}')
            
            for _ in range(rand_multiplier): 
                while True:
                    rand_pos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
                    
                    if rand_pos not in self.all_elem_pos and self.getObj(rand_pos[0],rand_pos[1] )== None:
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








