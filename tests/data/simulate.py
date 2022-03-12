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


def simulate_fret_emission_path(
    statepath, mu, total_intensity, channel_sigma, lifetime_frames=None
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
    channel_sigma : float
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

    acceptor = np.random.normal(loc=acceptor_statepath, scale=channel_sigma)
    donor = np.random.normal(loc=donor_statepath, scale=channel_sigma)
    fret = acceptor / (acceptor + donor)

    return fret, donor, acceptor, bleach_statepath


def sample_spot_locations(frame_size, border, N):
    """Sample spot locations from uniform distribution, excluding border around each channel.

    Channel images are aligned, translation/rotation not applied.

    Parameters
    ----------
    frame_size : int
        number of pixels along an edge of the full two-channel image
    border : int
        number of border pixels around each channel to exclude from sampling range
    N : int
        number of spots
    """
    channel_width = frame_size / 2
    channel_height = frame_size

    channel1_x = np.random.uniform(border, channel_width - border, size=N)
    channel2_x = channel1_x + channel_width
    channels_y = np.random.uniform(border, channel_height - border, size=N)

    pks = []
    for x1, x2, y in zip(channel1_x, channel2_x, channels_y):
        pks.append(((x1, y), (x2, y)))
    return pks


def make_image(traces, pks, frame_size):
    """Generate image, spots as 2D gaussian

    2D normal distribution is calculate for each spot location and then
    multiplied by the mean signal in the first 10 frames of each channel
    for that spot.

    Parameters
    ----------
    traces : list
        list of (donor, acceptor) trace pairs
    pks : list
        list of ((donor-x, donor-y), (acceptor-x, acceptor-y)) coordinates
    frame_size : int
        number of pixels along an edge of the full two-channel image
    """

    def normal_2d(x, y, mu, sigma):
        diff = np.vstack((x, y)) - mu[:, np.newaxis]
        quad_form = np.sum(np.dot(diff.T, np.linalg.inv(sigma)) * diff.T, axis=1)
        return np.exp(-0.5 * quad_form) / np.sqrt(2 * np.pi * np.linalg.det(sigma))

    frame_shape = (frame_size, frame_size)
    sigma = np.eye(2) * 2
    X, Y = np.meshgrid(np.arange(0, frame_size), np.arange(0, frame_size))
    X, Y = X.ravel(), Y.ravel()
    image = np.zeros(frame_shape)

    for trace, peak in zip(traces, pks):
        trace = np.vstack(trace)
        amplitudes = np.mean(trace[:, :10], axis=1)

        for coord, amplitude in zip(peak, amplitudes):
            spot = normal_2d(X, Y, np.array(coord), sigma) * amplitude
            image += spot.reshape(frame_shape)

    image = np.clip(image, 0, 255)
    return image.astype(np.uint8)


def simulate_fret_experiment(
    K,
    n_frames,
    n_spots,
    *,
    pi=None,
    A=None,
    mu=None,
    transition_diag=10,
    frame_length=0.100,
    signal_lifetime=80,
    total_intensity=500,
    channel_sigma=30,
    frame_size=512,
    channel_border=20,
):
    """Generate traces for a FRET experiment.

    Parameters
    ----------
    K : int
        number of states
    n_frames : int
        number of frames in the movie
    n_spots : int
        number of spots in the field of view
    pi : np.array
        initial state probability vector; defaults to uniform probability
    A : np.array
        K x K array of state transitions probabilities;
        defaults to symmetric matrix controlled by `transition_diag`
    mu : np.array
        state emission vector; defaults to equally spaced between [0, 1]
    transition_diag : float
        elements along the diagonal of the transition probablity matrix
        if none is supplied. Off-diagonal elements are set to 1 and matrix
        is then normalized.
    frame_length : float
        frame integration time in seconds
    signal_lifetime : float
        exponential mean of fluorophore lifetime; controls bleaching time
    total_intensity : float
        intensity of donor + acceptor signals
    channel_sigma : float
        standard deviation of the signal in donor/acceptor channels
    frame_size : int
        number of pixels along an edge of the full two-channel image
    channel_border : int
        number of border pixels around each channel to exclude from sampling range
    """

    if pi is None:
        pi = np.ones(K) / K

    if A is None:
        A = (np.eye(K) * transition_diag) + np.ones((K, K))
        A = A / A.sum(axis=1)[:, np.newaxis]

    if mu is None:
        mu = np.linspace(0, 1, K)

    assert pi.shape == (K,)
    assert A.shape == (K, K)
    assert mu.shape == (K,)

    signal_lifetime_frames = signal_lifetime / frame_length

    statepaths, traces = [], []
    for _ in range(n_spots):
        statepaths.append(simulate_statepath(K, pi, A, n_frames))
        _, *trace, _ = simulate_fret_emission_path(
            statepaths[-1], mu, total_intensity, channel_sigma, signal_lifetime_frames
        )
        traces.append(trace)

    peaks = sample_spot_locations(frame_size, channel_border, n_spots)
    image = make_image(traces, peaks, frame_size)

    return statepaths, traces, peaks, image


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    sp, traces, pks, img = simulate_fret_experiment(3, 500, 5)

    donor, acceptor = traces[0]
    total = donor + acceptor
    fret = acceptor / total
    t = np.arange(fret.size) * 0.1

    plt.subplot(3, 1, 1)
    plt.plot(t, acceptor, c="tab:orange")
    plt.plot(t, donor, c="tab:green")
    plt.subplot(3, 1, 2)
    plt.plot(t, fret, c="tab:blue")
    plt.ylim(-0.1, 1.1)
    plt.subplot(3, 1, 3)
    plt.plot(t, total, c="k")

    plt.gcf().set_size_inches(10, 6)
    plt.tight_layout()
    plt.show()


    plt.imshow(img)
    plt.show()
