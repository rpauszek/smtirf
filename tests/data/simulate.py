import numpy as np


def simulate_statepath(K, pi, A, T):
    """Sample statepath from HMM.

    Parameters
    ----------
    K : int
        number of states
    pi : np.ndarray
        initial state probabilities
    A : np.ndarray
        K x K transition probability matrix
    T : int
        number of time points in trace
    """
    assert K == pi.size
    assert A.shape == (K, K)

    # initialization
    statepath = np.zeros(T, dtype=np.uint8)
    statepath[0] = np.random.choice(K, 1, replace=False, p=pi).squeeze()

    # induction
    for t in range(1, T):
        statepath[t] = np.random.choice(
            K, 1, replace=False, p=A[statepath[t - 1]]
        ).squeeze()

    return statepath


def simulate_fret_experiment(
    statepath, mu, total_intensity, sigma_channel, lifetime_frames=None
):
    """Simulate FRET, donor, and acceptor traces from statepath.

    Parameters
    ----------
    statepath : np.ndarray
        vector of states; int ∈ K
    mu : np.ndarray
        array of FRET states
    total_intensity : float
        total signal intensity; sum of donor and acceptor
    sigma_channel : float
        noise in donor/acceptor signal
    lifetime_frames : float
        mean lifetime (in frames) of the fluorophore;
        tau parameter in exponential distribution
    """

    fret_statepath = mu[statepath]
    acceptor_statepath = fret_statepath * total_intensity
    donor_statepath = total_intensity - acceptor_statepath

    if lifetime_frames is not None:
        bleach_index = np.rint(
            np.random.exponential(lifetime_frames, size=1).squeeze()
        ).astype(int)

        bleach_statepath = np.zeros(statepath.shape)
        bleach_statepath[bleach_index:] = 1

        acceptor_statepath[bleach_index:] = 0
        donor_statepath[bleach_index:] = 0
    else:
        bleach_statepath = np.zeros(statepath.shape)

    acceptor = np.random.normal(loc=acceptor_statepath, scale=sigma_channel)
    donor = np.random.normal(loc=donor_statepath, scale=sigma_channel)
    fret = acceptor / (acceptor + donor)

    return fret, donor, acceptor, bleach_statepath


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    K = 3
    pi = np.ones(K) / K
    A = (np.eye(K) * 10) + np.ones((K, K))
    A = A / A.sum(axis=1)[:, np.newaxis]
    sp = simulate_statepath(K, pi, A, 1000)

    frame_time_sec = 0.100
    bleach_lifetime = 80
    bleach_lifetime_frames = bleach_lifetime / frame_time_sec

    E, D, A, _ = simulate_fret_experiment(
        sp, np.linspace(0, 1, K), 300, 30, bleach_lifetime_frames
    )
    t = np.arange(E.size) * frame_time_sec

    plt.subplot(3, 1, 1)
    plt.plot(t, A, c="tab:orange")
    plt.plot(t, D, c="tab:green")
    plt.subplot(3, 1, 2)
    plt.plot(t, E, c="tab:blue")
    plt.ylim(-0.1, 1.1)
    plt.subplot(3, 1, 3)
    plt.plot(t, D + A, c="k")

    plt.gcf().set_size_inches(10, 6)
    plt.tight_layout()
    plt.show()
