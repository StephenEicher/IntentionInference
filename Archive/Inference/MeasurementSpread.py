import numpy as np
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
rng = np.random.RandomState(1)


tCur = 60
X = []
# w = np.random.uniform(size=nFeatures)
# w = w / np.sum(w)
n = 50
w = np.array([1, -1, 1, -1])
w = w[:, np.newaxis]  * np.ones([4, n])

noise = 1.5*rng.normal(loc=0.0, scale=2, size=(4, n))
bias = 0.3

plt.figure()
for idx, weight in enumerate(w):
    bias = np.random.uniform(-1, 1)
    noise[idx, :] = noise[idx, :] + bias
    err = np.mean(noise[idx, :])
    plt.scatter(w[idx, :] + noise[idx, :], idx*np.ones(noise[idx, :].shape), s=1, label=f'Err= {np.round(err, 2)}')
    plt.scatter(weight, idx*np.ones(noise[idx, :].shape), s=10)

# Adjust the layout to make space for the legend
plt.subplots_adjust(bottom=0.4)
plt.title('Measurement Noise Characterization')
plt.ylabel('Feature')
plt.xlabel('Measurement')
plt.yticks([0, 1, 2, 3])
plt.legend()

