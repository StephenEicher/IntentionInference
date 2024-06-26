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
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
import matplotlib.pyplot as plt


def quantifyDiff(state1, state2):
    s1 = state1.constructCompVars()
    s2 = state2.constructCompVars()
    pDiff = 0
    hpDiff = 0
    apDiff = 0
    actionDiff = 0
    s1Units = set([entry[0] for entry in s1])
    s2Units = set([entry[0] for entry in s2])
    missingS2Units = list(s1Units.difference(s2Units))
    missingS1Units = list(s2Units.difference(s1Units))

    for unitID in missingS1Units:
         s1.append((unitID, (0, 0), 0, 0, 0, 0, False, False, False))
    s1.sort()
    for unitID in missingS2Units:
         s2.append((unitID, (0, 0), 0, 0, 0, 0, False, False, False))
    s2.sort()
        

    for idx, entry in enumerate(s1):
        pDiff += np.linalg.norm(np.array(entry[1]) - np.array(s2[idx][1]))
        hpDiff += np.abs(entry[2] - s2[idx][2])
        apDiff += np.abs(entry[3] - s2[idx][3])

    return actionDiff + pDiff + hpDiff + apDiff


def cross_entropy_optimization(mu0, sigma0, n_samples, n_elite, max_iter, tol):
    # Initialize parameters
    mean = mu0
    cov = sigma0
    
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

def plotGP(X, y_predict, y_predict_std, y_train, nFeatures, noise_std, truth):
    
    plt.figure(figsize = (10, 8))
    for feature in range(nFeatures):
        plt.subplot(2, 2, feature+1)
        # plt.plot(X, truth[:, feature], label='Truth', linestyle="dotted")
        plt.plot(X, y_train[:, feature], label=r"$f(x) = x \sin(x)$", linestyle="dotted")
        plt.errorbar(
            X,
            y_train[:, feature],
            noise_std[:, feature],
            linestyle="None",
            color="tab:blue",
            marker=".",
            markersize=5,
            label="Observations",
        )
        plt.plot(X, y_predict[:, feature], label="Mean prediction")
        plt.fill_between(
            X.ravel(),
            y_predict[:, feature] - 1.96 * y_predict_std[:, feature],
            y_predict[:, feature] + 1.96 * y_predict_std[:, feature],
            color="tab:orange",
            alpha=0.5,
            label='95% confidence interval',
        )
        plt.legend()
        nPlot = len(X)
        plt.xlabel('Turn Number')
        plt.ylabel(f'Feature {feature}')
        plt.grid(True)
    plt.savefig(f'C:/Users/steph/Documents/IntentionInference/GameHistories/{gameID}/Plots/{nPlot}.png')     


def extractWeights(state):
    weights = []
    dic = state.p2.weights
    weights.append(dic['action'])
    weights.append(dic['no_action'])
    weights.append(dic['end_game'])
    weights.append(dic['n_turns'])
    return np.array(weights)

files = os.listdir(preDir)
# Filter to include only .pkl files (if your pickled files have a different extension, change it accordingly)
files = [f for f in files if f.endswith('.pkl')]
meas_mean = []
meas_sigma = []
mu0 = np.array([1, -1, 1, -1])
sigma0 = 4*np.eye(4)
# Iterate through each pickled file and de-pickle it
X = []
turns = []
fileIdxs = []
meas_std = []
for idx, file_name in enumerate(files):
    turnNumber = file_name.replace("turn_", "")
    turnNumber = turnNumber.split('.')[0]
    turnNumber = int(turnNumber)  
    turns.append(turnNumber)
    fileIdxs.append(idx)

fileIdxs = [x for _, x in sorted(zip(turns, fileIdxs))]
turns = np.array(turns)
turns = np.sort(turns)

nFeatures = len(mu0)


Y_predict = []
Y_predict_std = []
truth = []

for idx, fidx in enumerate(fileIdxs[1:]):
    file_name = files[fidx]
    
    preFile = os.path.join(preDir, file_name)
    postFile = os.path.join(postDir, file_name)

    with open(preFile, 'rb') as file:
        preState = pickle.load(file)
    with open(preFile, 'rb') as file:
        postState = pickle.load(file)    
    

         
    
    def objective_function(x):
        test_state = preState.clone()
        test_state.p2.assignWeights(x)
        test_state.p2.time_limit = 300
        test_state.p2.d = 5
        test_state.queryAgentForMove()
        y = quantifyDiff(preState, test_state)
        return y
    tStart = time.time()
    

    if idx > 1:
        kernel = 1 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 5e2))
        # kernel = 1 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
        gaussian_process = GaussianProcessRegressor(
            kernel=kernel, alpha=0.5**2, n_restarts_optimizer=9
            )

        X_plot = turns[:idx]
        X = np.ones(len(X_plot)).reshape(-1, 1)
        Y_train = np.vstack(meas_mean)
        gaussian_process.fit(X, np.vstack(Y_train))
        # gaussian_process.fit(X_plot.reshape(-1, 1), np.vstack(Y_train))
        gaussian_process.kernel_
        gp_mean, gp_std = gaussian_process.predict(np.array(1).reshape(-1, 1), return_std=True)
        mu0 = gp_mean.squeeze()
        sigma0 = np.eye(nFeatures)*gp_std**2

        # gp_mean, gp_std = gaussian_process.predict(X_plot.reshape(-1, 1), return_std=True)
        # mu0 = gp_mean[-1]
        # sigma0 = np.eye(nFeatures)*gp_std[-1]**2

        Y_predict.append(gp_mean.squeeze())
        Y_predict_std.append(gp_std)



        if idx > 1:
            try:
                # plotGP(np.array(X_plot), gp_mean, gp_std, Y_train, nFeatures, np.vstack(meas_std).squeeze(), np.vstack(truth).squeeze())
                plotGP(np.array(X_plot), np.vstack(Y_predict), np.vstack(Y_predict_std), Y_train, nFeatures, np.vstack(meas_std).squeeze(), np.vstack(truth).squeeze())
            except:
                print('Error plotting!')
    truth.append(extractWeights(preState))

    # mu, sigma = cross_entropy_optimization(mu0, sigma0, 250, 20, 8, 0.1)
    mu, sigma = cross_entropy_optimization(mu0, sigma0, 5, 5, 2, 0.1)
    dur = time.time() - tStart
    print('Time to complete:')
    print(dur)
    meas_mean.append(mu)
    meas_sigma.append(sigma)
    meas_std.append(np.sqrt(np.abs(np.diag(sigma))))
    print(mu, sigma)

GPData = {}
GPData['Y_pred'] = np.vstack(Y_predict)
GPData['Y_pred_std'] = np.vstack(Y_predict_std)
GPData['Y_train'] = Y_train
GPData['X_plot'] = X_plot
GPData['truth'] = np.vstack(truth)
GPData['meas_mean'] = np.vstack(meas_mean)
GPData['meas_sigma'] = np.vstack(meas_sigma).squeeze()

    
with open(f'./GameHistories/{gameID}/mu_meas.pkl', 'wb') as file:
            pickle.dump(meas_mean, file)
with open(f'./GameHistories/{gameID}/sigma_meas.pkl', 'wb') as file:
            pickle.dump(meas_sigma, file)
with open(f'./GameHistories/{gameID}/GP.pkl', 'wb') as file:
            pickle.dump(GPData, file)         

    # bounds = Bounds([-1.5, -1.5, -1.5, -1.5], [1.5, 1.5, 1.5, 1.5])
    # result = direct(objective_function, bounds, len_tol=0.1, maxiter=100)
    # result.x, result.fun, result.nfev

