import numpy as np
import json
from .. import SMJsonEncoder, SMJsonDecoder
from . import row, col, normalize_rows, ExitFlag
from . import algorithms as hmmalg
from .distributions import *
from . import hyperparameters as hyper


class BaseHiddenMarkovModel():

    def simulate(self, M=1, T=1000):
        """ simulate M traces of length T from model """
        S = [hmmalg.sample_statepath(self.K, self.pi, self.A, T=T) for m in range(M)]
        Y = [np.random.normal(loc=self.mu[s], scale=self.sigma[s]) for s in S]
        return [(s, y) for s, y in zip(S,Y)]

    def label(self, x, deBlur=False, deSpike=False):
        SP = hmmalg._viterbi(x, self.pi, self.A, self.p_X(x).T).astype(int)
        return SP

    def get_emission_path(self, SP):
        return self.mu[SP]


class ClassicHiddenMarkovModel(BaseHiddenMarkovModel):
    modelType = "em"

    def __init__(self, K, pi, A, mu, tau, sharedVariance, exitFlag=None):
        self._K = K
        self._pi = Categorical(pi)
        self._A = CategoricalArray(A)
        if sharedVariance:
            self._phi = NormalSharedVariance(mu, tau)
        else:
            self._phi = Normal(mu, tau)
        assert self._pi.K == K and self._A.K == K and self._phi.K == K
        self.sharedVariance = sharedVariance
        self.exitFlag = exitFlag

    def _as_json(self):
        return json.dumps({"modelType": self.modelType,
                           "K": self.K,
                           "pi": self.pi,
                           "A": self.A,
                           "mu": self.mu,
                           "tau": self.tau,
                           "sharedVariance": self.sharedVariance,
                           "exitFlag": self.exitFlag}, cls=SMJsonEncoder)

    @classmethod
    def _from_json(cls, d):
        d["exitFlag"] = ExitFlag(**d["exitFlag"])
        return cls(**d)

    @property
    def K(self): return self._K

    @property
    def pi(self): return self._pi.mu

    @property
    def A(self): return self._A.mu

    @property
    def mu(self): return self._phi.mu

    @property
    def tau(self): return self._phi.tau

    @property
    def sigma(self): return self._phi.sigma

    def p_X(self, x):
        return self._phi.p_X(x)

    # TODO => update_global, train_new_global

    def update(self, x, gamma, xi):
        self._pi.update(gamma[0])
        self._A.update(xi/col(gamma[:-1].sum(axis=0)))
        self._phi.update(x, gamma)

    def train(self, x, maxIter=1000, tol=1e-5, printWarnings=True):
        self.exitFlag = hmmalg.train_baumwelch(x, self, maxIter=maxIter, tol=tol, printWarnings=printWarnings)

    # TODO => muScale for PIFE data
    @classmethod
    def train_new(cls, x, K, sharedVariance, refineByKmeans=True, maxIter=1000, tol=1e-5, printWarnings=True):
        # initial guess for parameters
        pi = np.ones(K)/K
        A = normalize_rows(np.eye(K)*1 + np.ones((K,K)))
        mu = np.linspace(0, 1, K+2)[1:-1]
        if sharedVariance:
            sigma = 0.1
        else:
            sigma = np.ones(K)*0.1
        theta = cls(K, pi, A, mu, 1/sigma**2, sharedVariance)
        # TRAIN
        if refineByKmeans:
            theta.refine_by_kmeans(x)
        theta.train(x)
        return theta

    def refine_by_kmeans(self, x):
        self._phi.refine_by_kmeans(x)



