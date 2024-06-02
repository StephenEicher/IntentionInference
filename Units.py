import pygame
import Board as b
import SpriteClasses as sc
import copy
from immutables import Map

class Unit:
    def __init__(self, agentIndex, unitID, position, board, game, image=None):
        self.agentIndex = agentIndex
        self.ID = unitID
        self.unitSymbol = "U"
        self.position = position
        self.board = board
        self.game = game

        self.Alive = True
        self.Avail = True  # Available to select from team of units to move/act with
        self.canMove = True
        self.canAct = True

        # Initialize the default stats for the unit
        self.HP = 100
        self.movement = 4
        self.momentum = 0
        self.massConstant = 1
        self.jump = 0
        self.actionPoints = 2
        
        # Initialize current stats
        self.currentHP = self.HP
        self.currentMovement = self.movement
        self.currentMomentum = 0
        self.currentJump = self.jump
        self.currentActionPoints = self.actionPoints
        self.unitAbilities = self.abilities()
        if image is not None:
            self.sprite = sc.UnitSprite(self, image)
        else:
            self.sprite = None
    def __deepcopy__(self, memo):
        # Create a new instance of Unit without calling __init__
        cloned_unit = self.__class__.__new__(self.__class__)
        # Add the new instance to the memo dictionary
        memo[id(self)] = cloned_unit

        # Deepcopy each attribute
        cloned_unit.agentIndex = copy.deepcopy(self.agentIndex, memo)
        cloned_unit.ID = copy.deepcopy(self.ID, memo)
        cloned_unit.unitSymbol = copy.deepcopy(self.unitSymbol, memo)
        cloned_unit.position = copy.deepcopy(self.position, memo)
        
        cloned_unit.Alive = copy.deepcopy(self.Alive, memo)
        cloned_unit.Avail = copy.deepcopy(self.Avail, memo)
        cloned_unit.canMove = copy.deepcopy(self.canMove, memo)
        cloned_unit.canAct = copy.deepcopy(self.canAct, memo)

        cloned_unit.HP = copy.deepcopy(self.HP, memo)
        cloned_unit.movement = copy.deepcopy(self.movement, memo)
        cloned_unit.momentum = copy.deepcopy(self.momentum, memo)
        cloned_unit.massConstant = copy.deepcopy(self.massConstant, memo)
        cloned_unit.jump = copy.deepcopy(self.jump, memo)
        cloned_unit.actionPoints = copy.deepcopy(self.actionPoints, memo)

        cloned_unit.currentHP = copy.deepcopy(self.currentHP, memo)
        cloned_unit.currentMovement = copy.deepcopy(self.currentMovement, memo)
        cloned_unit.currentMomentum = copy.deepcopy(self.currentMomentum, memo)
        cloned_unit.currentJump = copy.deepcopy(self.currentJump, memo)
        cloned_unit.currentActionPoints = copy.deepcopy(self.currentActionPoints, memo)
        cloned_unit.unitAbilities = copy.deepcopy(self.unitAbilities, memo)

        # Do not copy the sprite
        cloned_unit.sprite = None

        return cloned_unit


    def abilities(self):
        abilities = [
            Map({
                "name": "Unarmed Strike",
                "cost": 1,
                "range": 1,
                "events": (
                    Map({"type": "changeHP", "target": "targetunit", "value": -1}),
                    Map({"type": "changeActionPoints", "target": "self", "value": -1}),
                ),
                "targetedUnit" : None,
            }),
            # Map({
            #     "name": "Shove",
            #     "cost": 1,
            #     "range": 1,
            #     "events": (
            #         Map({"type": "displace", "target": "targetunit", "distance": 1}),
            #         Map({"type": "changeActionPoints", "target": "self", "value": -1}),
            #     ),
            #     "targetedUnit" : None,
            # }),
        ]
        return abilities
    # def unitValidForTurn(self):
    #     if self.currentHP > 0 and (self.canMove or self.canAct):
    #         return True
    #     else:
    #         print("toggling to False!")
    #         self.Avail = False
    #         return False
    def resetForEndTurn(self):
        if self.Alive:
            self.Avail = True
            self.canMove = True
            self.canAct = True
            self.currentMovement = self.movement
            self.currentActionPoints = self.actionPoints
    # def dispose(self):
    #     posessingAgent = self.game.allAgents[self.agentIndex]
    #     # for unit in self.game.allAgents
    #     team = posessingAgent.team
    #     for unit in self.game.allUnits:
    #         if unit.ID == self.ID:
    #             self.game.allUnits.remove(unit)

    #     for unit in team:
    #         if unit.ID == self.ID:
    #             team.remove(unit)
    #             if self.sprite is not None:
    #                 self.board.bPygame.spriteGroup.remove(unit.sprite)
    #             self.board.instUM.map[unit.position[0]][unit.position[1]] = None
    #             print(f"{unit.ID} is disposed")

class meleeUnit(Unit):
    def __init__(self, agentIndex, unitID, position, board, game):
        if agentIndex == 0:
            # image = game.gPygame.spritesImageDict['Moo_melee']
            image = sc.Sprites().spritesDictScaled['Moo_melee']
        else:
            # image = game.gPygame.spritesImageDict['Haku']
            image = sc.Sprites().spritesDictScaled['Haku']
        super().__init__(agentIndex, unitID, position, board, game, image)
        self.unitSymbol = "M"
        self.movement = 3
        self.currentMovement = self.movement
        self.HP = 2
        self.currentHP = self.HP
        
class rangedUnit(Unit):
    def __init__(self, agentIndex, unitID, position, board, game):
        if agentIndex == 0:
            # image = game.gPygame.spritesImageDict['Moo_ranged']
            image = sc.Sprites().spritesDictScaled['Moo_ranged']
        else:
            # image = game.gPygame.spritesImageDict['Haku']
            image = sc.Sprites().spritesDictScaled['Haku']
        super().__init__(agentIndex, unitID, position, board, game, image)
        self.unitSymbol = "R"
        self.movement = 2
        self.currentMovement = self.movement
        self.HP = 2 
        self.currentHP = self.HP

        rangedStrike = Map({
                "name": "Ranged Strike",
                "cost": 1,
                "range": 3,
                "events": (
                    Map({"type": "changeHP", "target": "targetunit", "value": -1}),
                    Map({"type": "changeActionPoints", "target": "self", "value": -1}),
                ),
                "targetedUnit" : None,
            })
        self.unitAbilities.append(rangedStrike)



