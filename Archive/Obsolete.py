    def getValidAbilities(self, unit):
        self.getValidAbilitiesTemp(unit)
        unitAbilities = unit.unitAbilities()
        
        # Access dictionary of class actions and their action points cost
        # Return all, but denote which are actually allowed by current action points
        # Highest level keys are 'name,''cost,' and 'events' which consists of type of events (dictionaries) involved in constructing the ability

        affordableAbilities = []
        validAbilities = []

        flatAbilities = []

        if unit.canAct is False:
            invalidAbilities=unitAbilities
            return (validAbilities, invalidAbilities, flatAbilities)

        for ability in unitAbilities:
            if ability.get("cost") <= unit.currentActionPoints:
                affordableAbilities.append(ability)
            if ability.get("cost") > unit.currentActionPoints:
                invalidAbilities[ability["name"]] = ability.get("cost")

        for ability in affordableAbilities:
            for event in ability.get("events"):
                
                if "target" in event:
                    if event.get("target") == "targetunit":
                        range = ability.get("range")
                        event = e.eTargetsInRange(unit, range)
                        responseList = self.dispatcher.dispatch(event)
                        viableTargets = responseList[0][1] # for first index: 0 for UMHandleEvent's response, 1 for ZMHandleEvent's response, 2 for GOTHandleEvent's response

                        if viableTargets:
                            validAbilities.append(ability)
                        if viableTargets is None:
                            invalidAbilities[ability["name"]] = ability.get("cost")

                        for target in viableTargets:
                            abilityWithTarget = dict(ability)
                            abilityWithTarget["targetedUnit"] = target.ID
                            abilityWithTarget["targetedUnitHP"] = target.HP
                            abilityWithTarget = Map(abilityWithTarget)
                            flatAbilities.append((unit.ID, Map({"type" : "castAbility", "abilityDict" : abilityWithTarget})))
                else:
                    flatAbilities.append((unit.ID, Map({"type" : "castAbility", "abilityDict" : Map(ability)})))

        for ability in affordableAbilities: # If affordable but no targeting required add to valid abilities
            if ability not in validAbilities and ability.get("range") == 0:
                validAbilities.append(ability)

        return (validAbilities, invalidAbilities, flatAbilities)

    def getValidDirections(self, unit):
        validAdjPositions = self.getAdjDirections(unit)
    
        GOY = len(self.instUM.map) - 1 - unit.position[0]
        UX = unit.position[1]

        # Initialize minPoint to the desired values
        minPointX = max(UX - 1, 0)  # Ensure minPointX is at least 0
        minPointY = max(GOY - 1, 0)  # Ensure minPointY is at least 0

        # Set minPoint based on computed values
        minPoint = (minPointX, minPointY)

        # Set maxPoint
        maxPointX = minPointX + 2
        maxPointY = minPointY + 2  # maxPoint is calculated based on a 3x3 region

        if maxPointX > (len(self.instUM.map) - 1):
            maxPointX = self.maxX
        
        if maxPointY > (len(self.instUM.map) - 1):
            maxPointY = self.maxY

        maxPoint = (maxPointX, maxPointY)

        event = e.eMove(unit, minPoint, maxPoint)
        
        listenerResponses = self.dispatcher.dispatch(event)
        # A list of tuples (listener name, its response)
        # Each response always occurs in the same order in the list:
            # Within UnitsMap response: dictionary
                # first key is unit's position as a tuple and its value is the unit object
                # remaining keys are tuples containing the direction string, position tuple and their values are the adjacent unit object if any
            # Within ZMap response: dictionary 
                # first key is unit's position as a tuple and its value is the z value the unit is standing on 
                # remaining keys are tuples containing the direction string, position tuple and their value are the z value of that adjacent spot
            # Within GameObjectTree response: list of dictionaries
                # each dictionary contains keys "direction," "position," "stack," "stackZ," and "surfaces"
                # first 2 self-explanatory
                # key "stack"'s value is the stack of GameObjects for a given position
                # key "stackZ"'s value is the int total height (z) of the stack
                # key "surfaces"'s value is the list of surface GameObjects for a given position
  
        # Unpack listenerResponses
        #gameObjectTreeR = listenerResponses[0][1]
        unitsMapR = listenerResponses[0][1]
        gameObjectTreeR = listenerResponses[1][1]
 
        zMapR = listenerResponses[3][1]

        

        takeFallDamage = False
        addSurfaces = []
        validDirections = {}
        flatValidDirections = []
        
        for direction, position in validAdjPositions.items():
    
            # Check if adjacent Unit exists
            if (direction, position) in unitsMapR:
                if unitsMapR[(direction, position)] is not None:
                    continue

            # Calculate elevation difference and check if it's too great, parse out gameObjectTreeR
            if gameObjectTreeR:
                for dict in gameObjectTreeR:
                    if position == dict.get("position"):
                        stackZ = dict.get("stackZ")
                        surfaces = dict.get("surfaces")
                        totalZ = zMapR[(direction, position)] + stackZ
                        if surfaces:
                            addSurfaces.append(surfaces)

                        unitZ = zMapR[unit.position]
                        break  # Break the loop once we have found and assigned totalZ and unitZ
                else:
                    # If we do not break the loop, it means no matching position was found
                    totalZ = zMapR[direction, position]
                    unitZ = zMapR[unit.position]
            else:
                totalZ = zMapR[direction, position]
                unitZ = zMapR[unit.position]

            if (totalZ - unitZ) > unit.jump:
                continue

            # If the position is valid, add it to the validDirections dictionary
            validDirections[(direction, position)] = (takeFallDamage, None)
            flatValidDirections.append((unit.ID, Map({"type" : "move", "directionDict" : Map({(direction, position) : (takeFallDamage, None)})})))
            
        return Map(validDirections), flatValidDirections


