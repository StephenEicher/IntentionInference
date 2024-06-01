class EventDispatcher:
    def __init__(self, board):
        self.board = board
        self.genericListeners = {}
        self.indexedListeners = {}
        self.orderSensitiveEvents = []

    def addListener(self, event, listener, index = None, allListenersAdded = False):
        if index:
            if event not in self.orderSensitiveEvents:
                self.orderSensitiveEvents.append(event)
                self.indexedListeners[event] = []
            self.indexedListeners.get(event).append((listener, index))

            if allListenersAdded:
                self.indexedListeners.get(event).sort(key=lambda x: x[1]) # During initialization after all listeners have been added, reorganize the listeners according to their indices
                return True
            
            return True
            
        if event not in self.genericListeners:
            self.genericListeners[event] = []
        
        list = self.genericListeners.get(event)
        list.append(listener)

    def dispatch(self, event):
        eventType = type(event)
        responseList = []

        if eventType in self.genericListeners:
            for listener in self.genericListeners[eventType]:
                listenerName = listener.__name__
                response = listener(event)
                # self.board.manageScreen(None, None, response)
                listenerTuple = (listenerName, response)
                responseList.append(listenerTuple)

        else:
            for listener, _ in self.indexedListeners[eventType]:
                listenerName = listener.__name__
                response = listener(event)
                # self.board.manageScreen(None, None, response)
                listenerTuple = (listenerName, response)
                responseList.append(listenerTuple)

        return responseList

class eMove:
    def __init__(self, unit, minPoint, maxPoint):
        self.unit = unit
        self.minPoint = minPoint
        self.maxPoint = maxPoint

class eDisplace:
    def __init__(self, unit, castTarget, displaceDistance):
        self.unit = unit
        self.castTarget = castTarget
        self.displaceDistance = displaceDistance

class meCollision:
    def __init__(self, minPoint, maxPoint):
        self.minPoint = minPoint
        self.maxPoint = maxPoint

class eMeleeTargets:
    def __init__(self, unit):
        self.unit = unit

class eTargetsInRange:
    def __init__(self, unit, abilityRange):
        self.unit = unit
        self.checkUnit = None
        self.range = abilityRange
        self.minPoint = None
        self.maxPoint = None
        self.OnlyCardinalDirs = True
