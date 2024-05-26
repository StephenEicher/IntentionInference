import pygame
import Board as b
import SpriteClasses as sc



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
        self.jump = 2
        self.actionPoints = 2
        
        # Initialize current stats
        self.currentHP = self.HP
        self.currentMovement = self.movement
        self.currentJump = self.jump
        self.currentActionPoints = self.actionPoints
        self.unitAbilities = self.abilities()
        if image is not None:
            self.sprite = sc.UnitSprite(self, image)
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
    def dispose(self):
        posessingAgent = self.game.allAgents[self.agentIndex]
        team = posessingAgent.team
        for unit in team:
            if unit.ID == self.ID:
                team.remove(unit)
                self.board.bPygame.spriteGroup.remove(unit.sprite)
                self.board.unitsMap[unit.position[0]][unit.position[1]] = None
                print(f"{unit.ID} is disposed")

class meleeUnit(Unit):
    def __init__(self, agentIndex, unitID, position, board, game):
        if agentIndex == 0:
            image = game.gPygame.spritesImageDict['Moo_melee']
        else:
            image = game.gPygame.spritesImageDict['Haku']
        super().__init__(agentIndex, unitID, position, board, game, image)
        self.unitSymbol = "M"
        self.movement = 2
        self.currentMovement = 2
        self.HP = 2
        self.currentHP = self.HP
        
class rangedUnit(Unit):
    def __init__(self, agentIndex, unitID, position, board, game):
        if agentIndex == 0:
            image = game.gPygame.spritesImageDict['Moo_ranged']
        else:
            image = game.gPygame.spritesImageDict['Haku']
        super().__init__(agentIndex, unitID, position, board, game, image)
        self.unitSymbol = "R"
        self.movement = 9999
        self.currentMovement = self.movement
        self.HP = 100
        self.currentHP = self.HP

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

    