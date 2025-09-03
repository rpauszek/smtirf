import warnings

import numpy as np
from numba import jit

from .detail import ExitFlag
from .distributions import Dirichlet, DirichletArray, NormalGamma


def train_baumwelch(x, theta, maxIter=250, tol=1e-5, printWarnings=True):
    L = np.zeros(maxIter)
    isConverged = False
    for itr in range(maxIter):
        # E-step
        gamma, xi, lnZ = fwdback(theta.pi, theta.A, theta.p_X(x).T)
        L[itr] = lnZ
        # Check for convergence
        if itr > 1:
            deltaL = L[itr] - L[itr - 1]
            if deltaL < 0 and printWarnings:
                # todo: check stacklevel, pytest
                warnings.warn(
                    f"log likelihood decreasing by {np.abs(deltaL):0.4f}", stacklevel=1
                )
            if np.abs(deltaL) < tol:
                isConverged = True
                break
        # M-step
        theta.update(x, gamma, xi)

    return ExitFlag(L[: itr + 1], isConverged)


def train_variational(x, theta, maxIter=250, tol=1e-5, printWarnings=True):
    u, w = theta._u, theta._w
    L = np.zeros(maxIter)
    isConverged = False
    for itr in range(maxIter):
        # E-step
        gamma, xi, lnZ = fwdback(
            np.exp(w.lnPiStar), np.exp(w.lnAStar), np.exp(w.mahalanobis(x))
        )
        # Evaluate ELBO
        L[itr] = lnZ - kldiv(u, w)
        # Check for convergence
        if itr > 0:
            deltaL = L[itr] - L[itr - 1]
            if deltaL < 0 and printWarnings:
                # todo: check stacklevel, pytest
                warnings.warn(
                    f"lower bound decreasing by {np.abs(deltaL):0.4f}", stacklevel=1
                )
            if np.abs(deltaL) < tol:
                isConverged = True
                break
        # M-step
        theta.update(u, x, gamma, xi)

    # TODO: need to sort mu

    return ExitFlag(L[: itr + 1], isConverged)


@jit(nopython=True)
def fwdback(pi, A, B):
    T, K = B.shape
    alpha = np.zeros((T, K))
    beta = np.zeros((T, K))
    c = np.zeros(T)

    # forward loop
    alpha[0] = pi * B[0]
    c[0] = np.sum(alpha[0])
    alpha[0] = alpha[0] / c[0]
    for t in range(1, T):
        for k in range(K):
            alpha[t, k] = np.sum(alpha[t - 1] * A[:, k]) * B[t, k]
        c[t] = np.sum(alpha[t])
        alpha[t] = alpha[t] / c[t]

    # backward loop
    beta[-1] = 1
    for t in range(1, T):
        for k in range(K):
            beta[-(t + 1), k] = np.sum(A[k] * B[-t] * beta[-t]) / c[-t]

    # state probabilities
    gamma = alpha * beta
    # transition probabilities
    xi = np.zeros((T - 1, K, K))
    for t in range(T - 1):
        for i in range(K):
            for j in range(K):
                xi[t, i, j] = (
                    alpha[t, i] * A[i, j] * B[t + 1, j] * beta[t + 1, j] / c[t + 1]
                )
    xi = np.sum(xi, axis=0)  # sum over time
    L = np.sum(np.log(c))  # log(likelihood) !!! usual BaumWelch minimizes -log(L)

    return gamma, xi, L


@jit(nopython=True)
def _viterbi(x, pi, A, B):
    # setup
    T, K = B.shape
    pi = np.log(pi)
    A = np.log(A)
    B = np.log(B)
    psi = np.zeros(B.shape, dtype=np.int32)
    Q = np.zeros(T, dtype=np.int32)

    # initialization
    delta = np.expand_dims(pi + B[0], 1)
    # recursion
    for t in range(1, T):
        R = delta + A
        for k in range(K):
            psi[t, k] = np.argmax(R[:, k])
            delta[k] = np.max(R[:, k]) + B[t, k]

    # termination
    # todo: check if this is still needed
    # psiStar = np.max(delta)
    Q[-1] = np.argmax(delta)
    # path backtracking
    for t in range(1, T):
        Q[-(t + 1)] = psi[-t, Q[-t]]

    return Q


def kldiv(u, w):
    DKL = Dirichlet.kldiv(u._rho, w._rho)
    DKL += DirichletArray.kldiv(u._alpha, w._alpha)
    DKL += NormalGamma.kldiv(u._phi, w._phi)
    return DKL


@jit(nopython=True)
def sample_statepath(K, pi, A, T):
    S = np.zeros(T, dtype=np.uint32)
    S[0] = catrnd(pi)
    for t in range(1, T):
        S[t] = catrnd(A[S[t - 1]])
    return S


@jit(nopython=True)
def catrnd(p):
    """from Presse iHMM beam sampler"""
    K = p.size
    p = np.cumsum(p)
    for k in range(K):
        if np.random.uniform(0, p[-1]) < p[k]:
            break
    return k
