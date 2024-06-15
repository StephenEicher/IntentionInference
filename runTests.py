import gameClasses as g
import agentClasses as agC
import unitClasses as u
import time
import random
import abilityClasses as abC
class testManager:
    def __init__(self):       
        self.failedTests = []
        self.passedTests = []
        self.myTests = []
    def runTests(self):
        failedTests = []
        nTests = len(failedTests)
        nFailed = 0
        for testClass, nTrials in self.myTests:
            tests = [testClass() for _ in range(nTrials)]
            print(f'Running Test: {tests[0].name}')
            passed = True
            for test in tests:
                try:
                    if not test.execute():
                        passed = False
                        break
                except:
                    passed = False
                    
            if passed:
                print('... passed!')
            else:
                print('... failed!')
                nFailed += 1
                failedTests.append(test.name)

        print('-'*60)
        if nFailed > 0:
            print(f'{nFailed} Tests Failed')
            print(failedTests)
        else:
            print('All tests Succeeded!')

    def addTest(self, testClass, nTrials=1):
        self.myTests.append((testClass, nTrials))


class test:
    def __init__(self, seed=10):
        self.name = "Test Name Not Assigned"
        self.p1Class = agC.HumanAgent
        self.p2Class = agC.HumanAgent
        team1 = [(5, 5, u.meleeUnit),]
        team2 =  [(6,6, u.meleeUnit),]
        teamComp = [team1, team2]
        self.teamComp = teamComp
        self.pyGame = True
        self.seed = seed
        self.game = None

    def constructGame(self):
        self.game = g.GameManager(self.p1Class, self.p2Class, self.teamComp, self.pyGame, self.seed, False)


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
                    delta = u2Info[key] -  u1Info[key]
                    dInfo[key] = delta
                else:
                    dInfo[key] = (u1Info[key], u2Info[key])
        return dInfo
  
class execMoveMovement(test):
    def __init__(self, seed=10):
        super().__init__(seed)
        self.name = 'game.executeMove() - Movement Test'
    def execute(self):
        self.constructGame()
        unit = self.game.p1.team[0]
        preMove = self.storeUnitInfo(unit)
        actionSpace = self.game.getCurrentStateActions(self.game)
        random.shuffle(actionSpace)
        for action in actionSpace:
            unitID, actionType, info = action
            if actionType == 'move':
                self.game.executeMove(action)
                break
        postMove = self.storeUnitInfo(unit)
        delta = self.compareUnitInfo(preMove, postMove)
        assert len(delta.keys()) == 2
        assert delta['currentMovement'] == -1
        self.game.quit()
        return True

class execMoveMeleeAttack(test):
    def __init__(self, seed=10):
        super().__init__(seed)
        team1 = [(0, 0, u.meleeUnit),]
        team2 =  [(0,1, u.meleeUnit),]
        teamComp = [team1, team2]
        self.teamComp = teamComp
        self.name = 'game.executeMove() - Melee Attack Test'
        self.abilityToTest = abC.unarmedStrike
    def execute(self):
        self.constructGame()
        unit = self.game.p1.team[0]
        attacker_pre = self.storeUnitInfo(unit)
        actionSpace = self.game.getCurrentStateActions(self.game)
        for unitID, actionType, action in actionSpace:
            if actionType == 'ability':
                if action[0] == self.abilityToTest:
                    targetedUnitID = action[1]
                    target = self.game.allUnits[targetedUnitID]
                    target_pre = self.storeUnitInfo(target)
                    self.game.executeMove((unitID, actionType, action))
                    target_post = self.storeUnitInfo(target)
                    break
        ability = abC.unarmedStrike(unit)
        attacker_post = self.storeUnitInfo(unit)
        attacker_delta = self.compareUnitInfo(attacker_pre, attacker_post)
        target_delta = self.compareUnitInfo(target_pre, target_post)
        assert len(attacker_delta.keys()) == 1
        assert attacker_delta['currentActionPoints'] == ability.ap
        assert len(target_delta.keys()) == 1
        assert target_delta['currentHP'] == ability.dmg
        self.game.quit()
        return True
class execMoveRangedAttack(execMoveMeleeAttack):
    def __init__(self, seed=10):
        super().__init__(seed)
        team1 = [(0, 0, u.rangedUnit),]
        team2 =  [(0,1, u.rangedUnit),]
        teamComp = [team1, team2]
        self.teamComp = teamComp
        self.name = 'game.executeMove() - Ranged Attack Test'     
        self.abilityToTest = abC.rangedStrike 


class cloneTest(test):
    def __init__(self, seed=10):
        super().__init__(seed)
        self.teamComp = [[ [(0, 0), u.rangedUnit]], 
                        [[(0,1), u.rangedUnit]]]
        self.name = 'game.clone() - Object Instance Checks'   
        self.constructGame()   
    def execute(self):
        try:
            clone = self.game.clone()
            assert self.game is not clone
            assert clone.board is not self.game.board
            assert clone.board.instOM is not self.game.board.instOM
            # assert clone.board.instOM == self.game.instOM
            assert clone.board.instUM is not self.game.board.instUM
            # assert clone.board.instUM == self.game.board.instUM
            assert clone.board.instZM is not self.game.board.instZM
            # assert clone.board.instZM == self.game.instZM
            assert clone.board.gameObjectDict is not self.game.board.gameObjectDict
            # assert clone.board.gameObjectDict == self.game.board.gameObjectDict
            assert clone.board.GOT is not self.game.board.GOT
            # assert clone.board.GOT == self.game.board.GOT
            for unit in self.game.allUnits:
                compUnit = clone.getUnitByID(unit.ID)
                assert unit is not compUnit
                assert unit.ID == compUnit.ID
                u1 = self.storeUnitInfo(unit)
                u2 = self.storeUnitInfo(compUnit)
                delta = self.compareUnitInfo(u1, u2)
                assert len(delta.keys()) == 0
            return True
        except:
            return False
class getValidDirections(test):
    def __init__(self,seed=10):
        super().__init__(seed)
        self.name = 'board.getValidDirections()- Checking get valid directions'   
        self.constructGame()
    
    def execute(self):
        try:
            for unit in self.game.allUnits:
                if unit.position == (2, 4):
                    curUnit = unit
                    break
            out, outFlat = self.game.board.getValidDirections(curUnit)
            invalidDirs =  ['N', 'E']
            validDirs = ['S', 'SE', 'SW', 'NW', 'W', 'NE']
            passed = True
            for entry in out.keys():
                dir = entry[0]
                if dir in invalidDirs:
                    passed = False
                if dir not in validDirs:
                    passed = False
            for entry in outFlat:
                curDict = entry[1]['directionDict']
                key = list(curDict.keys())
                dir = key[0][0]
                if dir in invalidDirs:
                    passed = False
                if dir not in validDirs:
                    passed = False
            self.game.quit()

            return passed
            

        except:
            return False



tm = testManager()
tm.addTest(execMoveMovement, 10)
tm.addTest(execMoveMeleeAttack)
tm.addTest(execMoveRangedAttack)
tm.addTest(getValidDirections)
# tm.addTest(cloneTest())
tm.runTests()

