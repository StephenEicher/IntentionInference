import pygame
import time
import Units as u
import config as c
import threading
import queue
import sys

class Pygame:
    def __init__(self, game):
        pygame.init()
        config = c.config
        self.game = game

        self.screen = pygame.display.set_mode((config.windowWidth, config.windowHeight))

        self.unitsLayer = pygame.Surface((config.windowWidth, config.windowHeight), pygame.SRCALPHA)
        self.unitsGroup = pygame.sprite.Group()

        self.sprites = u.Sprites()
        self.spritesImageDict = self.sprites.spritesDictScaled

        self.directionButtons = []
        self.abilityButtons = []

    # def logicAI(self):
    #     while not self.game.gameOver:
    #         currentAgent = self.game.allAgents[self.agentTurnIndex]
    #         selectedUnit = currentAgent.selectUnit()
    #         while selectedUnit.unitValidForTurn():
    #             moveDict = currentAgent.selectMove(selectedUnit, self.board)
    #             self.board.updateBoard(selectedUnit, moveDict)

    def pygameLoop(self):
        print('Starting pygameLoop')
        # for agent in self.game.allAgents:
        #     if type(agent) != self.game.HumanAgent:
        #         AIThread = threading.Thread(target=self.inclAI)
        #         AIThread.daemon = True
        #         AIThread.start()

        clock = pygame.time.Clock()
        run = True

        while run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quit event detected")
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game.getInput:
                        if event.button == 1:
                            mousePos = pygame.mouse.get_pos()
                            print(mousePos)

                            pReturnDict = self.handleMouseInput(mousePos)
                            if pReturnDict["type"] == "move":
                                self.game.moveQueue.put(pReturnDict["directionDict"])                 
                            if pReturnDict["type"] == "castAbility":
                                self.game.moveQueue.put(pReturnDict["abilityDict"])

                

            clock.tick(30)

        pygame.display.quit()
        pygame.quit()

                # if event.type == pygame.MOUSEBUTTONDOWN:
                #     if self.game.getInput:
                #         if event.button == 1:
                #             mousePos = pygame.mouse.get_pos()
                #             print(mousePos)

                #             pReturnDict = self.handleMouseInput(mousePos)
                #             if pReturnDict["type"] == "move":
                #                 self.game.moveQueue.put(pReturnDict["directionDict"])                 
                #             if pReturnDict["type"] == "castAbility":
                #                 self.game.moveQueue.put(pReturnDict["abilityDict"])
        
            # self.updateScreen()

    def drawButtons(self, validDirections, validAbilities):
        # Draw buttons for valid directions
        self.directionButtons = []
        for directionTuple, v in validDirections.items():
            buttonRect = pygame.Rect(10, 50 * len(self.directionButtons), 100, 40)  # Adjust dimensions as needed
            pygame.draw.rect(self.screen, (0, 255, 0), buttonRect)  # Green button
            directionName = directionTuple[0]
            self.directionButtons.append((buttonRect, {directionTuple : v}))
            # Render text on button (direction)
            font = pygame.font.Font(None, 24)
            text = font.render(directionName, True, (0, 0, 0))
            textRect = text.get_rect(center=buttonRect.center)
            self.screen.blit(text, textRect)

        # Draw buttons for valid abilities
        self.abilityButtons = []
        for i, ability in enumerate(validAbilities):
            buttonRect = pygame.Rect(10, self.screen.get_height() - (50 * (len(validAbilities) - i)), 200, 40)  # Adjust dimensions as needed
            pygame.draw.rect(self.screen, (255, 0, 0), buttonRect)  # Red button
            abilityName = ability["name"]
            self.abilityButtons.append((buttonRect, ability))
            # Render text on button (ability name)
            font = pygame.font.Font(None, 24)
            text = font.render(abilityName, True, (0, 0, 0))
            textRect = text.get_rect(center=buttonRect.center)
            self.screen.blit(text, textRect)

    def handleMouseInput(self, mousePos):
        for buttonRect, directionDict in self.directionButtons:
            if buttonRect.collidepoint(mousePos):
                return {"type": "move", "directionDict": directionDict}
        for buttonRect, abilityDict in self.abilityButtons:
            if buttonRect.collidepoint(mousePos):
                return {"type": "castAbility", "abilityDict": abilityDict}
        return None

    def updateScreen(self):
        # self.unitsLayer.fill((0,0,0,0))
        # self.unitsGroup.draw(self.unitsLayer)
        # self.screen.fill((0,0,0))
        # self.screen.blit(self.unitsLayer, (0,0))

        pygame.display.flip()

# validDirections = {
#     ('E', (0, 1)):(False, []),
#     ('SE', (1, 1)):(False, []),
#     ('S', (1, 0)):(False, [])
# }
# validAbilities = [
# {'name':'Hide',
# 'cost':1,
# 'range':0,
# 'events':[{'type': 'hide', 'target': 'self'}]}
# ]

# a = Pygame(None)
# pygameThread = threading.Thread(target = a.pygameLoop)
# pygameThread.daemon = True
# pygameThread.start()
# moveQueue = queue.Queue(maxsize = 1)
# # a.drawButtons(validDirections, validAbilities)
# # moveQueue = queue.Queue(maxsize = 1)
# while True:
#     if moveQueue.get():
#         break