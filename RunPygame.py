import pygame
import time
import Units as u
import config as c
import threading
import sys
import numpy as np
import copy
import queue

class Pygame:
    def __init__(self, game):
        self.c = c.config
        self.game = game

        self.abilityButtons = []
        self.unitButtons = []
        self.unitButtonsToBlit = []
        self.buttonsToBlit = []
        self.spriteButtons = []
        self.unitToMove = None
        self.validDirections = None
        self.prevRects = []
        self.hoveredSprite = None
        self.getTarget = False
        self.getInput = False
        self.actionDictAwaitingTarget = None

        uiElements = {
            "select_hover": pygame.image.load(r".\sprites\select_target_hover.PNG"),
            "select_confirm": pygame.image.load(r".\sprites\select_target_confirm.PNG")
        }
        self.uiElementsScaled = {}
        for name, surface in uiElements.items():
            self.uiElementsScaled[name] = pygame.transform.scale(surface, (self.c.widthFactor, self.c.heightFactor))

    def startup(self):
        pygame.init()
        self.unitsLayer = pygame.Surface((self.c.windowWidth, self.c.windowHeight), pygame.SRCALPHA)
        self.spriteGroup = pygame.sprite.Group()
        
        temp = u.Sprites()
        self.spritesImageDict = temp.spritesDictScaled
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
                if self.getInput:
                    if self.getTarget:
                        self.prevRects = []
                        self.trackMouseHover(mousePos)
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            
                            targetedUnit = self.handleTargeting(mousePos)
                            if targetedUnit is None:
                                continue
                            else:
                                pReturnDict = self.actionDictAwaitingTarget
                                abilityDict = pReturnDict["abilityDict"]
                                abilityDict["targetedUnit"] = targetedUnit
                                pReturnDict["abilityDict"] = abilityDict
                                self.game.actionQueue.put(pReturnDict)
                                self.hoveredSprite = None
                                self.getTarget = False
                    else:
                        mouseTrackReturn = self.trackMouseAndDisplayMove(mousePos)
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            print("click rcvd")
                            mouseClickDict = self.handleMouseInput(mousePos)
                            if mouseClickDict is None and mouseTrackReturn is not None:
                                pReturnDict = mouseTrackReturn
                            elif mouseClickDict is not None:
                                pReturnDict = mouseClickDict
                            else:
                                continue                                         
                            if pReturnDict["type"] == "castAbility":
                                self.getTarget = True
                                self.actionDictAwaitingTarget = pReturnDict
                                #self.game.moveQueue.put(pReturnDict)
                            else: 
                                self.game.actionQueue.put(pReturnDict)

            self.updateScreen()
            clock.tick(30)

        pygame.display.quit()
        pygame.quit()
        self.game.gameOver = True
        self.game.actionQueue.put({}) #This is just to get past the waiting for input portion in the game loop

    def trackMouseAndDisplayMove(self, mousePos):
        self.prevRects = []
        if self.unitToMove is not None and self.unitToMove.canMove is not False:
            spritePos = self.unitToMove.sprite.rect.topleft
            # Relative vector from sprite to mouse
            mouseRelPos = np.array(mousePos) - np.array(spritePos)
            distance = np.linalg.norm(mouseRelPos)
            
            # Calculate angle
            theta = np.rad2deg(np.arctan2(mouseRelPos[1], mouseRelPos[0]))
            if theta < 0:
                theta += 360

            # Increase precision based on distance
            if distance < 50:
                segment_size = 22.5  # More precise
            else:
                segment_size = 45  # Less precise

            dirs = ['E', 'SE', 'S', 'SW', 'W', 'NW', 'N', 'NE']
            index = int((theta + (segment_size / 2)) // segment_size) % 8
            queryDirId = dirs[index]

            key = None
            for dirId, matCoord in self.validDirections.keys():
                if dirId == queryDirId:
                    key = (dirId, matCoord)
                    v = self.validDirections[key]
                    break
            
            if key is None:
                return None
            else:
                image = self.unitToMove.sprite.image.copy()
                image = image.convert_alpha()
                newRect = self.unitToMove.sprite.image.get_rect()
                newRect.topleft = self.unitToMove.sprite.convertToRect((key[1][0], key[1][1]))
                alpha = 128
                image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
                self.prevRects.append((newRect, image))

            return {"type": "move", "directionDict": {key: v}}
        else:
            return None

    # def trackMouseAndDisplayMove(self,mousePos):
    #     self.prevRects = []
    #     if self.unitToMove is not None:
    #         spritePos = self.unitToMove.rect.topleft
    #         #Rel vector to mouse from spite
    #         mouseRelPos = np.array(mousePos) - np.array(spritePos)
    #         #flip y
    #         # mouseRelPos[1] = mouseRelPos[1]
    #         theta = np.rad2deg(np.arctan2(mouseRelPos[1], mouseRelPos[0]))
    #         dirs = ['E', 'SE', 'S', 'SW', 'W', 'NW','N', 'NE']
    #         # Compute the index by dividing the angle by 45 and rounding to the nearest integer
    #         # Adding 0.5 before taking int to handle rounding correctly
    #         index = int((theta + 22.5) // 45) % 8

    #         # Get the direction
    #         queryDirId = dirs[index]
    #         key = None
    #         for i, (dirId, matCoord) in enumerate(self.validDirections.keys()):
    #             if dirId == queryDirId:
    #                 key = (dirId, matCoord)
    #                 v = self.validDirections[key]
    #                 break
    #         if key is None:
    #             return None
    #         else:
    #             image = self.unitToMove.image
    #             image = image.convert_alpha()
    #             newRect = self.unitToMove.image.get_rect()
    #             newRect.topleft = self.unitToMove.convertToRect((key[1][0], key[1][1]))
    #             alpha = 128
    #             image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
    #             self.prevRects.append((newRect, image))

    #         return {"type": "move", "directionDict": {key: v}}
       
    #     else:
    #         return None

    def drawSelectUnit(self, unitRefs):
        # self.buttonsToBlit = []  # Initialize the list to store buttons and text
        self.unitButtonsToBlit = []
        self.unitButtons = []
        self.game.getInput = True
        for i, unit in enumerate(unitRefs):
            buttonRect = pygame.Rect((720 + 144), (50 * (len(unitRefs) - i)), 50, 40)  # Adjust dimensions as needed
            image = unit.sprite.image
            self.unitButtonsToBlit.append((buttonRect, image, buttonRect, (0, 0, 255)))
            self.unitButtons.append((buttonRect, unit))

    def drawButtons(self, validAbilities, unit):
        self.buttonsToBlit = []  # Initialize the list to store buttons and text
        self.unitToMove = unit

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
        for buttonRect, unit in self.unitButtons:
            if buttonRect.collidepoint(mousePos):
                return {"type": "unit", "unit": unit}
        for buttonRect, abilityDict in self.abilityButtons:
            if buttonRect.collidepoint(mousePos):
                return {"type": "castAbility", "abilityDict": abilityDict}
        return None

    def trackMouseHover(self, mousePos):
        self.hoveredSprite = None  # Reset hovered sprite before checking
        for sprite in self.spriteGroup:
            if sprite.rect.collidepoint(mousePos):
                self.hoveredSprite = sprite
                self.displayStats(self.hoveredSprite)
                break  # Stop checking once a hovering sprite is found

    def displayStats(self, sprite):
        pass

    def handleTargeting(self, mousePos):
        for sprite in self.spriteGroup:
            if sprite.rect.collidepoint(mousePos):
                return sprite.parent
                print("not within range!")
                    
    def updateScreen(self):
        self.unitsLayer.fill((0, 0, 0, 0))  # Clear units layer with transparent black
        self.spriteGroup.draw(self.unitsLayer)  # Draw units on the units layer
        if self.hoveredSprite is not None:
            self.unitsLayer.blit(self.uiElementsScaled["select_hover"], self.hoveredSprite.rect)

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
        