import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import yaml
import fantasy_chess.env.agentClasses as ac
import reinforcement_learning.train_fantasy_chess as t
import numpy as np

def minDistRewardFn(env, postGame, agentGameActions, preUnits, postUnits):
    rewards = {a: 0 for a in env.agents}
    for agent in env.agents:
        unit = postUnits.get(env.agentUnitDict[agent], None)
        if unit is None:
            rewards[agent] = -100    
        else:
            unitID = unit.ID
            friendlies, enemies = postGame.getUnitRelations(unitID)
            distance = 8
            for enemyID in enemies:
                enemy = postGame.allUnits[enemyID]
                distance = np.min([distance, np.linalg.norm(enemy.position - unit.position)])
            #Punish for distance away from enemy
            rewards[agent] = rewards[agent] - distance
            gameAction = agentGameActions.get(agent, None)
            if gameAction is not None:
                _, actionType, actionInfo = gameAction
                if actionType == "ability":
                    if actionInfo[0] == -1:
                        rewards[agent] = rewards[agent] - 10
                    else:
                        rewards[agent] = rewards[agent] - 20
            
    return rewards

def completeRewardFn(env, postGame, agentGameActions, preUnits, postUnits):
    rewards = {a: 0 for a in env.agents}
    if postGame.gameOver:
        if postGame.winner == 0:
            rewards = {a: 100 for a in env.agents}
        else:
            rewards = {a: -100 for a in env.agents}
    else:
        for agent in env.agents:
            unit = postUnits.get(env.agentUnitDict[agent], None)
            if unit is None:
                rewards[agent] = -25    
            else:
                unitID = unit.ID
                deltaHP = preUnits[unitID].currentHP - postUnits[unitID].currentHP
                if deltaHP != 0:
                        rewards[agent] = rewards[agent] - 10
                #Punish for losing HP
                friendlies, enemies = postGame.getUnitRelations(unitID)
                distance = 99999
                for enemyID in enemies:
                    enemy = postGame.allUnits[enemyID]
                    distance = np.min([distance, np.linalg.norm(enemy.position - unit.position)])
                #Punish for distance away from enemy
                rewards[agent] = rewards[agent] - distance
                #Reward for using an ability that isn't end turn
                gameAction = agentGameActions.get(agent, None)
                if gameAction is not None:
                    _, actionType, actionInfo = gameAction
                    if actionType == "ability" and actionInfo[0] != -1:
                        rewards[agent] = rewards[agent] + 5  
                    else:
                        rewards[agent] = rewards[agent] - 1
    return rewards




def rewardFn(env, postGame, preUnits, postUnits):
    rewards = {a: 0 for a in env.agents}
    if postGame.gameOver:
        if postGame.winner == 0:
            rewards = {a: 100 for a in env.agents}
        else:
            rewards = {a: -100 for a in env.agents}
    else:
        for agent in env.agents:
            unit = postUnits.get(env.agentUnitDict[agent], None)
            unitID = unit.ID
            gameAction = env.agentGameActions.get(agent, None)
            if unit is None:
                rewards[agent] = -25    
            else:
                deltaHP = preUnits[unitID] - postUnits[unitID]
                _, actionType, actionInfo = gameAction
                if actionType == "ability" and actionInfo[0] != -1:
                    rewards[agent] = 5
                else:
                    rewards[agent] = -0.25
                if deltaHP[agent] != 0:
                    rewards[agent] = rewards[agent] - 10
    return rewards


if __name__ == "__main__":
    with open("./reinforcement_learning/Configs/fc_matd3.yaml") as file:
            config = yaml.safe_load(file)  
    INIT_HP = config["INIT_HP"]
    MUTATION_PARAMS = config["MUTATION_PARAMS"]
    NET_CONFIG = config["NET_CONFIG"]
    opp = ac.StaticAgent('Static Agent')
    ELITE_PATH = "./reinforcement_learning/Agents/fc_0.pt"
    CHECKPOINT_PATH = "./reinforcement_learning/Agents/Checkpoints/"
    POP_PATH = "./reinforcement_learning/Agents/Checkpoints/"
    t.train(minDistRewardFn, opp,INIT_HP, MUTATION_PARAMS, NET_CONFIG, ELITE_PATH, CHECKPOINT_PATH, POP_PATH=POP_PATH)
    # t.train(minDistRewardFn, opp,INIT_HP, MUTATION_PARAMS, NET_CONFIG, ELITE_PATH, CHECKPOINT_PATH)