import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fantasy_chess.env import boardClasses as b
from fantasy_chess.env import spriteClasses as sc
import copy
from immutables import Map
from fantasy_chess.env import abilityClasses as a
import numpy as np
class Unit:
    def __init__(self, agentIndex, unitID, position, image=None):
        self.agentIndex = agentIndex
        self.ID = unitID
        self.unitSymbol = "U"
        self.position = np.array(position)
        self.Alive = True
        self.Avail = True  # Available to select from team of units to move/act with
        self.canMove = True
        self.canAct = True

        # Initialize the default stats for the unit
        self.HP = 2
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
    def clone(self):
        # 
        cloned_unit = self.__class__.__new__(self.__class__)

        # Deepcopy each attribute
        cloned_unit.agentIndex = self.agentIndex
        cloned_unit.ID = self.ID
        cloned_unit.position = self.position
        
        cloned_unit.Alive = self.Alive
        cloned_unit.Avail = self.Avail
        cloned_unit.canMove = self.canMove
        cloned_unit.canAct = self.canAct

        cloned_unit.HP = self.HP
        cloned_unit.movement = self.movement
        cloned_unit.actionPoints = self.actionPoints

        cloned_unit.currentHP = self.currentHP
        cloned_unit.currentMovement = self.currentMovement
        cloned_unit.currentActionPoints = self.currentActionPoints
        cloned_unit.unitAbilities = self.unitAbilities
        cloned_unit.sprite = None
        return cloned_unit

    def abilities(self):
        abilities = [a.unarmedStrike]
        return abilities
    def resetForEndTurn(self):
        if self.Alive:
            self.Avail = True
            self.canMove = True
            self.canAct = True
            self.currentMovement = self.movement
            self.currentActionPoints = self.actionPoints
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if (
                isinstance(other, self.__class__) and
                self.ID == other.ID and
                self.currentHP == other.currentHP and
                self.currentActionPoints == other.currentActionPoints and
                np.array_equal(self.position, other.position) and
                self.Avail == other.Avail and
                self.currentMovement == other.currentMovement and
                self.agentIndex == other.agentIndex
            ):
                return True

        return False

class meleeUnit(Unit):
    def __init__(self, agentIndex, unitID, position):
        if agentIndex == 0:
            image = sc.Sprites().spritesDictScaled['Moo_melee']
        else:
            image = sc.Sprites().spritesDictScaled['Moo_melee_grey']
        super().__init__(agentIndex, unitID, position, image)
        self.unitSymbol = "M"
        self.movement = 3
        self.currentMovement = self.movement
        self.HP = 2
        self.currentHP = self.HP
        
class rangedUnit(Unit):
    def __init__(self, agentIndex, unitID, position):
        if agentIndex == 0:
            image = sc.Sprites().spritesDictScaled['Moo_ranged']
        else:
            image = sc.Sprites().spritesDictScaled['Moo_ranged_grey']
        super().__init__(agentIndex, unitID, position, image)
        self.unitSymbol = "R"
        self.movement = 2
        self.currentMovement = self.movement
        self.HP = 2 
        self.currentHP = self.HP
        self.unitAbilities.append(a.rangedStrike)



