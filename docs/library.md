# Pipeline Library

This document contains a set of pipelines.  Each pipeline is designed to calculate one or more _Metrics_ on an _Entity_.

Pipeline template:

```
Name: "..."

Ordinary Descripiton: "..."

Technical Description (optional): "..."

Input: [Comment|User|...]

Output: { [name]: [value with type/range info] }
```

---

## Users pipeline

__Endpoint__: `/users/score`

__Description__: Computes the following metrics for a list of users. The computed values are designed to err on the side of caution, so will tend to be lower/less accurate for newer users or users with little activity.

__Technical description__: All of these metrics are computed with simple Bayesian models. To be conservative, the point estimate used for each score is the lower-bound of the 90% confidence interval (the 0.05 quantile) rather than the expected value.

__Input__:
```
[{
    'id': int,
    'comments': [{
        'id': int,
        'user_id': int,
        'parent_id': int,
        'children': [ ...comments... ],
        'likes': int,
        'starred': bool,
        'moderated': bool,
        'content': str,
        'date_created': isoformat datetime
    }, ...]
}, ...]
```

__Output__:
```
[{
    'id': int,
    'discussion_score': float,
    'like_score': float,
    'starred_score': float,
    'moderated_prob': float
}, ...]
```

### Metrics

#### Discussion score

__Description__: estimated number of replies a comment by this user will receive. Provides a sense of how much discussion this user tends to generate, without regard to what kind of discussion

__Technical Description__: The discussion score is computed using a Gamma-Poisson model based on the number of replies past comments by the user have received. The prior is parameterized with `shape=1, scale=2`.

__Range__: `[0, +infinity)`, more is better


#### Moderation probability

__Description__: estimated probability that a comment by this user will be moderated.

__Technical Description__: The moderated probability is computed using a Beta-Binomial model based on the user's moderation history. The prior is parameterized with `alpha=2, beta=2`.

__Range__: `[0, 1]`, less is better


#### Community approval

__Description__: estimated number of likes a comment by this user will receive. Provides a sense of community approval.

__Technical Description__: The like score is computed using a Gamma-Poisson model based on the number of likes past comments by the user have received. The prior is parameterized with `shape=1, scale=2`.

__Range__: `[0, +infinity)`, more is better


#### Organizational approval

__Description__: estimated probability that a comment by this user will be "starred" (i.e. be chosen as an "editor's pick"). Provides a sense of organizational approval.

__Technical Description__: The starred score is computed using a Beta-Binomial model based on the number of "starred" comments in the user's comment history. The prior is parameterized with `alpha=2, beta=2`.

__Range__: `[0, 1]`, more is better

## Comments pipeline

__Endpoint__: `/comments/score`

__Description__: Computes the following metrics for a list of comments. The computed values are designed to err on the side of caution, so will tend to be low/less accurate for newer comments or comments with fewer replies.

__Technical description__: All of these metrics are computed with simple Bayesian models. To be conservative, the point estimate used for each score is the lower-bound of the 90% confidence interval (the 0.05 quantile) rather than the expected value.

__Input__:
```
[{
    'id': int,
    'user_id': int,
    'parent_id': int,
    'children': [ ...comments... ],
    'likes': int,
    'starred': bool,
    'moderated': bool,
    'content': str,
    'date_created': isoformat datetime
}, ...]
```

__Output__:
```
[{
    'id': int,
    'diversity_score': float
}, ...]
```

### Metrics

#### Diversity score

__Description__: estimates the probability that a new reply to this comment would be posted from a new replier.

__Technical Description__: The diversity score is computed using a Beta-Binomial model based on the diversity of replies this comment has received so far. The prior is parameterized with `alpha=2, beta=2`.

__Range__: `[0, 1]`, more is better

## Assets pipeline

__Endpoint__: `/assets/score`

__Description__: Computes the following metrics for a list of assets. The computed values are designed to err on the side of caution, so will tend to be low/less accurate for newer assets or assets with fewer comments.

__Technical description__: All of these metrics are computed with simple Bayesian models. To be conservative, the point estimate used for each score is the lower-bound of the 90% confidence interval (the 0.05 quantile) rather than the expected value.

__Input__:
Either:
```
[{
    'id': int,
    'threads': [ thread-structured comments ],
}, ...]
```

Or:
```
[{
    'id': int,
    'comments': [ flat list of comments ],
}, ...]
```

__Output__:
```
[{
    'id': int,
    'discussion_score': float,
    'diversity_score': float
}, ...]
```

### Metrics

#### Diversity score

__Description__: estimates the probability that a new reply to this asset would be posted from a new replier.

__Technical Description__: The diversity score is computed using a Beta-Binomial model based on the diversity of replies this asset has received so far. The prior is parameterized with `alpha=2, beta=2`.

__Range__: `[0, 1]`, more is better

#### Discussion score

__Description__: estimates the length of a new thread started for this asset.
j
__Technical Description__: The diversity score is computed using a Gamma-Poisson model based on the length of the threads for this asset so far. The prior is parameterized with `shape=1, scale=2`.

__Range__: `[0, +infinity)`, more is better
