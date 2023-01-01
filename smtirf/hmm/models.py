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

    def train(self, x, max_iter=250, tol=1e-5):
        gamma, xi, ln_Z = fwdback(self.pi.mu, self.A.mu, self.phi.pdf(x).T)
        theta = HiddenMarkovModel(self.K, self.pi, self.A, self.phi, ExitFlag(ln_Z))

        for _ in range(max_iter):
            theta, gamma, xi, ln_Z = theta._update(x, gamma, xi, tol=tol)
            if theta.exit_flag.is_converged:
                break

        return theta

    def _update(self, x, gamma, xi, tol=1e-5):
        # M-Step
        pi = self.pi.update(gamma[0])
        A = self.A.update(xi / col(gamma[:-1].sum(axis=0)))
        phi = self.phi.update(x, gamma)

        # E-Step
        gamma, xi, ln_Z = fwdback(pi.mu, A.mu, phi.pdf(x).T)
        return (
            HiddenMarkovModel(self.K, pi, A, phi, self.exit_flag.step(ln_Z, tol=tol)),
            gamma,
            xi,
            ln_Z,
        )

    def label(self, x):
        return viterbi(self.pi.mu, self.A.mu, self.phi.pdf(x).T).astype(int)


def _construct_from_old_version(model):
    """Construct a HiddenMarkovModel from old JSON format, <v0.2.0"""

    if model["modelType"] != "em":
        raise NotImplementedError("Only Classic (Expectation-Maximization) models are supported currently.")

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
