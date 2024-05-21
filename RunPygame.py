import pygame
import time
import Units as u
import config as c
import threading
import queue
import sys
import numpy as np
import copy

class Pygame:
    def __init__(self, game):
        self.c = c.config
        self.game = game

        self.abilityButtons = []
        self.unitButtons = []
        self.unitButtonsToBlit = []
        self.buttonsToBlit = []
        self.unitToMove = None
        self.validDirections = None
        self.prevRects = []

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
            mousePos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quit event detected")
                    run = False
                if self.game.getInput:

                    mouseTrackReturn = self.trackMouseAndDisplayMove(mousePos)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            pReturnDict = self.handleMouseInput(mousePos)
                            if pReturnDict is None:
                                pReturnDict = mouseTrackReturn
                            if not pReturnDict:
                                continue
                            if pReturnDict["type"] == "move":
                                self.game.moveQueue.put(pReturnDict)                 
                            if pReturnDict["type"] == "castAbility":
                                self.game.moveQueue.put(pReturnDict)
                            if pReturnDict["type"] == "unit":
                                self.game.moveQueue.put(pReturnDict)

            
            self.updateScreen()
            clock.tick(30)

        pygame.display.quit()
        pygame.quit()
        self.game.gameOver = True
        self.game.moveQueue.put({}) #This is just to get past the waiting for input portion in the game loop
    

    def trackMouseAndDisplayMove(self,mousePos):
        self.prevRects = []
        if self.unitToMove is not None:
            spritePos = self.unitToMove.rect.topleft
            #Rel vector to mouse from spite
            mouseRelPos = np.array(mousePos) - np.array(spritePos)
            #flip y
            # mouseRelPos[1] = mouseRelPos[1]
            theta = np.rad2deg(np.arctan2(mouseRelPos[1], mouseRelPos[0]))
            dirs = ['E', 'SE', 'S', 'SW', 'W', 'NW','N', 'NE']
            # Compute the index by dividing the angle by 45 and rounding to the nearest integer
            # Adding 0.5 before taking int to handle rounding correctly
            index = int((theta + 22.5) // 45) % 8

            # Get the direction
            queryDirId = dirs[index]
            key = None
            for i, (dirId, matCoord) in enumerate(self.validDirections.keys()):
                if dirId== queryDirId:
                    key = (dirId, matCoord)
                    v = self.validDirections[key]
                    break
            if key is None:
                return None
            else:
                image = self.unitToMove.image
                image = image.convert_alpha()
                newRect = self.unitToMove.image.get_rect()
                newRect.topleft = self.unitToMove.convertToRect((key[1][0], key[1][1]))
                alpha = 128
                image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
                self.prevRects.append((newRect, image))

            return {"type": "move", "directionDict": {key: v}}
       
        else:
            return None

    def drawSelectUnit(self, unitIDs, unitRefs):
        # self.buttonsToBlit = []  # Initialize the list to store buttons and text
        self.game.getInput = True
        for i, id in enumerate(unitIDs):
            buttonRect = pygame.Rect((720 + 144), (50 * (len(unitRefs) - i)), 50, 40)  # Adjust dimensions as needed
            image = unitRefs[i].image
            self.unitButtonsToBlit.append((buttonRect, image, buttonRect, (0, 0, 255)))
            self.unitButtons.append((buttonRect, id))

    def drawButtons(self, validDirections, validAbilities, unit):

        self.buttonsToBlit = []  # Initialize the list to store buttons and text
        self.unitToMove = unit
        self.validDirections = validDirections

        # Draw buttons for valid abilities
        for i, ability in enumerate(validAbilities):
            buttonRect = pygame.Rect(10, self.screen.get_height() - (50 * (len(validAbilities) - i)), 200, 40)  # Adjust dimensions as needed
            self.abilityButtons.append((buttonRect, ability))

            # Render text on button (ability name)
            font = pygame.font.Font(None, 24)
            abilityName = ability["name"]
            aText = font.render(abilityName, True, (0, 0, 0))
            aTextRect = aText.get_rect(center=buttonRect.center)
            color = (255, 0, 0)
            self.buttonsToBlit.append((buttonRect, aText, aTextRect, color))

    def handleMouseInput(self, mousePos):
        for buttonRect, unitId in self.unitButtons:
            if buttonRect.collidepoint(mousePos):
                print(unitId)
                return {"type": "unit", "unit": unitId}
        for buttonRect, abilityDict in self.abilityButtons:
            if buttonRect.collidepoint(mousePos):
                print(abilityDict)
                return {"type": "castAbility", "abilityDict": abilityDict}
        return None
    


    def updateScreen(self):
        self.unitsLayer.fill((0, 0, 0, 0))  # Clear units layer with transparent black
        self.unitsGroup.draw(self.unitsLayer)  # Draw units on the units layer

        self.screen.fill((0, 0, 0))  # Clear the screen with black
        self.screen.blit(self.unitsLayer, (0, 0))  # Blit the units layer onto the screen

        for (rect, image) in self.prevRects:
            self.screen.blit(image, rect)

        # Blit all text elements and draw rectangles onto the screen
        for buttonRect, text, rect, color in self.unitButtonsToBlit:
            pygame.draw.rect(self.screen, color, buttonRect)  # Draw the rectangle
            if text is not None:
                self.screen.blit(text, rect)  # Blit the text on top of the rectangle

        # Blit all text elements and draw rectangles onto the screen
        for buttonRect, text, rect, color in self.buttonsToBlit:
            pygame.draw.rect(self.screen, color, buttonRect)  # Draw the rectangle
            if text is not None:
                self.screen.blit(text, rect)  # Blit the text on top of the rectangle

        pygame.display.update()  # Update the display
        