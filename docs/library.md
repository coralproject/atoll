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

Note that `atoll` only computes metrics for which the necessary keys are available. For instance, if some metric requires that an entity has an `actions` field, and it is not present, that metric will be skipped.

For the basic scoring endpoints, e.g. `/<entity>/score`, the response has JSON data in the following format:

```
{
    'results': {
        'collection': [{...}],  # computed metrics for each entity
        'aggregates': {         # aggregate statistics for each metric across the entire collection
            'mean': float,
            'min': float,
            'max': float,
            'std': float,
            'count': int
        }
    }
}
```

---

## Users pipeline

__Endpoint__: `/users/score`

__Description__: Computes the following metrics for a list of users. The computed values are designed to err on the side of caution, so will tend to be lower/less accurate for newer users or users with little activity.

__Technical description__: All of these metrics are computed with simple Bayesian models. To be conservative, the point estimate used for each score is the lower-bound of the 90% confidence interval (the 0.05 quantile) rather than the expected value.

__Input__:
```
{'data': [{
    '_id': str,
    'comments': [{
        '_id': str,
        'user_id': str,
        'parent_id': str,
        'children': [ ...comments... ],
        'actions': [{'type': str, 'val': int}, ...], # e.g. {'type': 'likes', 'val': 10}, {'type': 'starred', 'val': bool}
        'status': int,
        'body': str,
        'date_created': isoformat datetime
    }, ...]
}, ...]}
```

__Output__:
```
{'results':
    'collection': [{
        'id': str,
        'discussion_score': float,
        'like_score': float,
        'organization_score': float,
        'moderated_prob': float
    }, ...],
    'aggregates': {...}
}
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
{'data': [{
    '_id': str,
    'user_id': str,
    'parent_id': str,
    'children': [ ...comments... ],
    'actions': [{'type': str, 'val': int}, ...],
    'status': int,
    'body': str,
    'date_created': isoformat datetime
}, ...]}
```

__Output__:
```
{'results':
    'collection': [{
        'id': str,
        'diversity_score': float,
        'readability_scores': { ... }
    }, ...],
    'aggregates': {...}
}
```

### Metrics

#### Diversity score

__Description__: estimates the probability that a new reply to this comment would be posted from a new replier.

__Technical Description__: The diversity score is computed using a Beta-Binomial model based on the diversity of replies this comment has received so far. The prior is parameterized with `alpha=2, beta=2`.

__Range__: `[0, 1]`, more is better

#### Readability scores

__Description__: computes several different readability scores for the text of a comment.

##### Automated Readability Index (ARI)

__Description__: estimates the US grade level necessary to read the text.

