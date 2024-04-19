


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


class Board:
    """
    Board class which stores the map representation
    genBoard() - Procedural generation of game board at initial state
    genBoardForAgent() - Create a copy of the game board for the agent
    """
    
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # self.p1_row = 0
        # self.p1_col = 0
        # self.p2_row = 1
        # self.p2_col = 1
        # self.p1_pos = (self.p1_row, self.p1_col)
        # self.p2_pos = (self.p2_row, self.p2_col)
        self.grid = [[GameObject('.') for _ in range(self.cols)] for _ in range(self.rows)]

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

    def drawBoard(self):
        for row in self.grid:
            rowtoprint = ''.join(currGO.symbol for currGO in row)
            print(rowtoprint)

    def genElems(self, elem_types):
        print(f'Calling on genElems with {elem_types}') 
        elem_types = set(elem_types)
        print(f'Elems included: {elem_types}')
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
            elem_symbol = GameObject(included_elems_symbols[elem])
            print(f'Corresponding elem symbols: {elem_symbol}')
            all_elem_pos = set()
            rand_multiplier = random.randint(1,5)
            for _ in range(rand_multiplier): 
                while True:
                    rand_row = random.randint(0, self.rows - 1)
                    rand_col = random.randint(0, self.cols - 1)
                    rand_pos = (rand_row, rand_col)
                    
                    if rand_pos not in all_elem_pos and self.grid[rand_pos[0]][rand_pos[1]].occupied == False:
                        all_elem_pos.add(rand_pos)
                        self.grid[rand_pos[0]][rand_pos[1]].symbol = elem_symbol
                        break


                

        

           

              
      


       
class Agent:
  """
    Methods: selectAction()
    getActionSpace()
  """
def __init__(self, index=0):
    self.index = index

def selectAction(self, board):
    """
    The Agent will receive a GameState (from either) and
    must return an action from the direction space
    """
    raiseNotDefined()

def getActionSpace(self, board):
   """
    Return a list of all possible actions for the agent
   """
class Game:
   """
   Manager class which oversees turns and game
   startGame()
   """
   
class Unit:
    """
    Manager class which oversees turns and game


    """  








