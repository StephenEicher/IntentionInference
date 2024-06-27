class GameObjectDict:
    def __init__(self, board):
        self.GOmap = {}
    
    def addListeners(self, dispatcher):
        dispatcher.addListener(e.eMove, self.GODhandleEvent)
        return True

    def insert(self, gameObject):
        if self.GOmap.get(gameObject.position, None) is None:
            self.GOmap[gameObject.position] = [gameObject]
        else:
            self.GOmap[gameObject.position].append(gameObject)

    def query(self, positions):
        if not isinstance(positions, list):
            positions = [positions]
        allObjs = []
        for position in positions:
            if self.GOmap.get(position, None) is not None:
                for entry in self.GOmap.get(position, None):
                    if entry is not None:
                        allObjs.append(entry)
        return allObjs
    def GODhandleEvent(self, event):
        if isinstance(event, e.eMove):

            
            pass
            
    def getAllGOs(self):
        allGOs = []
        for key in self.GOmap.keys():
            for go in self.GOmap[key]:
                if go is not None:
                    allGOs.append(go)
        return allGOs
    def removeGO(self, GO):
        key = GO.position
        if self.GOmap.get(key, None) is not None:
            self.GOmap[key].remove(GO)
            GO.deactivate()
