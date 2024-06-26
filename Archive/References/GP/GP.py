import numpy as np
from scipy.linalg import cho_factor, cho_solve
import scipy
### -------------------------------- ###
# Question 2a

class GaussianProcess():
    def __init__(self, X1, Y1, kernel_func=None, noise=1e-2):
        # X1: (N x 3) inputs of training data
        # Y1: (N x 1) outputs of training data
        # kernel_func: (function) a function defining your kernel. It should take the form f(X1, X2) = K, where K is N x N if X1, X2 are N x k.
        # where k is the number of feature dimensions

        self.noise = noise
        self.X1 = X1
        self.Y1 = Y1

        self.kernel_func = kernel_func

        self.compute_training_covariance()

    def compute_training_covariance(self):

        # Kernel of the observations
        Σ11 = self.kernel_func(self.X1, self.X1) + ((self.noise) * np.eye(len(self.X1)))

        self.Σ11 = Σ11

    def compute_posterior(self, X):
        # X: (N x k) set of inputs used to predict
        # mu: (N x 1) GP means at inputs X
        # Sigma: (N x N) GP means at inputs X

        # Kernel of observations vs to-predict
        Σ12 = self.kernel_func(self.X1, X)

        # Solve. Hint: Use scipy.linalg.solve to solve a system of linear equations. This is typically much faster than computing an inverse.
        # Several different ways of doing the same thing...
        # solved = (np.linalg.inv(self.Σ11) @ Σ12).T 
        # solved = scipy.linalg.solve(self.Σ11, Σ12, assume_a='pos').T

        c, low = cho_factor(self.Σ11)
        solved = cho_solve((c, low), Σ12).T

        # Compute posterior mean
        μ2 = solved @ (self.Y1 - np.mean(self.Y1))

        # Compute the posterior covariance
        Σ22 = self.kernel_func(X, X)

        Σ2 = Σ22 - (solved @ Σ12)

        return μ2, Σ2  # mean, covariance

# Question 2b
def plot_GP(mu, Sigma, X, ax):
    # mu: (N x 1) GP means
    # Sigma: (N x N) GP covariances
    # X: (N x k) id's for mu (the x-axis plot)
    # ax: (object) figure axes

    mu = mu.flatten()
    X = X.flatten()
    ax.plot(X, mu, label='mean')

    std = 2. * np.sqrt(np.diag(Sigma))

    confidence_interval_top = mu + std
    confidence_interval_bottom = mu - std

    print(confidence_interval_top)
    print(confidence_interval_bottom)
    ax.fill_between(X, confidence_interval_bottom, confidence_interval_top, color='green', alpha=0.3)

    return ax

###### KERNELS ######

# Question 2c
def radial_basis(X1, X2, sig=1., l=.1):
    n_samples, n_features = X1.shape
    m_samples, m_features = X2.shape
    X1 = X1.reshape(n_samples, 1, -1)
    X2 = X2.reshape(1, m_samples, -1)

    diff = X1 - X2

    K = sig**2 *np.exp(-0.5 * (1/l)**2 * np.sum(diff**2, axis=-1))

    return K

def exponential_sine_squared(X1, X2, sig=1., l=15., p=.2):
    n_samples, n_features = X1.shape
    m_samples, m_features = X2.shape
    X1 = X1.reshape(n_samples, 1, -1)
    X2 = X2.reshape(1, m_samples, -1)

    diff = X1 - X2

    K = sig**2 *np.exp(-0.5 * (1/l)**2 * np.sin( np.pi*np.sum(diff**2, axis=-1) / p)**2)

    return K

def combined_kernel(X1, X2, sig1=1., l1=.1, sig2=1., l2=12., p=.2):

    K_rbf = radial_basis(X1, X2, sig1, l1)

    K_ess = exponential_sine_squared(X1, X2, sig2, l2, p)

    K = K_rbf * K_ess

    return K
