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
    def __init__(self, game, maxX, maxY):
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
        self.boardBoundsPx = (maxX * self.c.widthFactor, maxY * self.c.heightFactor)

    def startup(self):
        pygame.init()
        self.unitsLayer = pygame.Surface((self.c.windowWidth, self.c.windowHeight), pygame.SRCALPHA)
        self.spriteGroup = pygame.sprite.Group()
        
        temp = u.Sprites()
        self.spritesImageDict = temp.spritesDictScaled
        self.screen = pygame.display.set_mode((self.c.windowWidth, self.c.windowHeight))
        turnInfoButtonSize = (200, 100)
        self.turnInfoButton = pygame.Rect(0, 0, turnInfoButtonSize[0], turnInfoButtonSize[1])
        self.turnInfoButton.bottomright = (self.screen.get_width(), self.screen.get_height())

        self.rightPanelCenterX = self.screen.get_width()  - 0.5*(self.screen.get_width() - self.boardBoundsPx[0])



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
                            buttonClickDict = self.handleMouseInput(mousePos)
                            if buttonClickDict is not None:
                                if buttonClickDict["type"] == "castAbility":
                                    if buttonClickDict["abilityDict"].get("name") == "End Unit Turn":
                                        self.game.actionQueue.put(buttonClickDict)
                                    else:
                                        self.actionDictAwaitingTarget = buttonClickDict
                                elif  buttonClickDict["type"] == "unit":
                                    self.game.actionQueue.put(buttonClickDict)
                            else:
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
                                if pReturnDict["abilityDict"].get("name") == "End Unit Turn":
                                    self.game.actionQueue.put(pReturnDict)
                                else:
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

            # # Increase precision based on distance
            # if distance < 50:
            #     segment_size = 22.5  # More precise
            # else:
            #     segment_size = 45  # Less precise
            segment_size = 45

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


    def drawSelectUnit(self, unitRefs):
        # self.buttonsToBlit = []  # Initialize the list to store buttons and text
        self.unitButtonsToBlit = []
        self.unitButtons = []
        self.game.getInput = True
        for i, unit in enumerate(unitRefs):
            buttonSize = (100, 100)
            spacing = 10
            buttonRect = pygame.Rect(0, 0, buttonSize[0], buttonSize[1])  # Adjust dimensions as needed
            buttonRect.center = (self.rightPanelCenterX, (buttonSize[1] + spacing)* (len(unitRefs) - i))
            image = unit.sprite.image
            image = pygame.transform.scale(image, buttonRect.size)
            self.unitButtonsToBlit.append((buttonRect, image, buttonRect, (0, 0, 255)))
            self.unitButtons.append((buttonRect, unit))

    def drawButtons(self, validAbilities, unit):
        self.buttonsToBlit = []  # Initialize the list to store buttons and text
        self.abilityButtons = []
        self.unitToMove = unit

        # Draw buttons for valid abilities  
        for i, ability in enumerate(validAbilities):
            #buttonRect = pygame.Rect(10, self.screen.get_height() - (50 * (len(validAbilities) - i)), 200, 40)  # Adjust dimensions as needed
            box_width = 200
            box_spacing = 10
            buttonRect = pygame.Rect((box_width + box_spacing)*i + box_spacing ,self.screen.get_height() - 50, box_width, 40)  # Adjust dimensions as needed
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
        

    def handleTargeting(self, mousePos):
        for sprite in self.spriteGroup:
            if sprite.rect.collidepoint(mousePos):
                return sprite.parent
                print("not within range!")
                    
    def updateScreen(self):
        self.screen.fill((0, 0, 0))  # Clear the screen with black

        #Draw the board in a grey color
        boardRect = pygame.Rect(0, 0, self.boardBoundsPx[0], self.boardBoundsPx[1])
        pygame.draw.rect(self.screen, (100, 100, 100), boardRect)


        
        font = pygame.font.Font(None, 24)
        if self.game is not None:
            if self.game.currentAgent is not None:
                aTurnText = font.render(f'Turn: {self.game.currentAgent.name}', True, (255, 255, 255))
                dy = 10
                turnTextCenter = np.array(self.turnInfoButton.midtop) + np.array((0, 0.5*aTurnText.get_size()[1])) + dy
                aTextRect = aTurnText.get_rect(center= tuple(turnTextCenter))
                pygame.draw.rect(self.screen, (30, 30, 30), self.turnInfoButton)
                self.screen.blit(aTurnText, aTextRect)

        self.screen.blit(self.unitsLayer, (0, 0))  # Blit the units layer onto the screen
        self.unitsLayer.fill((0, 0, 0, 0))  # Clear units layer with transparent black
        
        self.spriteGroup.draw(self.unitsLayer)  # Draw units on the units layer
        if self.hoveredSprite is not None:
            self.unitsLayer.blit(self.uiElementsScaled["select_hover"], self.hoveredSprite.rect)



        

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
        