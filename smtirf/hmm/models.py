import numpy as np
from dataclasses import dataclass, field
from . import col, ExitFlag
from .distributions import Categorical, Normal
from .algorithms import fwdback, viterbi
from ..util import AsDictMixin


@dataclass(frozen=True)
class HiddenMarkovModel(AsDictMixin):

    K: int
    pi: Categorical
    A: Categorical
    phi: Normal
    exit_flag: ExitFlag = field(default_factory=ExitFlag)

    @classmethod
    def guess(cls, x, K, shared_variance=False):
        pi = Categorical.initialize_vector(K)
        A = Categorical.initalize_array(K, self_transition=10)
        phi = Normal.initialize_kmeans(K, x, shared_variance)
        return cls(K, pi, A, phi)

    @staticmethod
    def _expectation_step(pi, A, pdf, observations):
        """Evaluate the Expectation Step of the Baul-Welch algorithm on a set of observations.

        Parameters
        ----------
        pi : np.ndarray
            Initial state probabilities.
        A : np.ndarray
            State transition probability matrix.
        pdf : callable
            Probability Distribution Function for the emission model.
        observations : list
            List of observation arrays.
        """
        results = [fwdback(pi, A, pdf(x).T) for x in observations]
        gammas = [r[0] for r in results]
        xis = [r[1] for r in results]
        log_likelihoods = [r[2] for r in results]
        return gammas, xis, log_likelihoods

    def train(self, *observations, max_iter=250, tol=1e-5):
        """Train the model using the Baul-Welch algorithm.

        Parameters
        ----------
        observations
            Variable length set of observation arrays.
        max_iter : int
            Maximum number of iterations.
        tol : float
            Convergence tolerance.
        """
        gammas, xis, log_likelihoods = HiddenMarkovModel._expectation_step(
            self.pi.mu, self.A.mu, self.phi.pdf, observations
        )
        theta = HiddenMarkovModel(
            self.K, self.pi, self.A, self.phi, ExitFlag(np.sum(log_likelihoods))
        )

        for _ in range(max_iter):
            theta, gammas, xis, log_likelihoods = theta._update(
                observations, gammas, xis, tol=tol
            )
            if theta.exit_flag.is_converged:
                break

        return theta

    def _update(self, observations, gammas, xis, tol=1e-5):
        """Update the model from previous E-step.

        Parameters
        ----------
        observations : list
            List of observation arrays.
        gammas : list
            List of gamma parameter arrays; calculated from forward-backward algorithm.
        xis : list
            List of xi parameter arrays; calculated from forward-backward algorithm.
        tol : floag
            Convergence tolerance.
        """

        gamma0 = np.vstack([gamma[0] for gamma in gammas]).sum(axis=0) / len(gammas)
        xi_sum = np.stack(xis, axis=2).sum(axis=2)
        gamma_sum = np.vstack([gamma[:-1].sum(axis=0) for gamma in gammas]).sum(axis=0)

        # M-Step
        pi = self.pi.update(gamma0)
        A = self.A.update(xi_sum / col(gamma_sum))
        phi = self.phi.update(np.hstack(observations), np.vstack(gammas))

        # E-Step
        gammas, xis, log_likelihoods = HiddenMarkovModel._expectation_step(
            pi.mu, A.mu, phi.pdf, observations
        )

        exit_flag = self.exit_flag.step(np.sum(log_likelihoods), tol=tol)
        theta = HiddenMarkovModel(self.K, pi, A, phi, exit_flag)

        return (theta, gammas, xis, log_likelihoods)

    def label(self, x):
        return viterbi(self.pi.mu, self.A.mu, self.phi.pdf(x).T).astype(int)


def _construct_from_old_version(model):
    """Construct a HiddenMarkovModel from old JSON format, <v0.2.0"""

    if model["modelType"] != "em":
        raise NotImplementedError(
            "Only Classic (Expectation-Maximization) models are supported currently."
        )

    K = int(model["K"])
    pi = Categorical(K, np.array(model["pi"]))
    A = Categorical(K, np.array(model["A"]))
    phi = Normal(K, np.array(model["mu"]), np.array(model["tau"]))

    flag = ExitFlag(
        model["exitFlag"]["L"][-1],
        model["exitFlag"]["L"][-1] - model["exitFlag"]["L"][-2],
        len(model["exitFlag"]["L"]),
        model["exitFlag"]["isConverged"],
    )

    return HiddenMarkovModel(K, pi, A, phi, flag)
