import os
import sys
import torch
import time
import pygame as pg
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from PIL import Image
import glob
from fantasy_chess.env import fs_env as fc
from reinforcement_learning.agilerl.MGMATD3 import MGMATD3

if __name__ == "__main__":
    path = "./reinforcement_learning/Agents/fs.pt"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    
    env = fc.parallel_env()
    state, info = env.reset(options=True)
    env.game.startPGVis()
    
    matd3 = MGMATD3.load(path, device)

    maxSteps = 50
    agent_ids = env.agents
    agent_reward = {agent_id: 0 for agent_id in agent_ids}
    indi_agent_rewards = {
        agent_id: [] for agent_id in agent_ids
    }  # Dictionary to collect inidivdual agent rewards

    frame_count = 0
    for _ in range(maxSteps):
        agent_mask = info["agent_mask"] if "agent_mask" in info.keys() else None
        env_defined_actions = (
            info["env_defined_actions"]
            if "env_defined_actions" in info.keys()
            else None
        )

        # Get next action from agent
        cont_actions, discrete_action = matd3.get_action(
            state,
            training=False,
            agent_mask=agent_mask,
            env_defined_actions=env_defined_actions,
        )
        pg.image.save(env.game.pygameUI.screen, f'./reinforcement_learning/Videos/Frames/{frame_count:04d}.png')
        frame_count += 1
        action = discrete_action
        for key in action.keys():
            action[key] = action[key][0]
        # Take action in environment
        state, reward, termination, truncation, info = env.step(action)
        time.sleep(0.25)
        pg.image.save(env.game.pygameUI.screen, f'./reinforcement_learning/Videos/Frames/{frame_count:04d}.png')
        frame_count += 1

        for agent_id, r in reward.items():
            agent_reward[agent_id] += r
            # Determine total score for the episode and then append to rewards list
            score = sum(agent_reward.values())
        # Stop episode if any agents have terminated
        if any(truncation.values()) or any(termination.values()):
            env.game.quit()
            break
            
