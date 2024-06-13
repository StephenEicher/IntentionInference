#Abilities
import numpy as np
class baseAbility:
    def __init__(self, source):
        self.source = source
        self.target = None
        self.range = None
        self.name = 'Ability Name'
        self.targeted = False
    def changeHealth(self, unit, delta):
        unit.currentHP = unit.currentHP + delta
    def changeAP(self, unit, delta):
        unit.currentActionPoints = unit.currentActionPoints + delta
    def activate(self):
        pass
    def isValidToCast(self, board):
        pass
    def alignedRowOrCol(self):
        x, y = self.source.position
        xt, yt = self.target.position
        return (x == xt or y == yt)
    def setTarget(self, target):
        self.target = target
    def obstacleInPath(self, board):
        x, y = self.source.position
        xt, yt = self.target.position
        return np.sum(board.obs_map[x:xt+1, y:yt+1]) > 0

class unarmedStrike(baseAbility):
    def __init__(self, source):
        super().__init__(source)
        self.range = 1
        self.name = 'Unarmed Strike'
        self.targeted = True
    def activate(self):
        dmg = -1
        ap = -1
        self.changeHealth(self.target, dmg)
        self.changeAP(self.source, ap)
    def isValidToCast(self, board):
        if self.alignedRowOrCol():
            if not self.obstacleInPath(board):
                return True
        return False
    

class rangedStrike(baseAbility):
    def __init__(self, source):
        super().__init__(source)
        self.range = 3
        self.name = 'Ranged Strike'
        self.targeted = True
    def activate(self):
        dmg = -1
        ap = -1
        self.changeHealth(self.target, dmg)
        self.changeAP(self.source, ap)
        return self.alignedRowOrCol()
    def isValidToCast(self, board):
        if self.alignedRowOrCol():
            if not self.obstacleInPath(board):
                return True
        return False
