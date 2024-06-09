import game as g
import AgentClasses as ac
import Units as u
import threading
import time

class testManager:
    def __init__(self):       
        self.failedTests = []
        self.passedTests = []
        self.myTests = []
    def runTests(self):
        for test in self.myTests:
            print(f'Running Test: {test.name}')
            try:
                if test.execute():
                    print('... passed!')
                else:
                    print('... failed!')
            except:
                print('... failed!')
    def addTest(self, test):
        self.myTests.append(test)


class test:
    def __init__(self, seed=10):
        self.name = "Test Name Not Assigned"
        self.p1Class = ac.HumanAgent
        self.p2Class = ac.HumanAgent
        self.teamComp = [[ [(0, 0), u.meleeUnit],
                [(0, 1), u.rangedUnit],], 
                [[(6,6), u.meleeUnit],
                [(6, 7), u.rangedUnit]]]
        self.pyGame = True
        self.seed = seed
        self.testThread = threading.Thread(target=self.startGameLoop)
        self.testThread.daemon = True
        self.game = None
    def constructGame(self):
        self.game = g.GameManager(self.p1Class, self.p2Class, self.teamComp, self.pyGame, self.seed, False)

    def startGameLoop(self):
        self.game.start()

    def startGameLoopThread(self):
        if self.game is None:
            self.constructGame()
        self.testThread.start()

    def execute(self):
        pass
    
    def storeUnitInfo(self, unit):
        info = {}
        info['HP'] = unit.HP
        info['actionPoints'] = unit.actionPoints
        info['currentMovement'] = unit.currentMovement
        info['movement'] = unit.movement
        info['currentHP'] = unit.currentHP
        info['currentActionPoints'] = unit.currentActionPoints
        info['position'] = unit.position
        return info
    
    def compareUnitInfo(self, u1Info, u2Info):
        dInfo = {}
        for key in u1Info.keys():
            if u1Info[key] is not u2Info[key]:
                if type(u1Info[key]) is float or type(u1Info[key]) is int:
                    delta = u1Info[key] - u2Info[key]
                    if delta > 0:
                        dInfo[key] = delta
                else:
                    dInfo[key] = (u1Info[key], u2Info[key])
        return dInfo
    
class startUp(test):
    def __init__(self):
        super().__init__()
        self.name = 'Start Up Test'
    def execute(self):
        try:
            self.startGameLoopThread()
            time.sleep(1)
            self.game.quit()
            return True
        except:
            return False
        
class execMove(test):
    def __init__(self):
        super().__init__()
        self.name = 'game.executeMove() Test'
    def execute(self):
        try:
            self.constructGame()
            unit = self.game.p1.team[0]
            preMove = self.storeUnitInfo(unit)
            flatActionSpace, waitingUnits, allActions, noMovesOrAbilities = self.game.getCurrentStateActions(self.game)
            for unitID, action in flatActionSpace:
                if action['type'] == 'move':
                    self.game.executeMove((unitID, action))
                    break
            postMove = self.storeUnitInfo(unit)
            delta = self.compareUnitInfo(preMove, postMove)
            assert len(delta.keys()) == 2
            assert delta['currentMovement'] == 1
            return True
        except:
            return False

tm = testManager()
tm.addTest(startUp())
tm.addTest(execMove())

tm.runTests()

