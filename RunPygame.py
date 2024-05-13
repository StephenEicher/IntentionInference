import pygame
import time
import Units as u
import config as c

class Pygame:
    def __init__(self, game):
        pygame.init()
        config = c.config
        self.game = game

        self.screen = pygame.display.set_mode((config.windowWidth, config.windowHeight))
        self.widget = pygame.display.set_mode((config.widgetWidth, config.widgetHeight))

        self.unitsLayer = pygame.Surface((config.windowWidth, config.windowHeight), pygame.SRCALPHA)
        self.unitsGroup = pygame.sprite.Group()

        self.sprites = u.Sprites()
        self.spritesImageDict = self.sprites.spritesDictScaled

        self.directionButtons = []
        self.abilityButtons = []
        self.pReturnDict = None

    def pygameLoop(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mousePos = pygame.mouse.get_pos()
                        if self.game.getInput:
                            self.pReturnDict = self.handleMouseInput(mousePos)
                            # self.game.moveQueue.put(event)
            
            self.updateScreen

            clock.tick(60)

    def drawButtons(self, validDirections, validAbilities):
        # Draw buttons for valid directions
        self.directionButtons = []
        for directionTuple, v in validDirections.items():
            buttonRect = pygame.Rect(10, 50 * len(self.directionButtons), 100, 40)  # Adjust dimensions as needed
            pygame.draw.rect(self.widget, (0, 255, 0), buttonRect)  # Green button
            directionName = directionTuple[0]
            self.directionButtons.append((buttonRect, {directionTuple : v}))
            # Render text on button (direction)
            font = pygame.font.Font(None, 24)
            text = font.render(directionName, True, (0, 0, 0))
            textRect = text.get_rect(center=buttonRect.center)
            self.widget.blit(text, textRect)

        # Draw buttons for valid abilities
        self.abilityButtons = []
        for i, ability in enumerate(validAbilities):
            buttonRect = pygame.Rect(10, self.widget.get_height() - (50 * (len(validAbilities) - i)), 200, 40)  # Adjust dimensions as needed
            pygame.draw.rect(self.widget, (255, 0, 0), buttonRect)  # Red button
            abilityName = ability["name"]
            self.abilityButtons.append((buttonRect, ability))
            # Render text on button (ability name)
            font = pygame.font.Font(None, 24)
            text = font.render(abilityName, True, (0, 0, 0))
            textRect = text.get_rect(center=buttonRect.center)
            self.widget.blit(text, textRect)

            self.updateScreen()

    def handleMouseInput(self, mousePos):
        for buttonRect, directionDict in self.directionButtons:
            if buttonRect.collidepoint(mousePos):
                self.game.inputReady = True
                return {"type": "move", "directionDict": directionDict}
        for buttonRect, abilityDict in self.abilityButtons:
            if buttonRect.collidepoint(mousePos):
                self.game.inputReady = True
                return {"type": "castAbility", "abilityDict": abilityDict}
        return None

    def updateScreen(self):
        self.unitsLayer.fill((0,0,0,0))
        self.unitsGroup.draw(self.unitsLayer)
        self.screen.blit(self.unitsLayer, (0,0))

        pygame.display.flip()