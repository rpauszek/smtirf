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


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    np.random.seed(1234)

    T = 1000
    N = 5

    K = 3
    pi = np.array([1, 0, 0])
    A = (np.eye(K) * 10) + np.ones((K, K))
    A = A / A.sum(axis=1)[:, np.newaxis]

    frame_time_sec = 0.100
    bleach_lifetime = 80
    bleach_lifetime_frames = bleach_lifetime / frame_time_sec

    traces = []
    for i in range(N):
        sp = simulate_statepath(K, pi, A, T)
        fret, donor, acceptor, _ = simulate_fret_experiment(
            sp, np.linspace(0, 1, K), 800, 30, bleach_lifetime_frames
        )
        traces.append((donor, acceptor))
    t = np.arange(fret.size) * frame_time_sec

    # plt.subplot(3, 1, 1)
    # plt.plot(t, traces[-1][1], c="tab:orange")
    # plt.plot(t, traces[-1][0], c="tab:green")
    # plt.subplot(3, 1, 2)
    # plt.plot(t, fret, c="tab:blue")
    # plt.ylim(-0.1, 1.1)
    # plt.subplot(3, 1, 3)
    # plt.plot(t, np.vstack(traces[-1]).sum(axis=0), c="k")

    # plt.gcf().set_size_inches(10, 6)
    # plt.tight_layout()
    # plt.show()

    pks = sample_spot_locations(512, 20, N)
    image = make_image(traces, pks, 512)

    # plt.imshow(image, vmax=255)
    # plt.show()
