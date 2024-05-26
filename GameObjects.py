import SpriteClasses as sc

class GameObject:
    """
    In-game object class that represents a generic "game object" from which child classes
    for elements, obstacles, units manage corresponding symbols, behavior/interactions. 
    """
    occupied = False
    symbol = None

    def __init__(self, name, position, z, image=None):
        self.name = name
        self.position = position
        self.z = z
        self.occupied = self.symbol != '.'
        if image is not None:
            self.sprite = sc.UnitSprite(self, image)
        else:
            self.sprite = None

    def invoke(self, unitInvoking, game):
        pass
    def deactivate(self):
        if self.sprite is not None:
            self.sprite.kill()
# class Elements(GameObject):
#     elemRandMultiplierBounds = (1, 4)

class InvokeAbilty(GameObject):
    def __init__(self, name, position, z, image=None):
        super().__init__(name, position, z, image)
        self.target = self.getOpponentUnits
        self.events = {}
        self.abilityName = None
        self.range = None

    def getAlliedUnits(self, unit, game):
        agentInvoking = game.allAgents[unit.agentIndex]
        return agentInvoking.team
    def getOpponentUnits(self, unit, game):
        for idx, agent in enumerate(game.allAgents):
            if idx is not unit.agentIndex:
                opponentAgent = agent
        return opponentAgent.team
    def invoke(self, unitInvoking, game):
        ability = {
        "name": self.abilityName,
        "cost": 0,
        "range": self.range,
        "events": self.events,
        }    
        if self.target is not None:
            for unit in self.target(unitInvoking, game):
                ability["targetedUnit"] = unit
                game.board.cast(unit, ability)     
        else:
            game.board.cast(unit, ability)
        
        return game.board.gameObjectDict.removeGO(self)




class Rapture(InvokeAbilty):
    def __init__(self, name, position, z, image=None):
        super().__init__(name, position, z, image)
        self.events = [{"type": "changeHP", "target": "targetunit", "value": -100}]
        self.target = self.getOpponentUnits
        self.name = "Rapture"

class Blessings(InvokeAbilty):
    def __init__(self, name, position, z, image=None):
        super().__init__(name, position, z, image)
        self.events = [{"type": "changeHP", "target": "targetunit", "value": 50}]
        self.target = self.getAlliedUnits
        self.name = "Rapture"    

class Terrain(GameObject):
    pass
    
# class Obstacles(Terrain):
#     pass

# class Water(Elements):
#     debugName = 'Water'
#     symbol = 'W'
    
#     def __init__(self, position):
#         super().__init__(position)

# class Earth(Elements):
#     debugName = 'Earth'
#     symbol = 'E'
    
#     def __init__(self, position):
#         super().__init__(position)

# class Fire(Elements):
#     debugName = 'Fire'
#     symbol = 'F'
   
#     def __init__(self, position):
#         super().__init__(position)

# class Air(Elements):
#     debugName = 'Air'
#     symbol = 'A'
    
#     def __init__(self, position):
#         super().__init__(position)

# class Seed(Obstacles):
#     debugName = 'Seed'
#     symbol = '[ ]'
#     pGrow = 0.2
    
#     def __init__(self, position, boardClassInstance):
#         super().__init__(position)
#         self.position = position
#         self.boardClassInstance = boardClassInstance

#     def proliferate(self):
#         seedPosition = self.position
#         directions = [
#             (-1, 0),  # Top
#             (1, 0),   # Bottom
#             (0, -1),  # Left
#             (0, 1),   # Right
#         ]

#         for dRow, dCol in directions:
#             newRow = seedPosition[0] + dRow
#             newCol = seedPosition[1] + dCol
            
#             if 0 <= newRow < self.boardClassInstance.rows and 0 <= newCol < self.boardClassInstance.cols:
#                 newSeedPosition = (newRow, newCol)
#                 adjacentObject = self.boardClassInstance.grid[newRow][newCol]
                
#                 if (adjacentObject is None or not adjacentObject.occupied) and boolWithProb(self.pGrow):
#                     newSeed = Seed(newSeedPosition, self.boardClassInstance)
#                     newSeed.symbol = '~'
#                     self.boardClassInstance.grid[newRow][newCol] = newSeed
#                     newSeed.proliferate()

class Surface(Terrain):
    debugName = 'Surface'
    pass