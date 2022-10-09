import numpy as np
from smtirf import Experiment


# fmt: off
ref_state_path = np.array(
    [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1, 1, 1, 0, 0, 2]
)
ref_emission_path = np.array(
    [-0.05613604, -0.05613604, -0.05613604, -0.05613604, -0.05613604, -0.05613604,
     -0.05613604, -0.05613604,  1.00375579,  1.00375579,  1.00375579,  1.00375579,
      1.00375579,  1.00375579,  1.00375579,  1.00375579,  1.00375579, -0.05613604,
     -0.05613604,  0.45393879,  0.45393879,  0.45393879, -0.05613604, -0.05613604,
      1.00375579]
)
# fmt: on


def test_deterministic_hmm(fret_short_file):
    filename_base, params, statepaths = fret_short_file
    experiment = Experiment.from_pma(filename_base.with_suffix(".traces"), "fret")

    trc = experiment[0]
    trc.train(
        "em",
        params["K"],
        sharedVariance=False,
        refineByKmeans=False,
        maxIter=1000,
        tol=1e-5,
        printWarnings=False,
    )
    state_path = trc.SP
    emission_path = trc.EP

    np.testing.assert_equal(state_path, ref_state_path)
    np.testing.assert_almost_equal(emission_path, ref_emission_path)

    for _ in range(5):
        trc.train(
            "em",
            params["K"],
            sharedVariance=False,
            refineByKmeans=False,
            maxIter=1000,
            tol=1e-5,
            printWarnings=False,
        )
        np.testing.assert_equal(trc.SP, state_path)
        np.testing.assert_equal(trc.EP, emission_path)
