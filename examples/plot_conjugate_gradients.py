"""
Simulation study for conjugate gradients
========================================

We conduct in the following a simulation study illustrating the conjugate gradients algorithm.
"""

import random
import time
import numpy as np
from scipy.sparse import dia_matrix
import matplotlib.pyplot as plt
import EarlyStopping as es

random.seed(42)

# %%
# Simulation Setting
# ------------------
# To make our results comparable, we use the same simulation setting as `Blanchard et al. (2018) <https://doi.org/10.1137/17M1154096>`_ and `Stankewitz (2020) <https://doi.org/10.1214/20-EJS1747>`_.

# Set parameters
SAMPLE_SIZE = 10000
PARAMETER_SIZE = SAMPLE_SIZE
MAXIMAL_ITERATION = SAMPLE_SIZE
NOISE_LEVEL = 0.01
CRITICAL_VALUE = SAMPLE_SIZE * (NOISE_LEVEL**2)

# Create diagonal design matrices
indices = np.arange(SAMPLE_SIZE) + 1
design_matrix = dia_matrix(np.diag(1 / (np.sqrt(indices))))

# Create signals
signal_supersmooth = 5 * np.exp(-0.1 * indices)
signal_smooth = 5000 * np.abs(np.sin(0.01 * indices)) * indices ** (-1.6)
signal_rough = 250 * np.abs(np.sin(0.002 * indices)) * indices ** (-0.8)

# %%
# We plot the SVD coefficients of the three signals.

plt.plot(indices, signal_supersmooth, label="supersmooth signal")
plt.plot(indices, signal_smooth, label="smooth signal")
plt.plot(indices, signal_rough, label="rough signal")
plt.ylabel("Signal")
plt.xlabel("Index")
plt.ylim([-0.05, 1.6])
plt.legend()
plt.show()

# %%
# Monte Carlo Study
# -----------------
# We simulate NUMBER_RUNS realisations of the Gaussian sequence space model.

# Specify number of Monte Carlo runs
NUMBER_RUNS = 1  # set to 1000 for final simulations

# Create observations for the three different signals
noise = np.random.normal(0, NOISE_LEVEL, (SAMPLE_SIZE, NUMBER_RUNS))
observation_supersmooth = noise + (design_matrix @ signal_supersmooth)[:, None]
observation_smooth = noise + (design_matrix @ signal_smooth)[:, None]
observation_rough = noise + (design_matrix @ signal_rough)[:, None]

# %%
# We choose to interpolate linearly between the conjugate gradient estimates at integer iteration indices and create the models.

# Set interpolation boolean
INTERPOLATION_BOOLEAN = True

# Create models
models_supersmooth = [
    es.ConjugateGradients(
        design_matrix,
        observation_supersmooth[:, i],
        true_signal=signal_supersmooth,
        true_noise_level=NOISE_LEVEL,
        interpolation=INTERPOLATION_BOOLEAN,
    )
    for i in range(NUMBER_RUNS)
]
models_smooth = [
    es.ConjugateGradients(
        design_matrix,
        observation_smooth[:, i],
        true_signal=signal_smooth,
        true_noise_level=NOISE_LEVEL,
        interpolation=INTERPOLATION_BOOLEAN,
    )
    for i in range(NUMBER_RUNS)
]
models_rough = [
    es.ConjugateGradients(
        design_matrix,
        observation_rough[:, i],
        true_signal=signal_rough,
        true_noise_level=NOISE_LEVEL,
        interpolation=INTERPOLATION_BOOLEAN,
    )
    for i in range(NUMBER_RUNS)
]

# %%
# We calculate the early stopping index, the conjugate gradient estimate at the early stopping index and the squared residual norms along the whole iteration path (until MAXIMAL_ITERATION) for the three signals.

for run in range(NUMBER_RUNS):
    start_time = time.time()
    models_supersmooth[run].conjugate_gradients_gather_all(MAXIMAL_ITERATION)
    models_smooth[run].conjugate_gradients_gather_all(MAXIMAL_ITERATION)
    models_rough[run].conjugate_gradients_gather_all(MAXIMAL_ITERATION)
    end_time = time.time()
    print(f"The {run}-th Monte Carlo step took {end_time - start_time} seconds.")
    print(f"Supersmooth early stopping index: {models_supersmooth[run].early_stopping_index}")
    print(f"Smooth early stopping index: {models_smooth[run].early_stopping_index}")
    print(f"Rough early stopping index: {models_rough[run].early_stopping_index}")

# %%
# Plot of squared residual norms and empirical error terms
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# We plot for the first Monte Carlo run the squared residual norms along the whole iteration path and the corresponding weak and strong empirical error terms,
# i.e. the empirical prediction and reconstruction errors, for the three different signals. If we chose to interpolate, i.e. INTERPOLSTION_BOOLEAN is set to
# true, we need to interpolate between the squared residual norms at the integer iteration indices.


# Calculate interpolated squared residual norm for a given vector containing the squared
# residual norms at integer iteration indices and a possibliy non-integer index
def calculate_interpolated_residual(residuals, index):
    index_ceil = int(np.ceil(index))
    index_floor = int(np.floor(index))
    alpha = index - index_floor
    interpolated_residual = (1 - alpha) ** 2 * residuals[index_floor] + (1 - (1 - alpha) ** 2) * residuals[index_ceil]
    return interpolated_residual


# Vectorize interpolating function
calculate_interpolated_residual = np.vectorize(calculate_interpolated_residual, excluded=["residuals"])

# Set gridsize for the x-axis of the plots
GRIDSIZE = 0.01

# Calculate interpolated squared residual norms
if INTERPOLATION_BOOLEAN:
    grid = np.arange(0, MAXIMAL_ITERATION + GRIDSIZE, GRIDSIZE)
    residuals_supersmooth = calculate_interpolated_residual(residuals=models_supersmooth[0].residuals, index=grid)
else:
    grid = np.arange(0, MAXIMAL_ITERATION + 1)
    residuals_supersmooth = models_supersmooth[0].residuals

# Plot
plt.plot(grid, residuals_supersmooth, label="squared residual norm", color="green")
plt.axvline(x=models_supersmooth[0].early_stopping_index, color="grey", linestyle="--")
plt.axhline(y=models_supersmooth[0].critical_value, color="grey", linestyle="--")
plt.xlim([0, 12])
plt.ylim([0, 11])
plt.xlabel("Iteration index")
plt.xticks(list(plt.xticks()[0]) + [models_supersmooth[0].early_stopping_index], list(plt.xticks()[1]) + ["$\\tau$"])
plt.yticks(
    list(plt.yticks()[0]) + [models_supersmooth[0].critical_value], list(plt.yticks()[1]) + ["$\\kappa = D \\delta^2$"]
)
plt.legend()
plt.show()
