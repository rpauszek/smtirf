import warnings

import numpy as np
from sklearn import mixture

from smtirf.hmm.detail import col, normalize_rows, row


class AutoBaselineModel:
    """3-state Hidden Markov Model to estimate signal blinks and bleach
    => Emission parameters are estimated by a fixed GMM trained on a random sample of data
    => GMM components are split into "signal" or "blink/bleach" groups dependent on baselineCutoff
    => HMM is trained with fixed emission parameters from GMM using a batch
       version of the Viterbi algorithm
    """

    def __init__(self, expt, baselineCutoff=100):
        self.expt = expt
        self.X = np.vstack([trc.I0 for trc in self.expt])
        self.SP = None

        self.baselineCutoff = baselineCutoff

        self.pi = normalize_rows([10, 1, 0])
        self.Q = 3
        self.A = normalize_rows(
            [[99, 2, 5], [50, 50, 0], [0, 0, 1]]  # signal  # blink
        )  # bleach
        self.phi, self.mu, self.var = None, None, None

    def train_gmm(self, nComponents=5, nPoints=1e4):
        X = np.random.choice(self.X.ravel(), size=int(nPoints), replace=False)
        gmm = mixture.BayesianGaussianMixture(
            n_components=nComponents, covariance_type="full"
        ).fit(col(X))
        phi = gmm.weights_.squeeze()
        mu = gmm.means_.squeeze()
        var = gmm.covariances_.squeeze()
        # sort
        ix = mu.argsort()
        self.phi = phi[ix]
        self.mu = mu[ix]
        self.var = var[ix]

    def draw_gmm_samples(self, nDraws=5, nPoints=1e4):
        return [
            np.random.choice(self.X.ravel(), size=int(nPoints), replace=False)
            for n in range(nDraws)
        ]

    def gmm_p_X(self, X):
        X = row(X) - col(self.mu)
        tau = 1 / self.var
        lnP = -0.5 * np.log(2 * np.pi / col(tau)) - col(tau) / 2 * X**2
        return col(self.phi) * np.exp(lnP)

    def _calc_emission_prob(self):
        isSignal = self.mu > self.baselineCutoff

        # re-normalize weights
        phi = self.phi.copy()
        phi[isSignal] = self.phi[isSignal] / np.sum(self.phi[isSignal])
        phi[~isSignal] = self.phi[~isSignal] / np.sum(self.phi[~isSignal])

        # calculate nComponent (K) emission probabilities
        Y = self.X.T[np.newaxis, :, :]  # 1 x T x M
        p_X = np.sqrt(2 * np.pi * hcol(self.var)) ** -1 * np.exp(
            -0.5 * (Y - hcol(self.mu)) ** 2 / hcol(self.var)
        )  # K x T x M

        # calculate 3-state emission probabilities
        pBaseline = p_X[~isSignal, :, :].sum(axis=0)
        pSignal = p_X[isSignal, :, :].sum(axis=0)
        return np.stack((pSignal, pBaseline, pBaseline), axis=0)  # Q=3 x T x M

    def train_hmm(self, maxIter=50, tol=1e-3, printWarnings=False):
        M, T = self.X.shape
        p_X = self._calc_emission_prob()

        L = np.zeros(maxIter)
        # isConverged = False
        for itr in range(maxIter):
            # E-step
            sp, Li = viterbi_batch(self.pi, self.A, p_X)  # sp = M x T
            # Check for convergence
            L[itr] = Li
            if itr > 1:
                deltaL = L[itr] - L[itr - 1]
                if deltaL < 0 and printWarnings:
                    # todo: check stacklevel, pytest
                    warnings.warn(
                        f"log likelihood decreasing by {np.abs(deltaL):0.4f}",
                        stacklevel=1,
                    )
                if np.abs(deltaL) < tol:
                    # isConverged = True
                    break
            # M-step
            self.pi = np.array([np.sum(sp[:, 0] == i) for i in range(self.Q)]) / M
            self.A = np.zeros((self.Q, self.Q))
            for i in range(self.Q):
                for j in range(self.Q):
                    self.A[i, j] = np.sum(
                        np.logical_and(sp[:, :-1] == i, sp[:, 1:] == j)
                    ) / np.sum(sp[:, :-1] == i)

        self.SP = sp


def hcol(x):
    return x[:, np.newaxis, np.newaxis]


def viterbi_batch(pi, A, p_X):
    """Viterbi algorithm calculated on M traces simultaneously
    traces must all be the same length
    pi  -> [K, ]
    A   -> [K x K]
    p_X -> [K x T x M]
    """
    K, T, M = p_X.shape
    Psi = np.zeros((K, T, M)).astype(int)
    with np.errstate(divide="ignore"):
        pi = np.log(pi)
        A = np.log(A)
        B = np.log(p_X)  # [KxTxM]
    # broadcast into appropriate shapes
    pi = np.repeat(pi[:, np.newaxis], M, axis=1)  # [KxM]
    A = np.repeat(A[:, :, np.newaxis], M, axis=2)  # [KxKxM]
    # initialization
    delta = pi + B[:, 0, :]  # K x M
    # delta needs to be broadcast along axis=2
    delta = delta[:, np.newaxis, :]  # K x 1 x M
    # recursion
    for t in range(1, T):
        delta = delta + A  # K x K x M
        ix = np.argmax(delta, axis=0)  # K x M
        Psi[:, t, :] = ix
        delta = np.max(delta, axis=0) + B[:, t, :]  # K x M
        delta = delta[:, np.newaxis, :]  # K x 1 x M
    # termination
    Q = np.zeros((M, T)).astype(int)
    L = np.max(delta.squeeze(), axis=0)  # M,
    Q[:, -1] = np.argmax(delta.squeeze(), axis=0)  # M,
    # path backtracking
    for t in range(2, T + 1):
        Psi_tplus1 = Psi[:, -t + 1, :]  # K x M
        Q_tplus1 = Q[:, -t + 1]  # M,
        Q[:, -t] = Psi_tplus1[Q_tplus1, np.arange(M)]  # M,
    return Q, L.sum()
