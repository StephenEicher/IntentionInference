# Tester to play with pygame
import threading
import pygame
import time
import queue
from typing import Any



class pyGameClass:
    getInput = False
    def __init__(self, displaySize, gcRef):
        self.displaySize = displaySize
        self.gcRef = gcRef

    def startLoop(self):
        pygame.init()
        screen = pygame.display.set_mode(self.displaySize)
        run = True
        while run:
            
            for event in pygame.event.get():
                print(event)
                if event.type == pygame.QUIT:
                    run = False
                
                if event.type == pygame.KEYDOWN:
                    if self.getInput:
                        #This is where we do all of the parsing to actually extract what the move is in terms that are meaningful to the game class
                        self.gcRef.moveQueue.put(event)


        pygame.quit()
        # self.gcRef.quitLoop()


class GameClass: 
    moveQueue = queue.Queue(maxsize=1)
    quit = False
    def __init__(self, displaySize):
        self.pg = pyGameClass(displaySize, self)
        self.player = humanPlayer(self.pg)

    def startup(self):
        print('Starting up Pygame class!')
        #Create a separate thread on which the pygame loop will run
        pyGameThread = threading.Thread(target=self.pg.startLoop)
        pyGameThread.daemon = True
        pyGameThread.start()
        self.runGameLoop()

    def runGameLoop(self):
        run = True
        while run:
            print('.')


            ## If we have a human player, need to communicate move back through queue
            self.player.getMove()

            if not self.moveQueue.empty():
                self.displayMoveQueue()
            

            # If the player is not a human, just straight assign move as output of function
            #selectedMove = getMove()

            if self.quit:
                run = False
                print('Quitting!')
            
    def displayMoveQueue(self):
        if not self.moveQueue.empty():
            print(self.moveQueue.get())
            self.moveQueue.empty()

    def quitLoop(self):
        self.quit = True

class humanPlayer:
    def __init__(self, pyGameRef):
        print("Creating Player Agent")
        self.pg = pyGameRef
    def getMove(self):
        self.pg.getInput = True
    


gc = GameClass((200, 200))
gc.startup()

