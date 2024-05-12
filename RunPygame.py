import pygame
import time
import Units as u
import config

class Pygame:

    def __init__(self, game):
        pygame.init()
        self.game = game

        self.screen = pygame.display.set_mode((config.windowWidth, config.windowHeight))
        self.widget = pygame.display.set_mode((config.widgetWidth, config.widgetHeight))

        self.unitsLayer = pygame.Surface((config.windowWidth, config.windowHeight), pygame.SRCALPHA)
        self.unitsGroup = pygame.sprite.Group()

        self.sprites = u.Sprites(self)
        self.spritesImageDict = self.sprites.spritesDictScaled

    def pygameLoop(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePos = pygame.mouse.get_pos()
                    if self.getInput:
                        self.handleMouseInput(mousePos)
                        self.game.moveQueue.put(event)

    def drawButtons(self, validDirections, validAbilities):
        # Draw buttons for valid directions
        directionButtons = []
        for directionTuple, v in validDirections.items():
            buttonRect = pygame.Rect(10, 50 * len(directionButtons), 100, 40)  # Adjust dimensions as needed
            pygame.draw.rect(self.widget, (0, 255, 0), buttonRect)  # Green button
            directionName = directionTuple[0]
            directionButtons.append((buttonRect, directionName))
            # Render text on button (direction)
            font = pygame.font.Font(None, 24)
            text = font.render(directionName, True, (0, 0, 0))
            textRect = text.get_rect(center=buttonRect.center)
            self.widget.blit(text, textRect)

         # Draw buttons for valid abilities
        abilityButtons = []
        for i, ability in enumerate(validAbilities):
            buttonRect = pygame.Rect(10, 300 + (50 * i), 200, 40)  # Adjust dimensions as needed
            pygame.draw.rect(self.widget, (255, 0, 0), buttonRect)  # Red button
            abilityButtons.append((buttonRect, ability["name"]))
            # Render text on button (ability name)
            font = pygame.font.Font(None, 24)
            text = font.render(ability["name"], True, (0, 0, 0))
            textRect = text.get_rect(center=buttonRect.center)
            self.widget.blit(text, textRect)

    def handleMouseInput(mousePos):
        for button_rect, direction in direction_buttons:
            if button_rect.collidepoint(mouse_pos):
                return {"type": "move", "direction": direction}
        for button_rect, ability_name in ability_buttons:
            if button_rect.collidepoint(mouse_pos):
                return {"type": "castAbility", "ability_name": ability_name}
        return None

    def updateScreen(self):
        self.unitsLayer.fill((0,0,0,0))
        self.unitsGroup.draw(self.unitsLayer)
        self.screen.blit(self.unitsLayer, (0,0))

        pygame.display.flip()