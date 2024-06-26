import abc
import csv
import pandas as pd
import random
import os
import numpy as np
import copy
import MCTS
import math
from typing import Any, Callable
from fuzzywuzzy import fuzz
import statistics
#import ch09 as dm

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
        rankSample = max(1, np.random.normal(self.position_rank, self.rank_std/2))
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
            return 18 * random.uniform(0, 10.0)
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
        return player.name
    
class playerEntry(Agent):
    def make_pick(self, dc):
        # Get user input for the player name
        user_input = input("Enter the player name: ")

        # Get a list of available player names
        available_player_names = list(dc.available_players.keys())

        # Find the closest match using Levenshtein distance
        best_match = max(available_player_names, key=lambda name: fuzz.ratio(name, user_input))

        # Get the corresponding player object
        selected_player = dc.available_players[best_match][1]

        return selected_player.name


class SoftMaxAgent(Agent):
    #Choose Player with the lowest ECR with increasing noise
    def make_pick(self, dc):
        # Get a list of (ecr, player) tuples sorted by ECR in ascending order
        sorted_players = sorted(dc.available_players.values(), key=lambda x: x[0])
        curRound = len(dc.agent_picks[self.name]) + 1
        n = math.ceil(1.5*curRound)

        # Extract the names of the first n players
        pQb = {5: .3, 6: .4, 7: .5, 8: .6, 9: .7, 10: .8, 11: .9, 12: 1.00, 13: 1.00}
        pTE = {5: .2, 6: .3, 7: .4, 8: .5, 9: .6, 10: .6, 11: .7, 12: 0.8, 13: 1.00}
        if not dc.hasPosition(self.name, "QB")[0] and curRound >= min(pQb):
            if random.random() < pQb[curRound]:
                for entry in sorted_players:
                    ECR, playerObj = entry
                    if playerObj.position == "QB":
                        return playerObj.name
        elif not dc.hasPosition(self.name, "TE")[0] and curRound >= min(pTE):
            if random.random() < pTE[curRound]:
                for entry in sorted_players:
                    ECR, playerObj = entry
                    if playerObj.position == "TE":
                        return playerObj.name           
        selected_players = [player.name for _, player in sorted_players[:n]]
        return random.choice(selected_players)

class GreedyAgent(Agent):
    def make_pick(self, dc):
        #Choose Player with the lowest ECR
        ecr, player= min(list(dc.available_players.values()))
        return player.name

class MCTSAgent(Agent):
        def make_pick(self, dc):
        #Choose Player with the lowest ECR
            gamma = 0.9
            problem = MCTS.MDP(gamma, None, dc.getActions, None, dc.getReward, dc.getTransitionReward)
            d = 12
            m = 500 #number of simulations
            c = 500 #Exploration
            solver = MCTS.MonteCarloTreeSearch(problem, {}, {}, d, m, c, dc.getValue)
            return solver(dc)
        #return player


