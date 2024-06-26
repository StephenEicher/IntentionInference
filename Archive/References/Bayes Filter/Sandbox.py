import numpy as np
import scipy

import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF

w = np.array([1, -1, 1, -1])
class ParticleFilter:
    def __init__(self, mu, Sigma, Q, R):
        self.n_particles = 1000
        self.particles = np.random.multivariate_normal(mu, Sigma, self.n_particles)
        self.Q = Q
        self.w = None
        self.R = R
        self.mu0 = mu
    def predict(self, u):
        self.particles = self.f(self.particles, u)
        return
    
    def update(self, y):
        w_hat = np.zeros(self.n_particles)
        for idx, xi in enumerate(self.particles):
            w_hat[idx] = np.exp(-0.5*(y - self.g(xi)).T @ np.linalg.inv(self.R) @ (y-self.g(xi)) )
        
        #self.w = w_hat / np.sum(w_hat)
        self.w = w_hat / np.sum(w_hat + 1e-300)
        self.importanceResample()

    def importanceResample(self):
        cum_sum = np.cumsum(self.w)
        rand_numbers = np.random.rand(self.n_particles)
        idxs = np.searchsorted(cum_sum, rand_numbers)
        self.particles = self.particles[idxs]


    def f(self, x, u):
        noise = np.random.multivariate_normal(0*self.mu0, self.Q, x.shape[0])
        return w + noise
    
    def g(self, x):
        Sigma = 0.1*np.eye(4)
        noise = np.random.multivariate_normal(x, self.R,)

        y = x + noise
        return y
    def step(self, u, y):
        self.predict(u)
        self.update(y)
        return (self.particles, self.w)
    


tCur = 100
X = []
# w = np.random.uniform(size=nFeatures)
# w = w / np.sum(w)

nFeatures = len(w)
X = np.linspace(start=0, stop=tCur-1, num=tCur).reshape(-1, 1)
# y = w * X * np.sin(w * X)
y = w[np.newaxis, :] * np.ones([tCur, nFeatures])
# y[-30:, :] = y[-30, :] + np.random.uniform(size=nFeatures)
plt.figure()
for i in range(nFeatures):
    plt.plot(X, y[:, i], label=f'Feature {i}', linestyle="dotted")
plt.legend()
plt.xlabel("$x$")
plt.ylabel("$f(x)$")
_ = plt.title("True generative process")

mu = w
Sigma = 3 * np.eye(len(w))
Q = 0.1*np.eye(len(w))
R = 0.1*np.eye(len(w))



pf = ParticleFilter(mu, Sigma, Q, R)
x_est_samples_pf_hist = []
weights_pf_hist = []
x_est_pf_hist = []
for i, t in enumerate(X):
    x_est_samples_pf, weights_pf = pf.step(None, y[i, :])
    x_est_samples_pf_hist.append(x_est_samples_pf)
    weights_pf_hist.append(weights_pf)
    x_est_pf = np.average(x_est_samples_pf, weights=weights_pf, axis=0)
    x_est_pf_hist.append(x_est_pf)
x_est_pf_hist = np.vstack(x_est_pf_hist)



plt.figure(figsize = (8, 10))
for feature in range(nFeatures):
    plt.subplot(2, 2, feature+1)
    for idx, samples in enumerate(x_est_samples_pf_hist):
            x = X[idx] * np.ones(pf.n_particles)
            plt.scatter(x, samples[:, feature], s=5, color=[0.24, 0.6, 0], alpha=0.1)
    plt.scatter(X,x_est_pf_hist[:, feature], s=15, color=[1, 0.6, 0], label='Mean Estimated Weight', alpha=1)
    plt.plot(X, y[:, feature], label=f'Feature {feature}', linestyle="dotted", linewidth=3)
    plt.grid(True)
    plt.xlabel('Turn')
    plt.legend()