__Technical Description__: the ARI is computed with the following formula:

    4.71 * (# characters/# words) + 0.5 * (# words/# sentences) - 21.43

__Range__: `[-16.22, +infinity)`, more may be better or not depending on your goals

##### Flesch Reading Ease

__Description__: estimates how difficult a text is to read.

__Technical Description__: the Flesch Reading Ease is computed with the following formula:

    206.835 - 1.015 * (# words/# sentences) - 84.6 * (# syllables/# words)

__Range__: `(-infinity, 121.22]`. From [Wikipedia](https://en.wikipedia.org/wiki/Flesch–Kincaid_readability_tests#Flesch_reading_ease):

| Score      | Interpretation                                      |
|------------|-----------------------------------------------------|
| 90.0–100.0 | easily understood by an average 11-year-old student |
| 60.0–70.0  | easily understood by 13- to 15-year-old students    |
| 0.0–30.0   | best understood by university graduates             |

##### Flesch-Kincaid Grade Level

__Description__: estimates the US grade level necessary to read the text.

__Technical Description__: The Flesch-Kincaid Grade Level is computed with the following formula:

    0.39 * (# words/# sentences) + 11.8 (# syllables/# words) - 15.59

__Range__: `[-3.4, +infinity)`, more may be better or not depending on your goals

##### Coleman-Liau Index

__Description__: estimates the US grade level necessary to read the text.

__Technical Description__: The Coleman-Liau Index is computed with the following formula:

    0.0588 (avg # letters per 100 words) - 0.296 (avg # sentences per 100 words) - 15.8

__Range__: `[-15.8, +infinity)`, more may be better or not depending on your goals

##### Gunning fog index

__Description__: estimates the years of formal education necessary to read the text.

__Technical Description__: The Gunning fog index is computed with the following formula:

    0.4 * ((# words/# sentences) + 100 (# complex words/# words))

Where a "complex" word is defined as one with three or more syllables, excluding "proper nouns, familiar jargon, or compound words" and not counting "common suffixes" as syllables (see [Wikipedia](https://en.wikipedia.org/wiki/Gunning_fog_index)).

__Range__: `[0.4, +infinity)`, more may be better or not depending on your goals

##### SMOG index

__Description__: estimates the years of formal education necessary to read the text.

__Technical Description__: The SMOG index is computed with the following formula:

    1.0430 * sqrt(# polysyllables * (30/# sentences)) + 3.1291

Where a "polysyllable" is a word with three or more syllables.

__Range__: `[3.1291, +infinity)`, more may be better or not depending on your goals

##### LIX (Laesbarheds Index)

__Description__: estimates the difficulty of a text.

__Technical Description__: The LIX is computed with the following formula:

    (# words/# sentences) + 100 * (# words longer than 6 characters/# words)

__Range__: `[1, +infinity)`, more may be better or not depending on your goals. From [Ideosity](https://www.ideosity.com/readability-tests-and-formulas/#LIX):

| Score | Interpretation |
|-------|----------------|
| 0-24  | Very easy      |
| 25-34 | Easy           |
| 35-44 | Standard       |
| 45-54 | Difficult      |
| 55+   | Very difficult |

##### RIX

__Description__: estimates the difficulty of a text.

__Technical Description__: The LIX is computed with the following formula:

    # words longer than 6 characters/# sentences

__Range__: `[0, +infinity)`, more may be better or not depending on your goals. A score of 7.2 or above is interpreted as college-level, 0.2 or below is interpreted as US grade 1.

## Assets pipeline

__Endpoint__: `/assets/score`

__Description__: Computes the following metrics for a list of assets. The computed values are designed to err on the side of caution, so will tend to be low/less accurate for newer assets or assets with fewer comments.

__Technical description__: All of these metrics are computed with simple Bayesian models. To be conservative, the point estimate used for each score is the lower-bound of the 90% confidence interval (the 0.05 quantile) rather than the expected value.

__Input__:
Either:
```
{'data': [{
    '_id': str,
    'threads': [ thread-structured comments ],
}, ...]}
```

Or:
```
{'data': [{
    '_id': str,
    'comments': [ flat list of comments ],
}, ...]}
```

__Output__:
```
{'results':
    'collection': [{
        'id': str,
        'discussion_score': float,
        'diversity_score': float
    }, ...],
    'aggregates': {...}
}
```

### Metrics

#### Diversity score

__Description__: estimates the probability that a new reply to this asset would be posted from a new replier.

__Technical Description__: The diversity score is computed using a Beta-Binomial model based on the diversity of replies this asset has received so far. The prior is parameterized with `alpha=2, beta=2`.

__Range__: `[0, 1]`, more is better

#### Discussion score

__Description__: estimates the length of a new thread started for this asset.

__Technical Description__: The diversity score is computed using a Gamma-Poisson model based on the length of the threads for this asset so far. The prior is parameterized with `shape=1, scale=2`.

__Range__: `[0, +infinity)`, more is better

---

## NLP Endpoints

There is support for training and running NLP models.

At this point, the only model available is a comments moderation probability model (logistic regression), based on simple word usage.

Two endpoints are exposed for this:

- `/comments/model/moderation/train`. POST a collection of comments and a model name, e.g. `{'data': [ ...comments...], 'name': 'my_comments_model'}` to train the model. A response consisting of the following is returned:

    {'results': {
        'performance': {...},   # scores for the model, such as ROC AUC
        'n_samples': int,       # number of samples you submitted
        'notes': [...],         # any notes, such as suggestions
        'name': str             # the name of the model
    }}

- `/comments/model/moderation/run` POST a collection of comments and a model name, e.g. `{'data': [ ...comments...], 'name': 'my_comments_model'}` to run the model. A response consisting of the following is returned:

    {'results': [{
        'id': str,      # id of the comment
        'prob': float   # probability that the comment would be moderated
    }, ...]}

## Taxonomy endpoints

Comments and assets can be broken down by taxonomy (e.g. tags) and have metrics computed aggregately over these groups.

The two endpoints for this are:

- `assets/score/taxonomy`
- `comments/score/taxonomy`

You POST collections to these endpoints like you would for the basic scoring endpoints, but the response takes the format:

    {'results': {
        'sometag': { ... }, # metric aggregates, e.g. mean, std, etc
        'someothertag': { ... },
        ...
    }}

## Rolling metrics

For users, rolling metrics may be computed, so that their metrics can be updated without sending their entire history of data.

The endpoint for this is:

- `/users/rolling`

This requires data to be POSTed with the following form:

    {'data': [{
        'update': { ... }   # latest data for the user
        'prev': { ... }     # the previously computed metrics for the user
    }, ...]}

Then it returns data in the same format as the regular user scoring endpoint.
