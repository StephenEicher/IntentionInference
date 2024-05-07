import pygame
import time
import Units as u
import config

class Pygame:

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((config.windowWidth, config.windowHeight))

        self.unitsLayer = pygame.Surface((config.windowWidth, config.windowHeight), pygame.SRCALPHA)
        self.unitsGroup = pygame.sprite.Group()

        self.sprites = u.Sprites(self)
        self.spritesImageDict = self.sprites.spritesDictScaled

    def pygameLoop(self):
        clock = pygame.time.Clock()

    def updateScreen(self):
        self.unitsLayer.fill((0,0,0,0))
        self.unitsGroup.draw(self.unitsLayer)
        self.screen.blit(self.unitsLayer, (0,0))

        pygame.display.flip()