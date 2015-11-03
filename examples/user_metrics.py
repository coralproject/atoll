import numpy as np
from atoll import Pipeline
from examples.transform import reddit_map, nyt_map, wapo_map
from examples.common import beta_binomial_model, gamma_poission_model, standardize, load_data, merge_dicts, report, means


def like_score(comments, k=1, theta=2):
    """
    Approval by the community
    """
    X = np.array([c['likes'] for c in comments])
    n = len(X)

    # we want to be conservative in our estimate of the poisson's lambda parameter
    # so we take the lower-bound of the 90% confidence interval (i.e. the 0.05 quantile)
    # rather than the expected value
    return {'community_score': gamma_poission_model(X, n, k, theta, 0.05)}


def starred_score(comments, alpha=2, beta=2):
    """
    Approval by the organization
    """
    # assume whether or not a comment is starred
    # is drawn from a binomial distribution parameterized by n, p
    # n is known, we want to estimate p
    y = sum(1 for c in comments if c['starred'])
    n = len(comments)

    # again, to be conservative, we take the lower-bound
    # of the 90% credible interval (the 0.05 quantile)
    return {'organization_score': beta_binomial_model(y, n, alpha, beta, 0.05)}

    # if we wanted the expected value:
    #return user, alpha/(alpha+beta)


def moderated_prob(comments, alpha=2, beta=2):
    """
    Probability that a comment is moderated
    """
    y = sum(1 for c in comments if c['moderated'])
    n = len(comments)
    return {'moderation_prob': beta_binomial_model(y, n, alpha, beta, 0.05)}


def discussion_score(comments, k=1, theta=2):
    X = np.array([c['n_replies'] for c in comments])
    n = len(X)
    return {'discussion_score': gamma_poission_model(X, n, k, theta, 0.05)}


def run():
    preprocess = Pipeline().mapValues(standardize, kwargs=['key_map']).to(report)

    # TODO add some kind of fork->map support
    community_score = Pipeline().mapValues(like_score)
    organization_score = Pipeline().mapValues(starred_score)
    discuss_score = Pipeline().mapValues(discussion_score)
    mod_prob = Pipeline().mapValues(moderated_prob)

    pipeline = Pipeline()\
        .to(preprocess)\
        .fork(community_score, organization_score, discuss_score, mod_prob)\
        .flatMap(None)\
        .reduceByKey(merge_dicts)\
        .fork(None, Pipeline().to(means,
                            keys=['community_score', 'organization_score',
                                    'discussion_score', 'moderation_prob']))
    print(pipeline)

    for dataset, key_map in [
        ('nyt_user_sample.json', nyt_map),
        ('wapo_user_sample.json', wapo_map),
        ('reddit_user_sample.json', reddit_map),
    ]:
        print('\n',dataset,'\n')

        sample = load_data(dataset)
        scores, avgs = pipeline(sample, key_map=key_map)
        print('averages:', avgs)
        print('sample score:', scores[0])
