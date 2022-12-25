import numpy as np
from dataclasses import dataclass


def row(x):
    x = np.atleast_1d(x)
    assert x.ndim == 1, "Cannot form a row vector from a 2D array."
    return x[np.newaxis, :]


def col(x):
    x = np.atleast_1d(x)
    assert x.ndim == 1, "Cannot form a column vector from a 2D array."
    return x[:, np.newaxis]


@dataclass(frozen=True)
class ExitFlag:
    log_likelihood: float = -np.inf
    delta_log_likelihood: float = np.nan
    iterations: int = 0
    is_converged: bool = False

    def __str__(self):
        return (
            f"\nTraining Summary:\n"
            f"  {'log(L)': <13}" + f"{self.log_likelihood:0.6f}\n"
            f"  {'Δ log(L)': <13}" + f"{self.delta_log_likelihood:0.2e}\n"
            f"  {'Iterations': <13}" + f"{self.iterations}\n"
            f"  {'Converged': <13}" + f"{self.is_converged}\n"
        )

    def step(self, new_log_likelihood, tol):
        delta_ln_Z = new_log_likelihood - self.log_likelihood
        is_converged = delta_ln_Z < tol
        iterations = self.iterations + 1
        return ExitFlag(new_log_likelihood, delta_ln_Z, iterations, is_converged)
