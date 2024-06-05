import numpy as np
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
rng = np.random.RandomState(1)


tCur = 60
X = []
# w = np.random.uniform(size=nFeatures)
# w = w / np.sum(w)
w = np.array([0.2, -0.5, 0.7, 0.9])
nFeatures = len(w)
X = np.linspace(start=0, stop=tCur-1, num=tCur).reshape(-1, 1)
# y = w * X * np.sin(w * X)
y = w[np.newaxis, :] * np.ones([tCur, nFeatures])
y[-30:, :] = y[-30, :] + np.random.uniform(size=nFeatures)
plt.figure()
plt.plot(X, y, label=r"$f(x) = x \sin(x)$", linestyle="dotted")
plt.legend()
plt.xlabel("$x$")
plt.ylabel("$f(x)$")
_ = plt.title("True generative process")


training_indices = np.arange(tCur)
X_train, y_train = X[training_indices], y[training_indices, :]

kernel = 1 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
gaussian_process = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=9)
gaussian_process.fit(X_train, y_train)
gaussian_process.kernel_

mean_prediction, std_prediction = gaussian_process.predict(X, return_std=True)
plt.figure()
for feature in range(nFeatures):
    plt.plot(X, y[:, feature], label=r"$f(x) = x \sin(x)$", linestyle="dotted")
    plt.scatter(X_train, y_train[:, feature], label="Observations")
    plt.plot(X, mean_prediction[:, feature], label="Mean prediction")
    plt.fill_between(
        X.ravel(),
        mean_prediction[:, feature] - 1.96 * std_prediction[:, feature],
        mean_prediction[:, feature] + 1.96 * std_prediction[:, feature],
        alpha=0.5,
        label=r"95% confidence interval",
    )

plt.legend()
plt.xlabel("$x$")
plt.ylabel("$f(x)$")
_ = plt.title("Gaussian process regression on noise-free dataset")

noise_std = 0.6
y_train_noisy = y_train + rng.normal(loc=0.0, scale=noise_std, size=y_train.shape)

gaussian_process = GaussianProcessRegressor(
    kernel=kernel, alpha=noise_std**2, n_restarts_optimizer=9
)
gaussian_process.fit(X_train, y_train_noisy)
mean_prediction, std_prediction = gaussian_process.predict(X, return_std=True)
plt.figure(figsize = (8, 10))
for feature in range(nFeatures):
    plt.subplot(2, 2, feature+1)
    plt.plot(X, y[:, feature], label=r"$f(x) = x \sin(x)$", linestyle="dotted")
    plt.errorbar(
        X_train,
        y_train_noisy[:, feature],
        noise_std,
        linestyle="None",
        color="tab:blue",
        marker=".",
        markersize=5,
        label="Observations",
    )
    plt.plot(X, mean_prediction[:, feature], label="Mean prediction")
    plt.fill_between(
        X.ravel(),
        mean_prediction[:, feature] - 1.96 * std_prediction[:, feature],
        mean_prediction[:, feature] + 1.96 * std_prediction[:, feature],
        color="tab:orange",
        alpha=0.5,
        label=r"95% confidence interval",
    )
    # plt.legend()
    plt.xlabel("$x$")
    plt.ylabel("$f(x)$")
    plt.grid(True)
# _ = plt.title("Gaussian process regression on a noisy dataset")

