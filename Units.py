class Unit:
    def __init__(self, agentIndex, unitID, position):
        self.agentIndex = agentIndex
        self.unitID = unitID
        self.unitSymbol = "U"
        self.position = position

        self.Alive = True
        self.Avail = True  # Available to select from team of units to move/act with

        # Initialize the default stats for the unit
        self.HP = 100
        self.movement = 5
        self.jump = 2
        self.actionPoints = 2
        
        # Initialize current stats as instance variables
        self.currentHP = self.HP
        self.currentMovement = self.movement
        self.currentJump = self.jump
        self.currentActionPoints = self.actionPoints
        
    def abilities(self):
        uniqueAbilities = [
            {
                "name": "Unarmed Strike",
                "cost": 1,
                "range": 1,
                "events": [
                    {"type": "changeHP", "target": "targetunit", "value": -1},
                    {"type": "changeActionPoints", "target": "targetunit", "value": -1},
                ]
            },
            {
                "name": "Shove",
                "cost": 1,
                "range": 1,
                "events": [
                    {"type": "move", "target": "targetunit", "distance": 1},
                    {"type": "changeActionPoints", "target": "targetunit", "value": -1},
                ]
            },
            {
                "name": "Hide",
                "cost": 1,
                "range": 1,
                "events": [
                    {"type": "hide", "target": "self"}
                ]
            }
        ]
        return uniqueAbilities

    def unitValidForTurn(self):
        return self.currentHP > 0 or self.currentMovement > 0 or self.currentActionPoints > 0