class DraftController:
    def __init__(self, players_file, draft_info, player_class):
        self.agents = {}
        self.playerAgentName = 'Player'
        idx = 1
        for num in range(draft_info["num_managers"]):
            if num == (draft_info["self_pick"] - 1):
                self.agents[self.playerAgentName] = draft_info["self_agent"](self.playerAgentName)
            else:
                if draft_info['player_entry']:
                    self.agents[f'Opponent {idx}'] = playerEntry(f'Opponent {idx}')
                else:
                    self.agents[f'Opponent {idx}'] = draft_info["opp_agents"](f'Opponent {idx}')
                self.agents[f'Opponent {idx}'].name = f'Opponent {idx}'
                idx = idx + 1
        self.oppClass = draft_info["opp_agents"]
        self.playerClass = draft_info["self_agent"]
        self.available_players, self.positions = self.load_players(players_file, player_class)
        self.drafted_players = {}
        self.num_rounds = draft_info["num_rounds"]
        self.snake_draft = draft_info.get("snake_draft", True)
        self.team_format = draft_info["team_format"]
        self.draft_order = self.generate_draft_order(draft_info["self_pick"])
        self.curRound = 1
        self.agent_picks = {agent: {} for agent in self.agents.keys()}
        self.stateValue = 0
        self.root = True
        self.progressToPlayer()

    def clone(self):
        # Create a new instance of DraftController
        cloned_draft_controller = DraftController.__new__(DraftController)

        # Copy primitive attributes
        cloned_draft_controller.num_rounds = copy.deepcopy(self.num_rounds)
        cloned_draft_controller.snake_draft = copy.deepcopy(self.snake_draft)
        cloned_draft_controller.team_format = copy.deepcopy(self.team_format)
        cloned_draft_controller.curRound = copy.deepcopy(self.curRound)
        cloned_draft_controller.root = False
        # Copy dictionaries and nested structures
        newAgentList = {}
        for agent in self.agents.keys():
            if agent != self.playerAgentName:
                newAgentList[agent] = self.oppClass(agent)
            else:
                newAgentList[agent] = self.playerClass(agent)
        cloned_draft_controller.agents = newAgentList
        cloned_draft_controller.stateValue = copy.deepcopy(self.stateValue)
        cloned_draft_controller.drafted_players = copy.deepcopy(self.drafted_players)
        cloned_draft_controller.agent_picks = copy.deepcopy(self.agent_picks)
        cloned_draft_controller.available_players = copy.deepcopy(self.available_players)
        cloned_draft_controller.positions = copy.deepcopy(self.positions)
        cloned_draft_controller.draft_order = copy.deepcopy(self.draft_order)
        cloned_draft_controller.playerAgentName = self.playerAgentName

        # Return the cloned instance
        return cloned_draft_controller

    def hasPosition(self, agent, position):
        team = self.agent_picks[agent]
        nPosition = 0
        for player in team.keys():
            playerObj = team[player]
            if playerObj.position == position:
                nPosition = nPosition + 1

        return (nPosition > 0, nPosition)
    
    def progressToPlayer(self):
        #Set the game state to be ready for the player to decide
        while len(self.draft_order) > 0:
            turn = self.draft_order[0]
            if turn == self.playerAgentName:
                break
            else:
                agent = self.agents[turn]
                pickName = agent.make_pick(self)
                ECR, pickObj = self.available_players[pickName]
                self.pickPlayer(agent, pickName)
                if self.root:
                    print(f"{agent.name} picks {pickName} ({pickObj.position}, {ECR})")

    
    def playerAgentPick(self):
        if len(self.draft_order) > 0:
            if self.draft_order[0] != self.playerAgentName:
                print("ERROR! Not players turn!")
                return
            else:
                self.curRound = self.curRound + 1
                playerAgent = self.agents[self.draft_order[0]]
                pickName = playerAgent.make_pick(self)



                ECR, pickObj = self.available_players[pickName]
                if self.root:
                    print(f"{self.playerAgentName} picks {pickName} ({pickObj.position}, {ECR})")
                
                self.pickPlayer(playerAgent, pickName)
                self.progressToPlayer()
        else:
            print("ALL PICKS DONE!")
            return


    def load_players(self, file_path, player_class):
        df = pd.read_csv(file_path)
        playersByPos = {pos: {} for pos in df['Position'].unique()}
        allPlayers = {}
        for index, row in df.iterrows():
            if row['Position'] != "DST" and row['Position'] != "K":
                player = player_class(row['Player.Name'], row['Position'])
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

    def generate_draft_order(self, self_pick):
        draft_order = []
        for round_number in range(1, self.num_rounds + 1):
            if self.snake_draft and round_number % 2 == 0:
                draft_order.extend(reversed(self.agents.keys()))
            else:
                draft_order.extend(self.agents.keys())
        return draft_order

    
    def pickPlayer(self, agent, pickName):
            ECR, pickObj = self.available_players[pickName]
            agent_dict = self.agent_picks[agent.name]
            agent_dict[pickName] = pickObj
            self.drafted_players[pickName] = pickObj
            del self.available_players[pickName]
            self.draft_order.remove(self.draft_order[0])
    
    def getActions(self, state):
        allActions = list(state.available_players.keys())
        ECRs = np.array([ECR for ECR, _ in state.available_players.values()])
        sorted_indices = np.argsort(ECRs)
        sortedAllActions = [allActions[i] for i in sorted_indices]
        return sortedAllActions[0:19]





    def getValue(self, state):
        summary = state.evaluateTeams()
        deltaTotal = 0
        deltaStarters = 0
        summaryDict = {}
        for entry in summary:
            summaryDict[entry[0]] = (entry[1], entry[2])
        deltaTotal = []
        deltaStarters = []
        for agent in summaryDict.keys():
            if agent != self.playerAgentName:
                deltaTotal.append(summaryDict[self.playerAgentName][1] - summaryDict[agent][1])
                deltaStarters.append(summaryDict[self.playerAgentName][0] - summaryDict[agent][0])
        
        deltaTotal = sorted(deltaTotal)
        deltaStarters = sorted(deltaStarters)
        return sum(deltaTotal[0:4]) + 0.7*sum(deltaStarters[0:4])
    
    def getTransitionReward(self, state, pickName):
        
        if pickName not in self.available_players.keys():
            #Not a valid action
            return -1
        ECR, pickObj = state.available_players[pickName]
        #Transition reward function will only ever be for Manager 0:
        Ucur = state.getValue(self)
        sprime = state.clone()
        sprime.pickPlayer(self.agents[self.playerAgentName], pickName)
        sprime.progressToPlayer()
        if sprime.hasPosition(self.playerAgentName, 'QB')[1] > 2:
            Uprime = -10000
        elif sprime.hasPosition(self.playerAgentName,'TE')[1] > 2:
            Uprime = -10000
        else:
            Uprime = sprime.getValue(self)
        return (sprime, Uprime - Ucur)
    
    def getReward(self,state, pickName):
        sprime, r = state.getTransitionReward(state, pickName)
        return 0

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
        startersByPos = {key: {} for key in self.positions}
        startersByPos["FLEX"] = {}
        for player in team.keys():
            pointTotal, playerObj = team[player]
            playerPosition = playerObj.position
            if len(startersByPos[playerPosition]) < self.team_format[playerPosition]:
                startersByPos[playerPosition][player] = (pointTotal)
            elif (playerPosition == "RB" or playerPosition == "WR") and (len(startersByPos["FLEX"]) < self.team_format["FLEX"]):
                startersByPos["FLEX"][player] = (pointTotal)
            else:
                if (playerPosition == "RB" or playerPosition == "WR") and len(startersByPos["FLEX"]) > 0:
                    if startersByPos[playerPosition][min(startersByPos[playerPosition])] <  startersByPos["FLEX"][min(startersByPos["FLEX"])]:
                        removeCandidate = min(startersByPos[playerPosition])
                        removePosition = playerPosition
                    else:
                        removeCandidate = min(startersByPos["FLEX"])
                        removePosition = "FLEX"
                else:
                    removeCandidate = min(startersByPos[playerPosition]) 
                    removePosition = playerPosition
                if startersByPos[removePosition][removeCandidate] < pointTotal:
                    del startersByPos[removePosition][removeCandidate]
                    startersByPos[removePosition][player] = pointTotal
        starters = {}
        startTotals = 0
        for position in startersByPos.keys():
            for player in startersByPos[position].keys():
                startTotals = startTotals + startersByPos[position][player]
                starters[player] = startersByPos[position][player]
        
        return starters, startTotals

    def evaluateTeams(self, dfResults = False):
        starterScores = {agent : 0 for agent in self.agents.keys()}
        allScores = {agent : 0 for agent in self.agents.keys()}
        nTrials = 17
        for i in range(nTrials):
            teamSampling = self.sampleTeams()
            for agent in teamSampling.keys():
                starterScores[agent] = starterScores[agent]  + teamSampling[agent]['STARTERS TOTAL'] /  nTrials
                allScores[agent] = starterScores[agent]  + + teamSampling[agent]['TOTAL'] / nTrials
        summary = []
        for agent in starterScores.keys():
            summary.append((agent, starterScores[agent], allScores[agent]))
        if dfResults:
            df = pd.DataFrame({agent: [] for agent in draft_controller.agents.keys()})
            for agent in self.agents.keys():
                entry = list(self.agent_picks[agent].keys())
                for idx, player in enumerate(entry):
                    entry[idx] = (player, self.drafted_players[player].position)
                entry.append(starterScores[agent])
                entry.append(allScores[agent])
                df[agent] = entry
                df.to_csv('Results.csv', index=False)
            return sorted(summary, reverse=True), df
        else:
            return sorted(summary, reverse=True)


