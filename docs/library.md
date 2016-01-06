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

```
Endpoint: `/users/score`

Description: Computes the following metrics for a list of users:
- discussion score
    - estimated number of replies a comment by this user will receive. Provides a sense of how much discussion this user tends to generate, without regard to what kind of discussion
    - range: [0, +infinity], more is better
- moderated probability
    - estimated probability that a comment by this user will be moderated.
    - range: [0, 1], less is better
- like score
    - estimated number of likes a comment by this user will receive. Provides a sense of community approval.
    - range: [0, +infinity], more is better
- starred score
    - estimated probability that a comment by this user will be "starred" (i.e. be chosen as an "editor's pick"). Provides a sense of organizational approval.
    - range: [0, 1], more is better

Technical Description: All of these metrics are computed with simple Bayesian models. To be conservative, the point estimate used for each score is the lower-bound of the 90% confidence interval (the 0.05 quantile) rather than the expected value.
- The discussion score is computed using a Gamma-Poisson model based on the number of replies past comments by the user have received. The prior is parameterized with `shape=1, scale=2`.
- The moderated probability is computed using a Beta-Binomial model based on the user's moderation history. The prior is parameterized with `alpha=2, beta=2`.
- The like score is computed using a Gamma-Poisson model based on the number of likes past comments by the user have received. The prior is parameterized with `shape=1, scale=2`.
- The starred score is computed using a Beta-Binomial model based on the number of "starred" comments in the user's comment history. The prior is parameterized with `alpha=2, beta=2`.

Input: [{
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

Output: [{
    'id': int,
    'discussion_score': float,
    'like_score': float,
    'starred_score': float,
    'moderated_prob': float
}]
```
