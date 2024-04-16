


#Python script to define Game, Unit, Agent, and Board sub classes






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


class Board:
    """
    Board class which stores the map representation
    genBoard() - Procedural generation of game board at inital state
    genBoardForAgent() - Create a copy of the game board for the agent
    """


class Unit:
    """
    Manager class which oversees turns and game


    """  
