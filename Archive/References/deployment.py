import abc
import csv
import pandas as pd
import random
import os
import numpy as np
import ch09 as dm

class Player(abc.ABC):
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.rank_overall = -1.
        self.rank_std = -1.
        self.position_rank = -1.
        self.points_proj = -1.
        self.points_std = -1.

    @abc.abstractmethod
    def sample(self):
        pass

class cfPlayer(Player):
    # Specific attributes or methods for RunningBack
    def sample(self):
        rankSample = max(1, np.random.normal(self.position_rank, self.rank_std/4))
        
        if self.position == "QB":
            # Coefficients for fit 1
            p1, p2, p3, p4, p5, p6 = -7.066, 9.137, 30.35, -4.595, -142, 146.2
            mean, std = 28.77, 16.44
        elif self.position == "WR":
            # Coefficients for fit 2
            p1, p2, p3, p4, p5, p6 = -6.345, 9.709, 10.28, 0.9466, -64.83, 79.23
            mean, std = 55.85, 32.04
        elif self.position == "TE":
            # Coefficients for fit 3
            p1, p2, p3, p4, p5, p6 = -5.373, 7.982, 7.705, -1.274, -36.08, 52.68
            mean, std = 38.01, 21.81
        elif self.position == "RB":
            # Coefficients for fit 4
            p1, p2, p3, p4, p5, p6 = -4.148, 5.992, 4.854, 4.993, -54.96, 77.89
            mean, std = 78.45, 45.08
        else:
            print("No fit! Using random")
            return random.uniform(0, 10.0)
        def poly_fit_function(x):
            # Normalize x
            normalized_x = (x - mean) / std
            # Calculate the polynomial function
            return p1 * normalized_x**5 + p2 * normalized_x**4 + p3 * normalized_x**3 + p4 * normalized_x**2 + p5 * normalized_x + p6
        return max(0, poly_fit_function(rankSample))


class Agent(abc.ABC):
    def __init__(self, name):
        self.name = name
        

    @abc.abstractmethod
    def make_pick(self, dc):
        pass

class RandomAgent(Agent):
    def make_pick(self, dc):
        ecr, player = random.choice(list(dc.available_players.values()))
        return player
class GreedyAgent(Agent):
    def make_pick(self, dc):
        #Choose Player with the lowest ECR
        ecr, player= min(list(dc.available_players.values()))
        return player

class MTCSAgent(Agent):
        def make_pick(self, dc):
        #Choose Player with the lowest ECR
            gamma = 0.9
            problem = dm.MDP(gamma, None, dc.getActions, None, dc.getReward)
            RolloutLookahead(P, RandomAgent())    

        #return player

class State:
    def __init__(self, available_players, agent_picks, num_rounds, cur_round):
        self.available_players = available_players
        self.agent_picks = agent_picks
        self.num_rounds = num_rounds
        self.cur_round = cur_round

