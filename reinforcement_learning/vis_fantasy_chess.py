import os
import sys
import torch
import time
import pygame as pg
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from PIL import Image
import glob
from fantasy_chess import fc_env as fc
from reinforcement_learning.agilerl.MGMATD3 import MGMATD3
import fantasy_chess.env.agentClasses as ac
import fantasy_chess.env.gameClasses as g
import fantasy_chess.env.unitClasses as u
from PIL import Image
import glob
import shutil
import random
import numpy as np

if __name__ == "__main__":
    path = "./reinforcement_learning/Agents/fc_0.pt"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


    framePath = './reinforcement_learning/Videos/Frames/'
    try:
        shutil.rmtree(framePath)
    except:
        pass
    
    # env = fc.parallel_env(distRewardFn, ac.StaticAgent("Static"))
    # state, info = env.reset(options=True)
    # env.game.startPGVis()
    
    matd3 = MGMATD3.load(path, device)
    # Define grid dimensions
    grid_size = 8
    # Generate all possible coordinates in the grid
    all_coordinates = [(x, y) for x in range(grid_size) for y in range(grid_size)]
    # Randomly sample three unique coordinates
    coords = random.sample(all_coordinates, 3)

    team1 = [(coords[0][0], coords[0][1], u.meleeUnit), (coords[1][0], coords[1][1], u.rangedUnit)]
    team2 =  [(coords[2][0], coords[2][1], u.meleeUnit)]

    # team1 = [(0, 0, u.meleeUnit), (7,7, u.rangedUnit)]
    # team2 =  [(3, 3, u.meleeUnit)]

    teamComp = [team1, team2]

    if not os.path.exists(framePath):
        os.makedirs(framePath)

    p1 = ac.RLAgent('P1', matd3, ["melee", "ranged"])
    p2 = ac.StaticAgent('P2')
    a = g.GameManager(p1, p2, teamComp, inclPygame = True, framePath=framePath, noObstacles=True)
    a.start()
    crop_box = (0, 0, 220, 220)
    frames = [f for f in sorted(os.listdir(framePath)) if f.endswith('.png')]
    # Create a list to hold the images
    images = []
    for frame in frames:
        img_path = os.path.join(framePath, frame)
        images.append(Image.open(img_path).crop(crop_box))
    # Save as a GIF
    output_path = './reinforcement_learning/Videos/FC.gif'
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=50,  # Duration between frames in milliseconds
        loop=0  # Number of loops, 0 means infinite
    )
    


    # maxSteps = 50
    # agent_ids = env.agents
    # agent_reward = {agent_id: 0 for agent_id in agent_ids}
    # indi_agent_rewards = {
    #     agent_id: [] for agent_id in agent_ids
    # }  # Dictionary to collect inidivdual agent rewards

    # frame_count = 0
    # for _ in range(maxSteps):
    #     agent_mask = info["agent_mask"] if "agent_mask" in info.keys() else None
    #     env_defined_actions = (
    #         info["env_defined_actions"]
    #         if "env_defined_actions" in info.keys()
    #         else None
    #     )

    #     # Get next action from agent
    #     cont_actions, discrete_action = matd3.get_action(
    #         state,
    #         training=False,
    #         agent_mask=agent_mask,
    #         env_defined_actions=env_defined_actions,
    #     )
    #     pg.image.save(env.game.pygameUI.screen, f'./reinforcement_learning/Videos/Frames/{frame_count:04d}.png')
    #     frame_count += 1
    #     action = discrete_action
    #     for key in action.keys():
    #         action[key] = action[key][0]
    #     # Take action in environment
    #     state, reward, termination, truncation, info = env.step(action)
    #     time.sleep(0.25)
    #     pg.image.save(env.game.pygameUI.screen, f'./reinforcement_learning/Videos/Frames/{frame_count:04d}.png')
    #     frame_count += 1

    #     for agent_id, r in reward.items():
    #         agent_reward[agent_id] += r
    #         # Determine total score for the episode and then append to rewards list
    #         score = sum(agent_reward.values())
    #     # Stop episode if any agents have terminated
    #     if any(truncation.values()) or any(termination.values()):
    #         env.game.quit()
    #         break
            