def getValidDirections(self, unit):
        validAdjPositions = self.getAdjDirections(unit)

        GOY = len(self.instUM.map) - 1 - unit.position[0]
        UX = unit.position[1]

        # Initialize minPoint to the desired values
        minPointX = max(UX - 1, 0)  # Ensure minPointX is at least 0
        minPointY = max(GOY - 1, 0)  # Ensure minPointY is at least 0

        # Set minPoint based on computed values
        minPoint = (minPointX, minPointY)

        # Set maxPoint
        maxPointX = minPointX + 2
        maxPointY = minPointY + 2  # maxPoint is calculated based on a 3x3 region

        if maxPointX > (len(self.instUM.map) - 1):
            maxPointX = self.maxX
        
        if maxPointY > (len(self.instUM.map) - 1):
            maxPointY = self.maxY

        maxPoint = (maxPointX, maxPointY)

        event = e.eMove(unit, minPoint, maxPoint)
        
        listenerResponses = self.dispatcher.dispatch(event)
        # A list of tuples (listener name, its response)
        # Each response always occurs in the same order in the list:
            # Within UnitsMap response: dictionary
                # first key is unit's position as a tuple and its value is the unit object
                # remaining keys are tuples containing the direction string, position tuple and their values are the adjacent unit object if any
            # Within ZMap response: dictionary 
                # first key is unit's position as a tuple and its value is the z value the unit is standing on 
                # remaining keys are tuples containing the direction string, position tuple and their value are the z value of that adjacent spot
            # Within GameObjectTree response: list of dictionaries
                # each dictionary contains keys "direction," "position," "stack," "stackZ," and "surfaces"
                # first 2 self-explanatory
                # key "stack"'s value is the stack of GameObjects for a given position
                # key "stackZ"'s value is the int total height (z) of the stack
                # key "surfaces"'s value is the list of surface GameObjects for a given position
  
        # Unpack listenerResponses
        #gameObjectTreeR = listenerResponses[0][1]
        unitsMapR = listenerResponses[0][1]
        gameObjectTreeR = listenerResponses[1][1]
 
        zMapR = listenerResponses[3][1]

        

        takeFallDamage = False
        addSurfaces = []
        validDirections = {}
        flatValidDirections = []
        
        for direction, position in validAdjPositions.items():
    
            # Check if adjacent Unit exists
            if (direction, position) in unitsMapR:
                if unitsMapR[(direction, position)] is not None:
                    continue

            # Calculate elevation difference and check if it's too great, parse out gameObjectTreeR
            if gameObjectTreeR:
                for dict in gameObjectTreeR:
                    if position == dict.get("position"):
                        stackZ = dict.get("stackZ")
                        surfaces = dict.get("surfaces")
                        totalZ = zMapR[(direction, position)] + stackZ
                        if surfaces:
                            addSurfaces.append(surfaces)

                        unitZ = zMapR[unit.position]
                        break  # Break the loop once we have found and assigned totalZ and unitZ
                else:
                    # If we do not break the loop, it means no matching position was found
                    totalZ = zMapR[direction, position]
                    unitZ = zMapR[unit.position]
            else:
                totalZ = zMapR[direction, position]
                unitZ = zMapR[unit.position]

            if (totalZ - unitZ) > unit.jump:
                continue

            # If the position is valid, add it to the validDirections dictionary
            validDirections[(direction, position)] = (takeFallDamage, None)
            flatValidDirections.append((unit.ID, Map({"type" : "move", "directionDict" : Map({(direction, position) : (takeFallDamage, None)})})))
            
        return Map(validDirections), flatValidDirections



    def determineUnitCollision(self, unit, collateralTargets, maxDisplaceDistance, delta):
        """
        for each collision, decrease the maxDisplaceDistance which prior to unit collision checking
        is the product of the ability displace distance * displacing unit's massConstant

        for now, idea is that maxDisplaceDistance is the amount of tiles that a displacing unit or group of units
        due to collision will be displaced at the end of the sequence

        """
        for i, tile in enumerate(self.spatialLinearizedList):
            if isinstance(tile, u.Unit):
                for unit in collateralTargets:
                    if tile == unit:
                        continue
                    else:
                        # This potential collateral unit is separated from the displacing unit by an impassable object
                        lastUnitIndex = i - 1
                        break

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



    #     def UMhandleEvent(self, event):
    #     if isinstance(event, e.eMove):
    #         adjUnits = {}
    #         adjUnits[(event.unit.position[0], event.unit.position[1])] = event.unit
    #         for direction, (adjY, adjX) in self.board.getAdjDirections(event.unit).items():
    #             # Check if the adjacent position is within bounds of the map
    #             if 0 <= adjY < len(self.map) and 0 <= adjX < len(self.map):
    #                 adjUnit = self.map[adjY][adjX]

    #                 if isinstance(adjUnit, u.Unit):
    #                     adjUnits[(direction, (adjY, adjX))] = adjUnit
                        
    #         return adjUnits


    #     elif isinstance(event, e.eTargetsInRange):
    #         targets = []
    #         rowBounds = np.array([event.unit.position[0] - event.range, event.unit.position[0] + event.range])
    #         colBounds = np.array([event.unit.position[1] - event.range, event.unit.position[1] + event.range])
    #         rowBounds = np.clip(rowBounds, 0, len(self.map)-1)
    #         colBounds = np.clip(colBounds, 0, len(self.map)-1)
    #         #xMax = self.unit.position[0] + self.range
    #         tilesToCheck = []
    #         for row in np.arange(rowBounds[0], rowBounds[1]+1): # checks rectangular area defined with sides defined by length of bounds
    #             for col in np.arange(colBounds[0], colBounds[1]+1):
    #                 tilesToCheck.append(self.map[row][col]) # already appends all objects found at coordinates and excludes empty tiles                


    #         for unit in tilesToCheck:
    #             if isinstance(unit, u.Unit):
    #                 if unit.ID is not event.unit.ID and unit.agentIndex is not event.unit.agentIndex:

    #                     if not event.OnlyCardinalDirs:
    #                         targets.append(unit)
    #                     else:
    #                         #If on the same row or on the same column
    #                         if unit.position[0] == event.unit.position[0] or unit.position[1] == event.unit.position[1]:
    #                             selfPos = np.array(unit.position)
    #                             unitPos = np.array(event.unit.position)
    #                             if abs(np.linalg.norm(selfPos-unitPos)) <= event.range:
    #                                 targets.append(unit)
    #                         # if abs(event.unit.position[0] - unit.position[0]) == abs(event.unit.position[1] - unit.position[1]):
    #                         #     if abs(unit.position[0] - event.unit.position[0]) <= event.range or abs(unit.position[1] - event.unit.position[1]) <= event.range:
    #                         #         targets.append(unit)
           
    #         validTargets = self.board.GOT.checkforObstructions(event, targets)
    #         return validTargets # refer to GOT's response for final list of viable targets

    #     elif isinstance(event, e.eDisplace):
    #         if abs(event.unit.position[0] - event.castTarget.position[0]) == abs(event.unit.position[1] - event.castTarget.position[1]):
    #             if event.unit.position[0] - event.castTarget.position[0] >= 0:
    #                 if event.unit.position[1] - event.castTarget.position[1] >= 0:
    #                     delta = np.array([-1, -1])
    #                 else:
    #                     delta = np.array([-1, 1])
    #             else:
    #                 if event.unit.position[1] - event.castTarget.position[1] >= 0:
    #                     delta = np.array([1, -1])
    #                 else:
    #                     delta = np.array([1, 1])
    #         if event.unit.position[0] == event.castTarget.position[0]:
    #             delta = np.array([0, 1])
    #         if event.unit.position[1] == event.castTarget.position[1]:
    #             delta = np.array([1, 0])

    #         collateralUnits = []
    #         self.spatialLinearizedList = [None for _ in event.displaceDistance]
    #         start = np.array(list(event.castTarget.position))
    #         for i in range(event.displaceDistance):
    #             start += delta
    #             if self.map[start[0]][start[1]]:
    #                 unit = self.map[start[0]][start[1]]
    #                 if unit.ID is not event.unit.ID:
    #                     collateralUnits.append(unit)
    #                     self.spatialLinearizedList[i] = unit

    #         unitsAndDisplacement = (collateralUnits, start, delta)

    #         self.board.GOT.incomingUM.put(unitsAndDisplacement)
            

    #         return None

    #     else:
    #         return None


        
    #     groupToDisplace = []
    #     for _ in range(lastUnitIndex):
    #         for unit in self.spatialLinearizedList:
    #             maxDisplaceDistance -= unit.massConstant

    # def assignListeners(self, dispatcher):
    #     dispatcher.addListener(e.eMove, self.UMhandleEvent)
    #     dispatcher.addListener(e.eTargetsInRange, self.UMhandleEvent, 1, True)
    #     dispatcher.addListener(e.eDisplace, self.UMhandleEvent, 1, True)



        def bresenhamLine(start, end):
        # Bresenham's line algorithm to return a list of points from start to end
        points = []
        x1, y1 = start
        x2, y2 = end
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = -1 if x1 > x2 else 1
        sy = -1 if y1 > y2 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                points.append((y, x))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                points.append((y, x))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        points.append((y2, x2))

        return points


    def cast(self, entity, ability):
        targetType = ability["events"][0].get("target")
        if targetType == "targetunit":
            #castTarget = self.game.currentAgent.selectTarget(ability)
            castTargetID = ability["targetedUnit"]
            castTarget = self.game.getUnitByID(castTargetID)
        for event in ability.get("events"):
            for k, v in event.items():
                if v == "changeHP":
                    castTarget.currentHP += event["value"]
                    castTarget.currentHP = np.min([castTarget.currentHP, castTarget.HP])


                if v == "displace":
                    displaceDistance = event.get("distance")
                    castTarget.currentMomentum = displaceDistance * castTarget.massConstant
                    event = eDisplace(entity, castTarget, displaceDistance)
                    self.dispatcher.dispatch(event)

                    castTarget.position = event["value"]


                if v == "changeActionPoints":
                    entity.currentActionPoints += event["value"]
                if v == "changeMaxActionPoints":
                    delta = event["value"]
                    entity.actionPoints += delta
                if v == "changeMovement":
                    delta = event["value"]
                    entity.actionPoints += delta





