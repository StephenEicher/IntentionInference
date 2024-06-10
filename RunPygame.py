import pygame
import time
import Units as u
import config as c
import threading
import sys
import numpy as np
import copy
import queue
import SpriteClasses as sc

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
        self.spriteGroup = pygame.sprite.Group()
        self.obstacleGroup = pygame.sprite.Group()
        
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
        

        
        temp = sc.Sprites() # Does this isntance get automatically recycled/'deleted'?
        self.spritesImageDict = temp.spritesDictScaled
        self.screen = pygame.display.set_mode((self.c.windowWidth, self.c.windowHeight))
        turnInfoButtonSize = (self.screen.get_width() - self.boardBoundsPx[0], 50)
        self.turnInfoButton = pygame.Rect(0, 0, turnInfoButtonSize[0], turnInfoButtonSize[1])
        self.turnInfoButton.topright = (self.screen.get_width(), 0)
        self.rightPanelCenterX = self.screen.get_width()  - 0.5*(self.screen.get_width() - self.boardBoundsPx[0])
        self.botPanelCenterY = self.screen.get_height() - 0.5 * (self.screen.get_height() - self.boardBoundsPx[1])


    def pygameLoop(self):
        self.startup()
        clock = pygame.time.Clock()
        run = True
    
        while run:
            mousePos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.fprint("Quit event detected")
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
                                        self.game.pgQueue.put(buttonClickDict)
                                    else:
                                        self.actionDictAwaitingTarget = buttonClickDict
                                elif  buttonClickDict["type"] == "unit":
                                    self.game.pgQueue.put(buttonClickDict)
                            else:
                                targetedUnit = self.handleTargeting(mousePos)
                                if targetedUnit is None:
                                    continue
                                else:
                                    pReturnDict = self.actionDictAwaitingTarget
                                    abilityDict = pReturnDict["abilityDict"]
                                    abilityDict = dict(abilityDict)
                                    abilityDict["targetedUnit"] = targetedUnit.ID
                                    pReturnDict["abilityDict"] = abilityDict
                                    self.game.pgQueue.put(pReturnDict)
                                    self.hoveredSprite = None
                                    self.getTarget = False
                    else:
                        mouseTrackReturn = self.trackMouseAndDisplayMove(mousePos)
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.game.fprint("click rcvd")
                            mouseClickDict = self.handleMouseInput(mousePos)
                            if mouseClickDict is None and mouseTrackReturn is not None:
                                pReturnDict = mouseTrackReturn
                            elif mouseClickDict is not None:
                                pReturnDict = mouseClickDict
                            else:
                                continue                                         
                            if pReturnDict["type"] == "castAbility":
                                if pReturnDict["abilityDict"].get("name") == "End Unit Turn":
                                    self.game.pgQueue.put(pReturnDict)
                                else:
                                    self.getTarget = True
                                    self.actionDictAwaitingTarget = pReturnDict
                                    #self.game.moveQueue.put(pReturnDict)
                            else: 
                                self.game.pgQueue.put(pReturnDict)

            self.updateScreen()
            clock.tick(30)
            if self.game.gameOver:
                run = False
        pygame.display.quit()
        pygame.quit()
        self.game.gameOver = True
        self.game.pgQueue.put(None) #This is just to get past the waiting for input portion in the game loop
        
    def trackMouseAndDisplayMove(self, mousePos):
        self.prevRects = []
        if self.unitToMove is not None and self.unitToMove.canMove is not False:
            spritePos = self.unitToMove.sprite.rect.center
            # Relative vector from sprite to mouse
            mouseRelPos = np.array(mousePos) - np.array(spritePos)
            distance = np.linalg.norm(mouseRelPos)
            
            # Calculate angle
            theta = np.rad2deg(np.arctan2(mouseRelPos[1], mouseRelPos[0]))
            # if theta < 0:
            #     theta += 360
            theta = (theta + 180) % 360 - 180
            theta = round(theta/45) * 45

            
            target_loc = np.array([np.sin(np.deg2rad(theta)), np.cos(np.deg2rad(theta))])
            target_loc = np.round(target_loc, decimals=0)
            target_loc = np.array(target_loc, dtype=int)
            target_loc = target_loc + self.unitToMove.position
            if np.any(np.all(self.validDirections == target_loc, axis=1)):
                image = self.unitToMove.sprite.image.copy()
                image = image.convert_alpha()
                newRect = self.unitToMove.sprite.image.get_rect()
                # newRect.center = spritePos + target_loc_scaled
                newRect.topleft = self.unitToMove.sprite.convertToRect(target_loc)
                alpha = 128
                image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
                self.prevRects.append((newRect, image))   
                return (self.unitToMove.ID, 'move', target_loc)             
            else:
                return None
        
            # dirs = ['E', 'SE', 'S', 'SW', 'W', 'NW', 'N', 'NE']
            # index = int((theta + (segment_size / 2)) // segment_size) % 8
            # # queryDirId = dirs[index]

            # key = None
            # for dirId, matCoord in self.validDirections.keys():
            #     if dirId == queryDirId:
            #         key = (dirId, matCoord)
            #         v = self.validDirections[key]
            #         break
            
            # if key is None:
            #     return None
            # else:
            #     image = self.unitToMove.sprite.image.copy()
            #     image = image.convert_alpha()
            #     newRect = self.unitToMove.sprite.image.get_rect()
            #     newRect.topleft = self.unitToMove.sprite.convertToRect((key[1][0], key[1][1]))
            #     alpha = 128
            #     image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            #     self.prevRects.append((newRect, image))

            # return {"type": "move", "directionDict": {key: v}}
        else:
            return None


    def drawSelectUnit(self, unitRefs):
        try:
            # self.buttonsToBlit = []  # Initialize the list to store buttons and text
            self.unitButtonsToBlit = []
            self.unitButtons = []
            self.game.getInput = True
            for i, unit in enumerate(unitRefs):
                buttonSize = (self.screen.get_width() - self.boardBoundsPx[0], 75)
                imageSize = (75, 75)
                spacing = 10
                buttonRect = pygame.Rect(0, 0, buttonSize[0], buttonSize[1])  # Adjust dimensions as needed
                buttonRect.center = (self.rightPanelCenterX, (buttonSize[1] + spacing)* (len(unitRefs) - i))
                imageRect = pygame.Rect(0, 0, imageSize[0], imageSize[1])
                imageRect.center = (self.rightPanelCenterX, (buttonSize[1] + spacing)* (len(unitRefs) - i))
                image = unit.sprite.image
                image = pygame.transform.scale(image, imageSize)
                self.unitButtonsToBlit.append((buttonRect, image, imageRect, (0, 0, 255)))
                self.unitButtons.append((buttonRect, unit))
        except:
            self.game.fprint('error in drawing select units...')
            time.sleep(0.1)
            self.drawSelectUnit(unitRefs)

    def drawButtons(self, validAbilities, unit):
        self.buttonsToBlit = []  # Initialize the list to store buttons and text
        self.abilityButtons = []
        self.unitToMove = unit

        # Draw buttons for valid abilities  
        for i, abilityClass in enumerate(validAbilities):
            #buttonRect = pygame.Rect(10, self.screen.get_height() - (50 * (len(validAbilities) - i)), 200, 40)  # Adjust dimensions as needed
            box_width = 200
            box_height = 50
            box_spacing = 10
            buttonRect = pygame.Rect((box_width + box_spacing)*i + box_spacing ,self.botPanelCenterY, box_width, box_height)  # Adjust dimensions as needed
            buttonRect.centery = self.botPanelCenterY
            self.abilityButtons.append((buttonRect, abilityClass))
            if abilityClass == -1:
                abilityName = "End Unit Turn"
            else:
                ability = abilityClass(unit)
                abilityName = ability.name  
            # Render text on button (ability name)
            font = pygame.font.Font(None, 24)
            
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
        


   
        try:
            self.spriteGroup.draw(self.unitsLayer)  # Draw units on the units layer
            self.obstacleGroup.draw(self.unitsLayer)
            
            
            
            nSprites = len(self.game.allUnits)
            increment = self.boardBoundsPx[0] / nSprites
            idx = 0
            for sprite in self.spriteGroup:
                if isinstance(sprite.parent, u.Unit):
                    xPx = increment*idx
                    yPx = self.boardBoundsPx[1]+1
                    hpIndRect = pygame.Rect(0,0, increment, 50)
                    hpIndRect.topleft = (xPx, yPx)
                    image = sprite.image
                    self.screen.blit(image, hpIndRect)
                    idx = idx + 1
                    barXpx = xPx + image.get_size()[0]
                    ratio = sprite.parent.currentHP / sprite.parent.HP
                    pygame.draw.rect(self.screen, "red", (barXpx, yPx, increment - image.get_size()[0], image.get_size()[1]))
                    pygame.draw.rect(self.screen, "green", (barXpx, yPx, ratio*(increment - image.get_size()[0]), image.get_size()[1]))

        except:
            self.game.fprint('Warning! Unknown error in sprite group draw')
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
        