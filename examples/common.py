import os
import json
import random
import numpy as np
from scipy import stats


def identity(x):
    return x


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


def sample_dict(sample, n=10):
    """
    Sample a dictionary
    """
    keys = random.sample(list(sample.keys()), n)
    return {k:sample[k] for k in keys}


def load_data(fname):
    data_dir = os.path.expanduser('~/data')
    with open(os.path.join(data_dir, fname), 'r') as f:
        d = json.load(f)
    return d


def standardize(comments, key_map):
    """
    Convert comments to a standardized format
    according to the specified key map
    """
    results = []
    for d in comments:
        d_ = {}
        for k, v in key_map.items():
            if isinstance(v, dict):
                key = v['key']
                f = v.get('transform', identity)
                default = v.get('default', None)

            else:
                key, f = v, identity
                default = None

            try:
                subkeys = k.split('.')
                raw_val = d[subkeys[0]]
                for subkey in subkeys[1:]:
                    raw_val = raw_val[subkey]
                d_[key] = f(raw_val)
            except:
                if default is not None:
                    d_[key] = default
                else:
                    raise
        results.append(d_)
    return results



def report(input):
    print('input size (objects):', len(input))
    print('input size (comments):', sum(len(v) for k, v in input))
    print('Mean comments/object:', sum(len(v) for k,v  in input)/len(input))
    return input



def merge_dicts(d1, d2):
    d1.update(d2)
    return d1


def means(scores, keys=[]):
    """
    Computes means for values in a dictionary
    """
    results = {}
    # can be more efficient, just a sketch
    for k in keys:
        ss = [s[k] for _, s in scores]
        results[k] = sum(ss)/len(ss)
    return results
