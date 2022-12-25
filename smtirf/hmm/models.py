import numpy as np
from dataclasses import dataclass, field
import warnings
from . import col, ExitFlag
from .distributions import Categorical, Normal
from .algorithms import fwdback


@dataclass(frozen=True)
class HiddenMarkovModel:

    K: int
    pi: Categorical
    A: Categorical
    phi: Normal
    exit_flag: ExitFlag = field(default_factory=ExitFlag.empty)

    @classmethod
    def guess(cls, K, x):
        pi = Categorical.initialize_vector(K)
        A = Categorical.initalize_array(K, self_transition=10)
        phi = Normal.initialize_kmeans(K, x)
        return cls(K, pi, A, phi)

    def train(self, x, max_iter=250, tol=1e-5):
        log_likelihoods = np.zeros(max_iter)
        is_converged = False
        theta = self

        for itr in range(max_iter):
            # E-Step
            gamma, xi, ln_Z = fwdback(theta.pi.mu, theta.A.mu, theta.phi.pdf(x).T)
            log_likelihoods[itr] = ln_Z

            # check for convergence
            if itr > 0:
                delta_L = log_likelihoods[itr] - log_likelihoods[itr - 1]

                if delta_L < 0:
                    warnings.warn(f"log likelihood decreased by {np.abs(delta_L):0.4f}")
                if np.abs(delta_L) < tol:
                    is_converged = True
                    break

            # M-Step
            theta = theta.update(
                x, gamma, xi, ExitFlag(log_likelihoods[: itr + 1], is_converged)
            )

        exit_flag = ExitFlag(log_likelihoods[: itr + 1], is_converged)
        return HiddenMarkovModel(theta.K, theta.pi, theta.A, theta.phi, exit_flag)

    def update(self, x, gamma, xi, exit_flag=None):
        pi = self.pi.update(gamma[0])
        A = self.A.update(xi / col(gamma[:-1].sum(axis=0)))
        phi = self.phi.update(x, gamma)

        return HiddenMarkovModel(
            self.K, pi, A, phi, exit_flag if exit_flag else ExitFlag.empty()
        )
