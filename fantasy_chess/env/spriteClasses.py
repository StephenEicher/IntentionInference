import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


import pygame
from fantasy_chess.env import config as c

class Sprites:
    def __init__(self):
        spritePath = "./fantasy_chess/env/sprites/"
        spritesDict = {
            "Moo": pygame.image.load(spritePath + "sprite_moo.png"),
            "Haku": pygame.image.load(spritePath + "sprite_haku.png"),
            "Moo_ranged" : pygame.image.load(spritePath + "ranged_unit.png"),
            "Moo_melee" : pygame.image.load(spritePath + "melee_unit.png"),
            "Moo_melee_grey" : pygame.image.load(spritePath + "melee_unit_grey.png"),
            "Moo_ranged_grey" : pygame.image.load(spritePath + "ranged_unit_grey.png"),
            "Charlie" : pygame.image.load(spritePath + "sprite_charlie.png"),
            "obstacle" : pygame.image.load(spritePath + "sprite_obstacle.png")
        }
        
        self.spritesDictScaled = {}
        for name, surface in spritesDict.items():
            self.spritesDictScaled[name] = pygame.transform.scale(surface, (c.config.widthFactor, c.config.heightFactor))

class UnitSprite(pygame.sprite.Sprite):
    def __init__(self, parent, image):
        self.parent = parent
        pygame.sprite.Sprite.__init__(self)

        rectTopLeft = self.convertToRect(parent.position)

        # Initialize sprite image and position
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (rectTopLeft)

    def convertToRect(self, position):
        rectX = position[1] * c.config.widthFactor
        rectY = position[0] * c.config.heightFactor

        return (rectX, rectY)
    