class VariationalHiddenMarkovModel(BaseHiddenMarkovModel):
    modelType = "vb"

    def __init__(self, K, u, w, sharedVariance, exitFlag=None):
        self._K = K
        self._u = u
        self._w = w
        assert self._u.K == K and self._w.K == K
        self.sharedVariance = sharedVariance
        self.exitFlag = exitFlag

    def _as_json(self):
        return json.dumps({"modelType": self.modelType,
                           "K": self.K,
                           "u": self._u,
                           "w": self._w,
                           "sharedVariance": self.sharedVariance,
                           "exitFlag": self.exitFlag}, cls=SMJsonEncoder)

    @classmethod
    def _from_json(cls, d):
        hcls = hyper.HMMHyperParametersSharedVariance if d["sharedVariance"] else hyper.HMMHyperParameters
        for p in ("u", "w"):
            d[p] = hcls(**d[p])
        d["exitFlag"] = ExitFlag(**d["exitFlag"])
        return cls(**d)

    @property
    def K(self):
        return self._K

    @property
    def pi(self):
        return self._w.pi

    @property
    def A(self):
        return self._w.A

    @property
    def mu(self):
        return self._w.mu

    @property
    def sigma(self):
        return self._w.sigma

    def p_X(self, x):
        return self._w.p_X(x)

    def update(self, u, x, gamma, xi):
        # calculate sufficient calculate sufficient statistics
        Nk = gamma.sum(axis=0)
        xbar = np.sum(gamma*col(x), axis=0)/Nk
        S = np.sum(gamma*(col(x)-row(xbar))**2, axis=0)/Nk # variance
        # update posterior
        self._w.update(u, gamma, xi, Nk, xbar, S)

    # TODO => update_global, train_new_global

    def train(self, x, maxIter=1000, tol=1e-5, printWarnings=True):
        self.exitFlag = hmmalg.train_variational(x, self, maxIter=maxIter, tol=tol, printWarnings=printWarnings)
        try:
            self._w.sort()
        except IndexError: # multimer model has no sort method
            pass

    @classmethod
    def train_new(cls, x, K, sharedVariance, refineByKmeans=True, repeats=5, maxIter=1000, tol=1e-5, printWarnings=False):
        # initialize prior
        if sharedVariance:
            u = hyper.HMMHyperParametersSharedVariance.uninformative(K)
        else:
            u = hyper.HMMHyperParameters.uninformative(K)
        # sample posteriors from prior for r repeats
        thetas = [cls(K, u, u.sample_posterior(), sharedVariance) for r in range(repeats)]
        # TODO => update by kmeans
        # TRAIN
        for theta in thetas:
            if refineByKmeans:
                theta.refine_by_kmeans(x)
            theta.train(x, printWarnings=printWarnings)
        # select most likely model (largest Lmax)
        thetas.sort(reverse=True, key=lambda theta: theta.exitFlag.Lmax)
        return thetas[0]

    def refine_by_kmeans(self, x):
        self._w.refine_by_kmeans(x, self._u)


class MultimerHiddenMarkovModel(VariationalHiddenMarkovModel):
    modelType = "multimer"

    def __init__(self, K, u, w, sharedVariance=True, exitFlag=None):
        sharedVariance = True # *** model only defined for shared variance ***
        super().__init__(K, u, w, sharedVariance, exitFlag)

    @classmethod
    def _from_json(cls, d):
        hcls = hyper.HmmHyperParametersMultimer
        for p in ("u", "w"):
            d[p] = hcls(**d[p])
        d["exitFlag"] = ExitFlag(**d["exitFlag"])
        return cls(**d)

    @property
    def delta(self): return self._w.delta

    @property
    def mu0(self): return self._w.mu0

    @classmethod
    def train_new(cls, x, K, sharedVariance, refineByKmeans=False, repeats=5, maxIter=1000, tol=1e-5, printWarnings=False):
        # initialize prior
        if sharedVariance:
            u = hyper.HmmHyperParametersMultimer.uninformative(K)
        else:
            u = hyper.HmmHyperParametersMultimer.uninformative(K)
        # sample posteriors from prior for r repeats
        thetas = [cls(K, u, u.sample_posterior(), sharedVariance) for r in range(repeats)]
        # TODO => update by kmeans
        # TRAIN
        for theta in thetas:
            if refineByKmeans:
                # theta.refine_by_kmeans(x)
                # TODO => warn not implemented
                pass
            theta.train(x, printWarnings=printWarnings)
        # select most likely model (largest Lmax)
        thetas.sort(reverse=True, key=lambda theta: theta.exitFlag.Lmax)
        return thetas[0]

    def update(self, u, x, gamma, xi):
        # calculate sufficient calculate sufficient statistics
        T, K = gamma.shape
        Nk = gamma.sum(axis=0)
        # average baseline offset
        dbar = np.sum(gamma[:,0]*x)/Nk[0] # [1, ]
        # correct signal for offset, estimate monomer intensity
        xk = np.repeat(col(x), K-1, axis=1) - dbar # [T x K-1]
        xk = xk/row(np.arange(1,K))
        xbar = np.sum(gamma[:,1:]*xk)/Nk[1:].sum() # [1, ]
        mu = np.arange(K)*xbar + dbar # [K, ]
        S = np.sum(gamma*(col(x)-row(mu))**2, axis=0).sum()/Nk.sum() # variance
        # update posterior
        self._w.update(u, gamma, xi, Nk, dbar, xbar, S)


class HiddenMarkovModel():

    MODEL_TYPES = {"em" : ClassicHiddenMarkovModel,
                   "vb" : VariationalHiddenMarkovModel,
                   "multimer" : MultimerHiddenMarkovModel}

    @staticmethod
    def train_new(modelType, x, K, sharedVariance, **kwargs):
        """ kwargs -> maxIter, tol, printWarnings, {repeats} """
        cls = HiddenMarkovModel.MODEL_TYPES[modelType]
        theta = cls.train_new(x, K, sharedVariance, **kwargs)
        return theta

    @staticmethod
    def from_json(jString):
        if jString is None:
            return None
        try:
            model = json.loads(jString, cls=SMJsonDecoder)
        except TypeError:
            model = jString # already dict
        modelType = model.pop("modelType")
        cls = HiddenMarkovModel.MODEL_TYPES[modelType]
        return cls._from_json(model)
