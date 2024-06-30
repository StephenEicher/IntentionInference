import importlib

import supersuit as ss
import torch
import yaml

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from fantasy_chess.env import fs_env as fc
from reinforcement_learning.MABuffer import MultiAgentReplayBuffer
from agilerl.hpo.mutation import Mutations
from agilerl.hpo.tournament import TournamentSelection
from agilerl.networks.evolvable_mlp import EvolvableMLP
from agilerl.training.train_multi_agent import train_multi_agent
from agilerl.utils.utils import create_population
from reinforcement_learning.pettingzoo_wrappers import PettingZooVectorizationParallelWrapper
# from agilerl.wrappers.pettingzoo_wrappers import PettingZooVectorizationParallelWrapper
from reinforcement_learning import createAgentPop as rl
import trainMultiAgent as tma

# !Note: If you are running this demo without having installed agilerl,
# uncomment and place the following above agilerl imports:



def main(INIT_HP, MUTATION_PARAMS, NET_CONFIG, DISTRIBUTED_TRAINING, use_net=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("============ AgileRL Multi-agent benchmarking ============")
    accelerator = None
    print(f"DEVICE: {device}")

    # env = importlib.import_module(f"{INIT_HP['ENV_NAME']}").parallel_env(
    #     max_cycles=25, continuous_actions=True
    # )
    env = fc.parallel_env()
    env.reset()
    env = PettingZooVectorizationParallelWrapper(env, n_envs=INIT_HP["NUM_ENVS"])
    env.reset()

    # Configure the multi-agent algo input arguments
    try:
        state_dims = [env.observation_space(agent).n for agent in env.agents]
        one_hot = True
    except Exception:
        state_dims = [env.observation_space(agent).shape for agent in env.agents]
        one_hot = False


    try:
        action_dims = [env.action_space(agent).n for agent in env.agents]
        INIT_HP["DISCRETE_ACTIONS"] = True
        INIT_HP["MAX_ACTION"] = None
        INIT_HP["MIN_ACTION"] = None
    except Exception:
        action_dims = [env.action_space(agent).shape[0] for agent in env.agents]
        INIT_HP["DISCRETE_ACTIONS"] = False
        INIT_HP["MAX_ACTION"] = [env.action_space(agent).high for agent in env.agents]
        INIT_HP["MIN_ACTION"] = [env.action_space(agent).low for agent in env.agents]

    INIT_HP["N_AGENTS"] = env.num_agents
    INIT_HP["AGENT_IDS"] = [agent_id for agent_id in env.agents]

    field_names = ["state", "action", "reward", "next_state", "done"]
    memory = MultiAgentReplayBuffer(
        INIT_HP["MEMORY_SIZE"],
        field_names=field_names,
        agent_ids=INIT_HP["AGENT_IDS"],
        device=device,
    )

    tournament = TournamentSelection(
        INIT_HP["TOURN_SIZE"],
        INIT_HP["ELITISM"],
        INIT_HP["POP_SIZE"],
        INIT_HP["EVAL_LOOP"],
    )

    mutations = Mutations(
        algo="MATD3",
        no_mutation=MUTATION_PARAMS["NO_MUT"],
        architecture=MUTATION_PARAMS["ARCH_MUT"],
        new_layer_prob=MUTATION_PARAMS["NEW_LAYER"],
        parameters=MUTATION_PARAMS["PARAMS_MUT"],
        activation=MUTATION_PARAMS["ACT_MUT"],
        rl_hp=MUTATION_PARAMS["RL_HP_MUT"],
        rl_hp_selection=MUTATION_PARAMS["RL_HP_SELECTION"],
        mutation_sd=MUTATION_PARAMS["MUT_SD"],
        min_lr=MUTATION_PARAMS["MIN_LR"],
        max_lr=MUTATION_PARAMS["MAX_LR"],
        min_learn_step=MUTATION_PARAMS["MIN_LEARN_STEP"],
        max_learn_step=MUTATION_PARAMS["MAX_LEARN_STEP"],
        min_batch_size=MUTATION_PARAMS["MIN_BATCH_SIZE"],
        max_batch_size=MUTATION_PARAMS["MAX_BATCH_SIZE"],
        agent_ids=INIT_HP["AGENT_IDS"],
        arch=NET_CONFIG["arch"],
        rand_seed=MUTATION_PARAMS["RAND_SEED"],
        device=device,
        accelerator=accelerator,
    )

    total_state_dims = sum(state_dim[0] for state_dim in state_dims)
    total_action_dims = sum(action_dims)

    if use_net:
        ## Critic nets currently set-up for MATD3
        actor = [
            EvolvableMLP(
                num_inputs=state_dim[0],
                num_outputs=action_dim,
                hidden_size=[64, 64],
                mlp_activation="ReLU",
                mlp_output_activation="Sigmoid",
                device=device,
            )
            for state_dim, action_dim in zip(state_dims, action_dims)
        ]
        NET_CONFIG = None
        critic = [
            [
                EvolvableMLP(
                    num_inputs=total_state_dims + total_action_dims,
                    num_outputs=1,
                    device=device,
                    hidden_size=[64, 64],
                    mlp_activation="ReLU",
                    mlp_output_activation=None,
                )
                for _ in range(INIT_HP["N_AGENTS"])
            ]
            for _ in range(2)
        ]
    else:
        actor = None
        critic = None

    agent_pop = rl.create_population(
        algo=INIT_HP["ALGO"],
        state_dim=state_dims,
        action_dim=action_dims,
        one_hot=one_hot,
        net_config=NET_CONFIG,
        INIT_HP=INIT_HP,
        actor_network=actor,
        critic_network=critic,
        population_size=INIT_HP["POP_SIZE"],
        num_envs=INIT_HP["NUM_ENVS"],
        device=device,
        accelerator=accelerator,
    )

    tma.train_multi_agent(
        env,
        INIT_HP["ENV_NAME"],
        INIT_HP["ALGO"],
        agent_pop,
        memory=memory,
        INIT_HP=INIT_HP,
        MUT_P=MUTATION_PARAMS,
        net_config=NET_CONFIG,
        swap_channels=INIT_HP["CHANNELS_LAST"],
        max_steps=INIT_HP["MAX_STEPS"],
        evo_steps=INIT_HP["EVO_STEPS"],
        eval_steps=INIT_HP["EVAL_STEPS"],
        eval_loop=INIT_HP["EVAL_LOOP"],
        learning_delay=INIT_HP["LEARNING_DELAY"],
        target=INIT_HP["TARGET_SCORE"],
        tournament=tournament,
        mutation=mutations,
        accelerator=accelerator,
        save_elite=True,
        elite_path = './fs'
    )

    if str(device) == "cuda":
        torch.cuda.empty_cache()


if __name__ == "__main__":
    with open("./reinforcement_learning/Configs/fc_matd3.yaml") as file:
        config = yaml.safe_load(file)
    INIT_HP = config["INIT_HP"]
    MUTATION_PARAMS = config["MUTATION_PARAMS"]
    NET_CONFIG = config["NET_CONFIG"]
    DISTRIBUTED_TRAINING = config["DISTRIBUTED_TRAINING"]
    main(INIT_HP, MUTATION_PARAMS, NET_CONFIG, DISTRIBUTED_TRAINING, use_net=False)
