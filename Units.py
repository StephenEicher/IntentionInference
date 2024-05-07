import pygame
from config import config

class Sprites:
    def __init__(self):
        spritesDict = {
            "Moo": pygame.image.load(r"C:\Users\Brian\Documents\IntentionInference\sprites\sprite_moo.PNG")

        }

        self.spritesDictScaled = {}
        for name, surface in spritesDict.items():
            self.spritesDictScaled[name] = pygame.transform.scale(surface, (config.widthFactor, config.heightFactor))

class Unit:
    def __init__(self, agentIndex, unitID, position):
        self.agentIndex = agentIndex
        self.unitID = unitID
        self.unitSymbol = "U"
        self.position = position

        self.Alive = True
        self.Avail = True  # Available to select from team of units to move/act with
        self.canMove = True
        self.canAct = True

        # Initialize the default stats for the unit
        self.HP = 100
        self.movement = 4
        self.jump = 2
        self.actionPoints = 2
        
        # Initialize current stats as instance variables
        self.currentHP = self.HP
        self.currentMovement = self.movement
        self.currentJump = self.jump
        self.currentActionPoints = self.actionPoints
        
    def abilities(self):
        abilities = [
            {
                "name": "Unarmed Strike",
                "cost": 1,
                "range": 1,
                "events": [
                    {"type": "changeHP", "target": "targetunit", "value": -1},
                    {"type": "changeActionPoints", "target": "self", "value": -1},
                ]
            },
            {
                "name": "Shove",
                "cost": 1,
                "range": 1,
                "events": [
                    {"type": "move", "target": "targetunit", "distance": 1},
                    {"type": "changeActionPoints", "target": "self", "value": -1},
                ]
            },
            {
                "name": "Hide",
                "cost": 1,
                "range": 0,
                "events": [
                    {"type": "hide", "target": "self"}
                ]
            }
        ]
        return abilities

    def unitValidForTurn(self):
        if self.currentHP > 0 or self.currentMovement > 0 or self.currentActionPoints > 0:
            return True

class UnitSprite(Unit, pygame.sprite.Sprite):
    def __init__(self, agentIndex, unitID, position, image):
        super().__init__(agentIndex, unitID, position)
        pygame.sprite.Sprite.__init__(self)

        rectTopLeft = self.convertToRect(position)

        # Initialize sprite image and position
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (rectTopLeft)

    def convertToRect(self, position):
        rectX = position[1] * config.widthFactor
        rectY = position[0] * config.heightFactor

        return (rectX, rectY)