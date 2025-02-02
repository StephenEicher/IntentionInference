import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from fantasy_chess.env import gameClasses as g
from fantasy_chess.env import agentClasses as agC
from fantasy_chess.env import unitClasses as u
import time
import random
from fantasy_chess.env import abilityClasses as abC
import timeit
import numpy as np
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
        team1 = [(0, 0, u.meleeUnit),]
        team2 =  [(0,1, u.meleeUnit),]
        teamComp = [team1, team2]
        self.teamComp = teamComp
        self.name = 'game.clone() - Object Instance Checks'   
        self.constructGame()   
    def execute(self):
        try:
            clone = self.game.clone()
            assert self.game is not clone
            assert clone.board is not self.game.board
            assert clone.board.units_map is not self.game.board.units_map
            assert clone.board.obs_map is not self.game.board.obs_map
            assert self.game == clone
            assert self.game.board == clone.board
            for unit in self.game.allUnits.values():
                compUnit = clone.allUnits[unit.ID]
                assert unit is not compUnit
                assert unit == compUnit
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

class cloneBenchmark(test):
    def __init__(self, seed=10):
        super().__init__(seed)
        team1 = [(0, 0, u.meleeUnit),]
        team2 =  [(0,1, u.meleeUnit),]
        teamComp = [team1, team2]
        self.teamComp = teamComp
        self.name = 'game.clone() - Clone Benchmark'   
        self.constructGame()   
    def execute(self):
        testSetup = """
from gameClasses import GameManager
import unitClasses as u
import agentClasses as ac
team1 = [(5, 5, u.meleeUnit), (5, 6, u.meleeUnit)]
team2 = [(6, 6, u.meleeUnit)]
teamComp = [team1, team2]
g = GameManager(ac.HumanAgent, ac.RandomAgent, teamComp, inclPygame=True, seed=10)
"""
        testCode = """clone = g.clone()"""
        times = timeit.timeit(setup=testSetup, stmt=testCode, number=1000)
        # printing minimum exec. time
        print('Min Clone Time: {}'.format(min(times)))
        return True

class cloneBenchmark(test):
    def __init__(self, seed=10):
        super().__init__(seed)
        team1 = [(0, 0, u.meleeUnit),]
        team2 =  [(0,1, u.meleeUnit),]
        teamComp = [team1, team2]
        self.teamComp = teamComp
        self.name = 'Clone Benchmark'   
        self.constructGame()   
    def execute(self):
        testSetup = """
from gameClasses import GameManager
import unitClasses as u
import agentClasses as ac
team1 = [(5, 5, u.meleeUnit), (5, 6, u.meleeUnit)]
team2 = [(6, 6, u.meleeUnit)]
teamComp = [team1, team2]
g = GameManager(ac.HumanAgent, ac.RandomAgent, teamComp, inclPygame=True, seed=10)
"""
        testCode = """clone = g.clone()"""
        time = timeit.timeit(setup=testSetup, stmt=testCode, number=1000)
        meanTime = 1E6 * time/1000
        meanTime = np.round(meanTime, 4)
        print(f'Mean Time to Clone: {meanTime} (us)' )
        return True
class moveBenchmark(test):
    def __init__(self, seed=10):
        super().__init__(seed)
        team1 = [(0, 0, u.meleeUnit),]
        team2 =  [(0,1, u.meleeUnit),]
        teamComp = [team1, team2]
        self.teamComp = teamComp
        self.name = 'Execute Move Benchmark'   
        self.constructGame()   
    def execute(self):
        testSetup = """
from gameClasses import GameManager
import unitClasses as u
import agentClasses as ac
import random
team1 = [(1, 1, u.meleeUnit), (3, 3, u.meleeUnit)]
team2 = [(6, 6, u.meleeUnit)]
teamComp = [team1, team2]
original = GameManager(ac.RandomAgent, ac.RandomAgent, teamComp, inclPygame=True, seed=10)
g = original.clone()
"""
        testCode = """actionSpace = g.getCurrentStateActions(g)
g.executeMove(random.choice(actionSpace))"""
        time = timeit.timeit(setup=testSetup, stmt=testCode, number=1000)
        meanTime = 1E6 * time/1000
        meanTime = np.round(meanTime, 4)
        print(f'Mean Time to Exec Move: {meanTime} us' )
        return True

tm = testManager()
tm.addTest(execMoveMovement, 10)
tm.addTest(execMoveMeleeAttack)
tm.addTest(execMoveRangedAttack)
# tm.addTest(getValidDirections)
tm.addTest(cloneTest)
tm.addTest(cloneBenchmark)
tm.addTest(moveBenchmark)
tm.runTests()

