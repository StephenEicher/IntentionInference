import pygame
from config import config
class Sprites:
    def __init__(self):
        spritesDict = {
            "Moo": pygame.image.load(r".\sprites\sprite_moo.PNG"),
            "Haku": pygame.image.load(r".\sprites\sprite_haku.PNG"),
            "Moo_ranged" : pygame.image.load(r".\sprites\ranged_unit.PNG"),
            "Moo_melee" : pygame.image.load(r".\sprites\melee_unit.PNG"),
            "Charlie" : pygame.image.load(r".\sprites\sprite_charlie.PNG"),
            "obstacle" : pygame.image.load(r".\sprites\sprite_obstacle.PNG")
        }
        
        self.spritesDictScaled = {}
        for name, surface in spritesDict.items():
            self.spritesDictScaled[name] = pygame.transform.scale(surface, (config.widthFactor, config.heightFactor))

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
        rectX = position[1] * config.widthFactor
        rectY = position[0] * config.heightFactor

        return (rectX, rectY)
    
