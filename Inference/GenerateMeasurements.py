import os
import pickle
import sys
import numpy as np
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_dir)
from game import GameManager
from AgentClasses import MCTSTestAgent
import time
gameID = 1
preDir = f'C:/Users/steph/Documents/IntentionInference/GameHistories/{gameID}/Pre/'
postDir = f'C:/Users/steph/Documents/IntentionInference/GameHistories/{gameID}/Post/'

from scipy.optimize import direct, Bounds
from scipy.stats import multivariate_normal



def quantifyDiff(state1, state2):
    s1 = state1.constructCompVars()
    s2 = state2.constructCompVars()
    pDiff = 0
    hpDiff = 0
    apDiff = 0
    actionDiff = 0
    if len(s1) != len(s2):
        actionDiff = 2
    else:
        for idx, entry in enumerate(s1):
            pDiff += np.linalg.norm(np.array(entry[1]) - np.array(s2[idx][1]))
            hpDiff += np.abs(entry[2] - s2[idx][2])
            apDiff += np.abs(entry[3] - s2[idx][3])
    return actionDiff + pDiff + hpDiff + apDiff


def cross_entropy_optimization(dim, n_samples, n_elite, max_iter, tol):
    # Initialize parameters
    mean = np.zeros(dim)
    cov = 3*np.eye(dim)
    
    for _ in range(max_iter):
        # Generate samples
        samples = multivariate_normal.rvs(mean, cov, size=n_samples)
        
        # Evaluate samples
        scores = np.array([objective_function(sample) for sample in samples])
        
        # Select elite samples
        elite_indices = scores.argsort()[:n_elite]
        elite_samples = samples[elite_indices]
        
        # Update the distribution parameters
        mean_new = np.mean(elite_samples, axis=0)
        cov_new = np.cov(elite_samples, rowvar=False)
        
        # Check for convergence
        if np.linalg.norm(mean - mean_new) < tol and np.linalg.norm(cov - cov_new) < tol:
            break
        
        mean, cov = mean_new, cov_new
    
    return mean, cov



files = os.listdir(preDir)
# Filter to include only .pkl files (if your pickled files have a different extension, change it accordingly)
files = [f for f in files if f.endswith('.pkl')]
pred_mean = []
pred_cov = []
# Iterate through each pickled file and de-pickle it
for file_name in files:
    preFile = os.path.join(preDir, file_name)
    postFile = os.path.join(postDir, file_name)
    with open(preFile, 'rb') as file:
        preState = pickle.load(file)
    with open(preFile, 'rb') as file:
        postState = pickle.load(file)    
    
  
    
    def objective_function(x):
        test_state = preState.clone()
        test_state.p2.assignWeights(x)
        test_state.p2.time_limit = 200
        test_state.p2.d = 6
        test_state.queryAgentForMove()
        y = quantifyDiff(preState, test_state)
        return y
    tStart = time.time()
    optimal_mean, optimal_cov = cross_entropy_optimization(4, 50, 10, 10, 0.1)
    dur = time.time() - tStart
    print('Time to complete:')
    print(dur)
    # optimal_mean = np.random.randint(1)
    # optimal_cov = np.random.randint(1)
    pred_mean.append(optimal_mean)
    pred_cov.append(optimal_cov)
    print(optimal_mean, optimal_cov)

    
with open(f'./GameHistories/{gameID}/mu_meas.pkl', 'wb') as file:
            pickle.dump(pred_mean, file)
with open(f'./GameHistories/{gameID}/sigma_meas.pkl', 'wb') as file:
            pickle.dump(pred_cov, file)
    # bounds = Bounds([-1.5, -1.5, -1.5, -1.5], [1.5, 1.5, 1.5, 1.5])
    # result = direct(objective_function, bounds, len_tol=0.1, maxiter=100)
    # result.x, result.fun, result.nfev







