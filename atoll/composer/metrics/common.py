import numpy as np
from scipy import stats


def beta_binomial_model(y, n, alpha, beta, quantile):
    # alpha and beta are priors for the beta prior
    # the beta posterior is Beta(y + alpha, n - y + beta)
    alpha_ = y + alpha
    beta_ = n - y + beta
    return stats.beta.ppf(quantile, alpha_, beta_)


def gamma_poission_model(X, n, k, theta, quantile):
    # k (shape) and theta (scale) are priors for the gamma prior
    # the posterior is a gamma distribution parameterized as follows,
    # since the gamma distribution is a conjugate prior for the poisson
    k = np.sum(X) + k
    t = theta/(theta*n + 1)

    # we want to be conservative in our estimate of the poisson's lambda parameter
    # so we take the lower-bound of the 90% confidence interval (i.e. the 0.05 quantile)
    # rather than the expected value

    # scipy's ppf func for its distributions is the inverse CDF
    return stats.gamma.ppf(quantile, k, scale=t)