class DraftController:
    def __init__(self, players_file, draft_info, player_class):
        self.agents = {}
        self.selfAgentName = 'Manager 0'
        for num in np.random.permutation(draft_info["num_managers"]):
            if num == 0:
                self.agents[self.selfAgentName] = draft_info["self_agent"](self.selfAgentName)
            else:
                self.agents[f'Manager {num}'] = draft_info["opp_agents"](f'Manager {num}')
        
        self.available_players, self.positions = self.load_players(players_file, player_class)
        self.drafted_players = {}
        self.num_rounds = draft_info["num_rounds"]
        self.snake_draft = draft_info.get("snake_draft", True)
        self.team_format = draft_info["team_format"]
        self.draft_order = self.generate_draft_order()
        self.agent_picks = {agent: {} for agent in self.agents.keys()}
        

    def load_players(self, file_path, player_class):
        df = pd.read_csv(file_path)
        playersByPos = {pos: {} for pos in df['Position'].unique()}
        allPlayers = {}
        for index, row in df.iterrows():
            player = player_class(row['Player.Name'], row['Position'])  # Use the provided player_class
            player.rank_overall = row['Avg.Rank']
            player.rank_std = row['Std.Dev']
            player.position_rank = len(playersByPos[row['Position']]) + 1
            player.points_proj = 0
            player.points_std = 0
            posDict = playersByPos[row['Position']]
            posDict[row['Player.Name']] = player
            allPlayers[row['Player.Name']] = (player.rank_overall, player)
        Positions = df['Position'].unique()
        return allPlayers, Positions

    def generate_draft_order(self):
        draft_order = []
        for round_number in range(1, self.num_rounds + 1):
            if self.snake_draft and round_number % 2 == 0:
                draft_order.extend(reversed(self.agents.keys()))
            else:
                draft_order.extend(self.agents.keys())
        return draft_order

    def run_draft(self):
        pick_num = 1
        round_num = 1
        for turn in self.draft_order:
            if pick_num % len(self.agents) == 1:
                print(f"\nRound {round_num}:")
                round_num += 1
            agent = self.agents[turn]
            pick = agent.make_pick(self)
            self.pickPlayer(turn, pick)
            print(f"{pick_num}: {agent.name} picks {pick.name} ({pick.position})")
            pick_num += 1
    
    def pickPlayer(self, agent, pick):
            agent_dict = self.agent_picks[agent]
            agent_dict[pick.name] = pick
            self.drafted_players[pick.name] = pick
            del self.available_players[pick.name]
    
    # def getActions(self):
    #     return self.available_players.keys()
    # def getReward(self, action):
    #     if action not in self.available_players.keys():
    #         #Not a valid action
    #         return -1
    #     ecr, player = self.available_players[action]
    #     return player.sample()

    # def getTransitionReward(self, action):
    #     if action not in self.available_players.keys():
    #         #Not a valid action
    #         return -1
    #     #Transition reward function will only ever be for Manager 0:
    #     r = getReward(self, action)
    #     self.pickPlayer(self.selfAgentName, self.available_players[action])
         
    #     return 
    # def getValue(self, dc):
    #     sampling = dc.sampleTeams()
    #     return sampling['Manager 0']['TOTAL']

    def sampleTeams(self):
        teamSampling = {}
        for agent in self.agent_picks.keys():
            team = self.agent_picks[agent]
            teamSampling[agent] = {}
            total = 0
            samplingDict = teamSampling[agent]
            samplingDict['TEAM'] = {}
            teamDict = samplingDict['TEAM']
            for player in team.keys():
                playerObj = team[player]
                playerScore =  playerObj.sample()
                teamDict[player] = (playerScore, playerObj)
                total = total + playerScore
            starters, startTotal = self.getStarters(teamDict)
            samplingDict['STARTERS'] = starters
            samplingDict['STARTERS TOTAL'] = startTotal
            samplingDict['TOTAL'] = total

            
        return teamSampling
    def getStarters(self, team):
        startersByPos = {key: {} for key in self.playersByPos}
        for player in team.keys():
            pointTotal, playerObj = team[player]
            position = playerObj.position
            if len(startersByPos[position]) < self.team_format[position]:
                startersByPos[position][player] = (pointTotal)
            else:
                removeCandidate = min(startersByPos[position]) 
                if startersByPos[position][removeCandidate] < pointTotal:
                    del startersByPos[position][removeCandidate]
                    startersByPos[position][player] = pointTotal
        starters = {}
        startTotals = 0
        for position in startersByPos.keys():
            for player in startersByPos[position].keys():
                startTotals = startTotals + startersByPos[position][player]
                starters[player] = startersByPos[position][player]
        
        return starters, startTotals
        
            



# Example usage
players_file_path = os.path.join(os.getcwd(), "2023 ECR.csv")
draft_info = {
    "self_agent": RandomAgent,
    "opp_agents": GreedyAgent,
    "num_managers": 2,
    "num_rounds": 5,
    "snake_draft": True,
    "team_format": {"QB": 1, "WR": 2, "RB": 2, "TE": 1, "DST": 1, "K": 1}
}
draft_controller = DraftController(players_file_path, draft_info, player_class=cfPlayer)
draft_controller.run_draft()
draft_controller.sampleTeams()