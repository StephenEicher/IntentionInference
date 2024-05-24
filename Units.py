import pygame
from config import config
import Board as b

class Sprites:
    def __init__(self):
        spritesDict = {
            "Moo": pygame.image.load(r".\sprites\sprite_moo.PNG"),
            "Haku": pygame.image.load(r".\sprites\sprite_haku.PNG"),
            "Moo_ranged" : pygame.image.load(r".\sprites\ranged_unit.PNG"),
            "Moo_melee" : pygame.image.load(r".\sprites\melee_unit.PNG"),
        }
        
        self.spritesDictScaled = {}
        for name, surface in spritesDict.items():
            self.spritesDictScaled[name] = pygame.transform.scale(surface, (config.widthFactor, config.heightFactor))

class Unit:
    def __init__(self, agentIndex, unitID, position, game, image=None):
        self.agentIndex = agentIndex
        self.ID = unitID
        self.unitSymbol = "U"
        self.position = position
        self.game = game

        self.Alive = True
        self.Avail = True  # Available to select from team of units to move/act with
        self.canMove = True
        self.canAct = True

        # Initialize the default stats for the unit
        self.HP = 100
        self.movement = 4
        self.jump = 2
        self.actionPoints = 2
        
        # Initialize current stats
        self.currentHP = self.HP
        self.currentMovement = self.movement
        self.currentJump = self.jump
        self.currentActionPoints = self.actionPoints
        self.unitAbilities = self.abilities()
        if image is not None:
            self.sprite = UnitSprite(self, image)
        else:
            self.sprite = None
        
    def abilities(self):
        abilities = [
            {
                "name": "Unarmed Strike",
                "cost": 1,
                "range": 1,
                "events": [
                    {"type": "changeHP", "target": "targetunit", "value": -1},
                    {"type": "changeActionPoints", "target": "self", "value": -1},
                ],
                "targetedUnit" : None,
            },
            {
                "name": "Shove",
                "cost": 1,
                "range": 1,
                "events": [
                    {"type": "move", "target": "targetunit", "distance": 1},
                    {"type": "changeActionPoints", "target": "self", "value": -1},
                ],
                "targetedUnit" : None,
            },
        ]
        return abilities
    def unitValidForTurn(self):
        if self.currentHP > 0 and (self.canMove or self.canAct):
            return True
        else:
            print("toggling to False!")
            self.Avail = False
            return False
    def resetForEndTurn(self):
        if self.Alive:
            self.Avail = True
            self.canMove = True
            self.canAct = True
            self.currentMovement = self.movement
            self.currentActionPoints = self.actionPoints

class meleeUnit(Unit):
    def __init__(self, agentIndex, unitID, position, game, image=None):
        super().__init__(agentIndex, unitID, position, game, image)
        self.unitSymbol = "M"
        self.movement = 2
        self.currentMovement = 2
        self.HP = 200
        self.currentHP = 200
        
class rangedUnit(Unit):
    def __init__(self, agentIndex, unitID, position, game, image=None):
        super().__init__(agentIndex, unitID, position, game, image)
        self.unitSymbol = "R"
        self.movement = 4
        self.currentMovement = 4
        self.HP = 100
        self.currentHP = 100

        rangedStrike = {
                "name": "Ranged Strike",
                "cost": 1,
                "range": 100,
                "events": [
                    {"type": "changeHP", "target": "targetunit", "value": -1},
                    {"type": "changeActionPoints", "target": "self", "value": -1},
                ],
                "targetedUnit" : None,
            }
        self.unitAbilities.append(rangedStrike)

        

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
    
