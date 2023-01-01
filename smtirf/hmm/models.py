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

    def train(self, *observations, max_iter=250, tol=1e-5):

        results = [fwdback(self.pi.mu, self.A.mu, self.phi.pdf(x).T) for x in observations]

        gammas = [r[0] for r in results]
        xis = [r[1] for r in results]
        Ls = [r[2] for r in results]

        theta = HiddenMarkovModel(self.K, self.pi, self.A, self.phi, ExitFlag(np.sum(Ls)))
        print("***", theta.exit_flag)

        for itr in range(max_iter):
            theta, gammas, xis, Ls = theta._update(observations, gammas, xis, tol=tol)
            print(itr)
            print(theta.exit_flag)
            if theta.exit_flag.is_converged:
                break

        return theta

    def _update(self, observations, gammas, xis, tol=1e-5):
        # observations : list

        gamma0 = np.vstack([gamma[0] for gamma in gammas]).sum(axis=0) / len(gammas)
        xi_sum = np.stack(xis, axis=2).sum(axis=2)
        gamma_sum = np.vstack([gamma[:-1].sum(axis=0) for gamma in gammas]).sum(axis=0)

        # M-Step
        pi = self.pi.update(gamma0)
        A = self.A.update(xi_sum / col(gamma_sum))
        phi = self.phi.update(np.hstack(observations), np.vstack(gammas))

        # E-Step
        results = [fwdback(pi.mu, A.mu, phi.pdf(x).T) for x in observations]

        gammas = [r[0] for r in results]
        xis = [r[1] for r in results]
        Ls = [r[2] for r in results]

        return (
            HiddenMarkovModel(self.K, pi, A, phi, self.exit_flag.step(np.sum(Ls), tol=tol)),
            gammas,
            xis,
            Ls,
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
