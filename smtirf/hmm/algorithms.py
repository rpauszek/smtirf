import numpy as np
from numba import jit


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

    #! log(L); usual BaumWelch minimizes -log(L)
    log_likelihood = np.sum(np.log(c))

    return gamma, xi, log_likelihood