# Example usage
players_file_path = os.path.join(os.getcwd(), "2023 ECR.csv")

totalDelta = []
startersDelta = []
maxTotalDelta = []
minTotalDelta = []
maxStartersDelta = []
minStartersDelta = []
for num in range(1):
    player_pick = random.randint(1, 12)
    draft_info = {
        "self_agent": MCTSAgent,
        "opp_agents": SoftMaxAgent,#playerEntry,
        "player_entry": False,
        "self_pick": player_pick,
        "num_managers": 12,
        "num_rounds": 13,
        "snake_draft": True,
        "team_format": {"QB": 1, "WR": 2, "RB": 2, "TE": 1, "DST": 0, "K": 0, "FLEX": 1}
    }


    draft_controller = DraftController(players_file_path, draft_info, player_class=cfPlayer)

    for i in range(20):
        draft_controller.playerAgentPick()
    summary, results = (draft_controller.evaluateTeams(True))

    total = results.iloc[-1].tolist()
    playerTotal = total[player_pick - 1]
    total.remove(playerTotal)
    starters = results.iloc[-2].tolist()
    playerStarters = starters[player_pick - 1]
    starters.remove(playerStarters)


    totalDelta.append(playerTotal - np.mean(total))
    maxTotalDelta.append(playerTotal - np.max(total))
    minTotalDelta.append(playerTotal - np.min(total))
    startersDelta.append(playerStarters - np.mean(starters))
    maxStartersDelta.append(playerTotal - np.max(starters))
    minStartersDelta.append(playerTotal - np.min(starters))
    print(results)

print(f'Total: {np.mean(totalDelta)}')
print(f'Max Total: {np.mean(maxTotalDelta)}')
print(f'Min Tota;: {np.mean(minTotalDelta)}')
print(f'Starters: {np.mean(startersDelta)}')
print(f'Max Starters: {np.mean(maxStartersDelta)}')
print(f'Min Starters: {np.mean(minStartersDelta)}')