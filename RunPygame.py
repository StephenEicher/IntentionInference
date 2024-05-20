import pygame
import time
import Units as u
import config as c
import threading
import queue
import sys

class Pygame:
    def __init__(self, game):
        self.c = c.config
        self.game = game

        self.directionButtons = []
        self.abilityButtons = []
        self.buttonsToBlit = []

    def startup(self):
        pygame.init()
        self.unitsLayer = pygame.Surface((self.c.windowWidth, self.c.windowHeight), pygame.SRCALPHA)
        self.unitsGroup = pygame.sprite.Group()

        self.sprites = u.Sprites()
        self.spritesImageDict = self.sprites.spritesDictScaled
        self.screen = pygame.display.set_mode((self.c.windowWidth, self.c.windowHeight))

    def pygameLoop(self):
        self.startup()
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
                            pReturnDict = self.handleMouseInput(mousePos)
                            if not pReturnDict:
                                continue
                            if pReturnDict["type"] == "move":
                                self.game.moveQueue.put(pReturnDict)                 
                            if pReturnDict["type"] == "castAbility":
                                self.game.moveQueue.put(pReturnDict)
            
            self.updateScreen()
            clock.tick(30)

        pygame.display.quit()
        pygame.quit()
        
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
            dText = font.render(directionName, True, (0, 0, 0))
            dTextRect = dText.get_rect(center=buttonRect.center)
            self.buttonsToBlit.append((dText, dTextRect))
            # self.screen.blit(dText, dTextRect)

        # Draw buttons for valid abilities
        self.abilityButtons = []
        for i, ability in enumerate(validAbilities):
            buttonRect = pygame.Rect(10, self.screen.get_height() - (50 * (len(validAbilities) - i)), 200, 40)  # Adjust dimensions as needed
            pygame.draw.rect(self.screen, (255, 0, 0), buttonRect)  # Red button
            abilityName = ability["name"]
            self.abilityButtons.append((buttonRect, ability))
            # Render text on button (ability name)
            font = pygame.font.Font(None, 24)
            aText = font.render(abilityName, True, (0, 0, 0))
            aTextRect = aText.get_rect(center=buttonRect.center)
            self.buttonsToBlit.append((aText, aTextRect))
            # self.screen.blit(aText, aTextRect)

        # for text, rect in self.buttonsToBlit:
        #     self.screen.blit(text, rect)

        # pygame.display.update()

    def handleMouseInput(self, mousePos):
        for buttonRect, directionDict in self.directionButtons:
            if buttonRect.collidepoint(mousePos):
                print(directionDict)
                return {"type": "move", "directionDict": directionDict}
        for buttonRect, abilityDict in self.abilityButtons:
            if buttonRect.collidepoint(mousePos):
                print(abilityDict)
                return {"type": "castAbility", "abilityDict": abilityDict}
        return None

    def updateScreen(self):
        print('!')
        self.unitsLayer.fill((0, 0, 0, 0))  # Clear units layer with transparent black
        self.unitsGroup.draw(self.unitsLayer)  # Draw units on the units layer

        self.screen.fill((0, 0, 0))  # Clear the screen with black
        self.screen.blit(self.unitsLayer, (0, 0))  # Blit the units layer onto the screen

        # # Blit all text elements onto the screen
        for text, rect in self.buttonsToBlit:
            self.screen.blit(text, rect)

        pygame.display.update()  # Update the display