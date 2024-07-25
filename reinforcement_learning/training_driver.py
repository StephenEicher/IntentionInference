import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import yaml
import fantasy_chess.env.agentClasses as ac
import reinforcement_learning.train_fantasy_chess as t
import numpy as np


def randomRewardFn(env, postGame, agentGameActions, preUnits, postUnits):
    rewards = {a: np.random.rand() for a in env.agents}
    return rewards

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
                        rewards[agent] = rewards[agent] - 2
            
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
    INIT_POP_PATH = "./reinforcement_learning/Agents/Checkpoints/400000/"
    ##########
    '''
    Start training based on loaded configuration. Save checkpoints in to subfolders in CHECKPOINT_PATH
    '''
    # t.train(minDistRewardFn, opp,INIT_HP, MUTATION_PARAMS, NET_CONFIG, ELITE_PATH, CHECKPOINT_PATH)

    #######
    '''
    Resume training from checkpoints saved at CHECKPOINT_PATH
    '''
    t.train(minDistRewardFn, opp,INIT_HP, MUTATION_PARAMS, NET_CONFIG, ELITE_PATH, CHECKPOINT_PATH, POP_PATH=INIT_POP_PATH)






