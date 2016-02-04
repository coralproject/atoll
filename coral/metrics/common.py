import numpy as np
from scipy import stats
from functools import wraps, reduce


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


def required_keys(*keys):
    """before running the decorated function,
    check that all keys are present.
    nested keys can be specified using dot syntax"""
    def decorator(func):
        @wraps(func)
        def wrapper(obj, *args, **kwargs):
            if all(has_key(obj, key) for key in keys):
                return func(obj, *args, **kwargs)
            return None
        return wrapper
    return decorator


def get_item(d, k):
    """attempts to get an item from d
    at key k. if d is a list and the key is the list selector [],
    then tries to return the first item from the list.
    if the list is empty, returns None."""
    try:
        return d[k]
    except KeyError:
        if k.endswith('[]'):
            lst = d[k[:-2]]
            try:
                return lst[0]
            except IndexError:
                # return None for empty list
                return None
        return {}


def has_key(d, path):
    """test if the key path exists for the dict"""
    keys = path.split('.')
    try:
        last = reduce(get_item, keys[:-1], d)

        # if last is None, indicating an empty list,
        # return True
        if last is None:
            return True

        return keys[-1] in last
    except KeyError:
        return False
