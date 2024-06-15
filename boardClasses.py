import numpy as np
import noiseClasses as nc





class Board:
    def __init__(self, maxY, maxX, game):
        self.maxY = maxY
        self.maxX = maxX
        self.game = game
        self.units_map = np.zeros([maxX, maxY])
        row_indices, col_indices = np.meshgrid(np.arange(self.maxX), np.arange(self.maxY), indexing='ij')
        self.coord_map = np.stack((row_indices, col_indices), axis=-1)
        self.obs_map = self.initializeOMap()

    def clone(self, game):
        cloned_board = Board.__new__(Board)
        cloned_board.maxX = self.maxY
        cloned_board.maxY = self.maxX
        cloned_board.game = game
        cloned_board.units_map = np.array(self.units_map)
        cloned_board.obs_map = np.array(self.obs_map)
        cloned_board.coord_map = np.array(self.coord_map)
        return cloned_board



    def __eq__(self, other):
        if isinstance(other, Board):
            if not np.array_equal(self.units_map, other.units_map):
                return False
            if not np.array_equal(self.obs_map, other.obs_map):
                return False
            return True

    def initializeOMap(self):
        generatedObsMap = nc.OMap(self.maxY, self.maxX, self)
        return generatedObsMap.map
        # self.drawMap(self.instOM.map)


        
    def getValidMoveTargets(self, center):
        x, y = center

        # Check if there are any units in adjacent tiles
        xBounds = (np.max([0, x-1]), np.min([x + 2, self.maxX]))
        yBounds = (np.max([0, y-1]), np.min([y + 2, self.maxY]))
        coord_map_adj = self.coord_map[xBounds[0]:xBounds[1], yBounds[0]:yBounds[1]]
        unit_map_adj = self.units_map[xBounds[0]:xBounds[1], yBounds[0]:yBounds[1]]
        obs_map_adj = self.obs_map[xBounds[0]:xBounds[1], yBounds[0]:yBounds[1]]
        dirs = coord_map_adj[unit_map_adj + obs_map_adj == 0]
        return dirs
    

    
    def getUnitsInRadius(self, center, radius, excludeUnit=None):
        x, y = center

        # Check if there are any units in adjacent tiles
        xBounds = (np.max([0, x-radius]), np.min([x + radius+1, self.maxX]))
        yBounds = (np.max([0, y-radius]), np.min([y + radius+1, self.maxY]))
        unit_map_adj = self.units_map[xBounds[0]:xBounds[1], yBounds[0]:yBounds[1]]
        units = unit_map_adj[unit_map_adj != 0]
        if excludeUnit is not None:
            units = units[units != excludeUnit]
        return units
    
    def getValidAbilities(self, unit):
        validAbilities = []
        candidateAbilityClasses = unit.unitAbilities
        for abilityClass in candidateAbilityClasses:
            ability = abilityClass(unit)
            # candidateIDs = self.getUnitsInRadius(unit.position, ability.range)
            candidateIDs = self.getUnitsInRadius(unit.position, ability.range, unit.ID)
            for ID in candidateIDs:
                candidate = self.game.allUnits[ID]
                if ability.targeted:
                    ability.setTarget(candidate)
                    if ability.isValidToCast(self):
                        validAbilities.append((abilityClass, candidate.ID))
                else:
                    if ability.isValidToCast(self): 
                        validAbilities.append(abilityClass, None)
        
        return validAbilities

    
    def updateBoard(self, actionTuple):
        unitID, actionType, info = actionTuple
        if actionType == "move":
            self.processMove(actionTuple)
        if actionType == "ability":
            self.processAbility(actionTuple)

    def processMove(self, actionTuple):
        unitID, _, info = actionTuple
        unit = self.game.allUnits[unitID]
        initialPosition = unit.position
        finalPosition = info
        self.units_map[initialPosition[0], initialPosition[1]] = 0 # (Y, X) format
        self.units_map[finalPosition[0], finalPosition[1]] = unitID
        unit.position = finalPosition

        if self.game.pygameUI:
            unit.sprite.rect.topleft = unit.sprite.convertToRect(finalPosition)
        unit.currentMovement -= 1

        if unit.currentMovement == 0:
            unit.canMove = False

    def processAbility(self, actionTuple):
        unitID, actionType, info = actionTuple
        abilityClass, targetID = info
        unit = self.game.allUnits[unitID]
        if abilityClass == -1:
            #-1 is code for end turn
            unit.Avail = False
        else:
            ability = abilityClass(unit)
            if targetID is not None:
                target = self.game.allUnits[targetID]
                ability.setTarget(target)
            ability.activate()
        

        

