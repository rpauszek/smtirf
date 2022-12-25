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


@dataclass
class ExitFlag:
    log_likelihoods: np.ndarray
    is_converged: bool

    @classmethod
    def empty(cls):
        return cls(np.array([]), False)

    @property
    def max_log_likelihood(self):
        return self.log_likelihoods[-1] if self.iterations else np.nan

    @property
    def delta_log_likelihood(self):
        return (
            self.log_likelihoods[-1] - self.log_likelihoods[-2]
            if self.iterations
            else np.nan
        )

    @property
    def iterations(self):
        return self.log_likelihoods.size

    def __str__(self):
        return (
            f"\nTraining Summary:\n"
            f"  {'log(L)': <13}" + f"{self.max_log_likelihood:0.4g}\n"
            f"  {'Δ log(L)': <13}" + f"{self.delta_log_likelihood:0.2e}\n"
            f"  {'Iterations': <13}" + f"{self.iterations}\n"
            f"  {'Converged': <13}" + f"{self.is_converged}\n"
        )
