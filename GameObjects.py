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
# class Elements(GameObject):
#     elemRandMultiplierBounds = (1, 4)

class PowerUp(GameObject):
    def invoke(self, unitInvoking, game):
        agentInvoking = game.allAgents[unitInvoking.agentIndex]
        for idx, agent in enumerate(game.allAgents):
            if idx is not unitInvoking.agentIndex:
                opponentAgent = agent
        for unit in opponentAgent.team:
                    godsWrath = {
                "name": "Wrath of God",
                "cost": 0,
                "range": -1,
                "events": [
                    {"type": "changeHP", "target": "targetunit", "value": -100},
                    {"type": "changeActionPoints", "target": "self", "value": 0},
                ],
                "targetedUnit" : unit,
            }
        game.board.cast(godsWrath)


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