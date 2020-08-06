# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> hmm >> algorithms
"""
import numpy as np
from scipy.special import gammaln, digamma
from numba import jit
import warnings
from smtirf.stats import row, col

# ==============================================================================
# forward-backward algorithm
# ==============================================================================
@jit(nopython=True)
def fwdback(pi, A, B):
    T, K = B.shape
    alpha = np.zeros((T,K))
    beta = np.zeros((T,K))
    c = np.zeros(T)

    # forward loop
    alpha[0] = pi*B[0]
    c[0] = np.sum(alpha[0])
    alpha[0] = alpha[0]/c[0]
    for t in range(1, T):
        for k in range(K):
            alpha[t,k] = np.sum(alpha[t-1]*A[:,k]) * B[t,k]
        c[t] = np.sum(alpha[t])
        alpha[t] = alpha[t]/c[t]

    # backward loop
    beta[-1] = 1
    for t in range(1, T):
        for k in range(K):
            beta[-(t+1),k] = np.sum(A[k]*B[-t]*beta[-t])/c[-t]

    # state probabilities
    gamma = alpha*beta
    # transition probabilities
    xi = np.zeros((T-1,K,K))
    for t in range(T-1):
        for i in range(K):
            for j in range(K):
                xi[t,i,j] = alpha[t,i] * A[i,j] * B[t+1,j] * beta[t+1,j] / c[t+1]
    xi = np.sum(xi, axis=0) # sum over time
    L = np.sum(np.log(c)) # log(likelihood) !!! usual BaumWelch minimizes -log(L)

    return gamma, xi, L

# ==============================================================================
# Viterbi algorithm
# ==============================================================================
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
            psi[t,k] = np.argmax(R[:,k])
            delta[k] = np.max(R[:,k]) + B[t,k]

    # termination
    psiStar = np.max(delta)
    Q[-1] = np.argmax(delta)
    # path backtracking
    for t in range(1, T):
        Q[-(t+1)] = psi[-t, Q[-t]]

    return Q    
