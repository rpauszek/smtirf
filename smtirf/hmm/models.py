from dataclasses import dataclass, field
from . import col, ExitFlag
from .distributions import Categorical, Normal
from .algorithms import fwdback


@dataclass(frozen=True)
class HiddenMarkovModel:

    K: int
    pi: Categorical
    A: Categorical
    phi: Normal
    exit_flag: ExitFlag = field(default_factory=ExitFlag)

    @classmethod
    def guess(cls, K, x):
        pi = Categorical.initialize_vector(K)
        A = Categorical.initalize_array(K, self_transition=10)
        phi = Normal.initialize_kmeans(K, x)
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