def getAdjDirections(self, unit):
        unitY, unitX = unit.position
        adjPositions = { 
            "NW": (unitY - 1, unitX - 1),
            "N": (unitY - 1, unitX),
            "NE": (unitY - 1, unitX + 1),
            "E": (unitY, unitX + 1),
            "SE": (unitY + 1, unitX + 1),
            "S": (unitY + 1, unitX),
            "SW": (unitY + 1, unitX - 1),
            "W": (unitY, unitX - 1)
        }

        return self.filterValidDirections(adjPositions)   


   def rayCast(self, origin, target, castingUnit, targetUnit, gameObjectTree, unitsMap, zMap):
        
        line = self.bresenhamLine(origin, target)

        # Define query box size which captures line (quadtree order of axes is X, Y not Y, X)
        queryBoxMin = ()
        queryBoxMax = ()
        queryBoxStartX, initStartY = line[0]
        queryBoxEndX, initEndY = line[-1]

        # Convert numpy Y value to quadtree Y value
        queryBoxStartY = unitsMap.shape[0] - 1 - initStartY
        queryBoxEndY = unitsMap.shape[0] - 1 - initEndY

        len = queryBoxEndX - queryBoxStartX
        wid = queryBoxEndY - queryBoxStartY

        if len < 0 and wid < 0:
            queryBoxMin = (line[-1])
            queryBoxMax = (line[0])

        if len < 0:
            queryBoxMin = (queryBoxEndX, queryBoxStartY)
            queryBoxMax = (queryBoxStartX, queryBoxEndY)

        if wid < 0:
            queryBoxMin = (queryBoxStartX, queryBoxEndY)
            queryBoxMax = (queryBoxEndX, queryBoxStartY)

        # Return ALL gameObjectStacks found in that box 
        allGameObjectStacks = gameObjectTree.querySpace(queryBoxMin, queryBoxMax)

        # Include gameObjectStacks which fall on a point in the line
        lineStacks = {}
        for stack in allGameObjectStacks:
            if stack[0].position in line:
                lineStacks[stack[0].position] = stack

        # Get overall height of GameObjects on each point
        newLineStacks = {}
        totalGameObjectsZ = 0
        for position, stack in lineStacks.items():
            for gameObject in stack:
                totalGameObjectsZ += gameObject.height
            newLineStacks[position] = totalGameObjectsZ

        for point in line:
            y, x =  point

            # Check if other Units in line
            if unitsMap[y, x] is not None:
                return False
            
            # Combine totalGameObjectsZ with zMap values
            z = zMap[y, x]
            effectiveZ = z + newLineStacks[y, x]
            if targetUnit.height > castingUnit.height:
                targetUnit.height - castingUnit.height < effectiveZ
                return False
            if targetUnit.height < castingUnit.height:    
                castingUnit.height - targetUnit.height < effectiveZ
                return False
        
        # If no units found, or view obstructed by terrain or obstacles with clearance of target in mind, return True for clear LOS
        return True



    def filterValidDirections(self, directions):
        """Filter and return only valid directions within the grid bounds."""
        validDirections = {}
        for direction, (y, x) in directions.items():
            # Check if the coordinates are within the grid bounds
            if 0 <= y < self.maxY and 0 <= x < self.maxX:
                validDirections[direction] = (y, x)
        return validDirections

