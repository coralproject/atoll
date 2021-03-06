import os
import joblib
import numpy as np
from collections import defaultdict
from sklearn import cross_validation, metrics
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

mets = ['roc_auc_score', 'f1_score', 'log_loss', 'precision_score', 'recall_score']


def models_dir():
    dir = os.path.dirname(__file__)
    models_path = os.path.expanduser(os.path.join(dir, 'models'))
    if not os.path.isdir(models_path):
        os.makedirs(models_path)
    return models_path


def preprocess(name, comments, label_func):
    # labels
    labels = np.array(label_func(comments))

    # simple tfidf vectorization (for now, can enhance later)
    vector = TfidfVectorizer()
    vecs = vector.fit_transform((c['body'] for c in comments))

    # save vectorizer
    models_path = models_dir()
    joblib.dump(vector, '{}/{}_vectorizer.pkl'.format(models_path, name))

    return name, vecs, labels


def train_binary(name, vecs, labels):
    """train a generic binary classification model (logistic regression)"""
    notes = []
    if len(labels) < 10000:
        notes.append('For best performance, it is recommended you provide at least 10,000 samples.')

    # performance metrics
    scores = defaultdict(list)
    skf = cross_validation.StratifiedKFold(labels, n_folds=3, shuffle=True)
    for train_idx, test_idx in skf:
        X_train, X_test = vecs[train_idx], vecs[test_idx]
        y_train, y_test = labels[train_idx], labels[test_idx]
        model = LogisticRegression()
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        for metric in mets:
            scores[metric].append(getattr(metrics, metric)(y_test, pred))

    # compute means for each score
    scores = {metric: np.mean(scores[metric]) for metric in mets}
    if scores['roc_auc_score'] <= 0.6:
        notes.append('The model does not perform very well. It is not recommended you use it.')

    # train the full model
    model = LogisticRegression()
    model.fit(vecs, labels)

    # save the model
    models_path = models_dir()
    joblib.dump(model, '{}/{}.pkl'.format(models_path, name))

    return {
        'performance': scores,
        'n_samples': len(labels),
        'notes': notes,
        'name': name
    }


def run_binary(name, comments):
    """run a binary model (logistic regression)"""
    models_path = models_dir()
    vector = joblib.load('{}/{}_vectorizer.pkl'.format(models_path, name))
    vecs = vector.transform((c['body'] for c in comments))

    model = joblib.load('{}/{}.pkl'.format(models_path, name))
    probs = model.predict_proba(vecs)

    pred = [{
        'id': c['_id'],
        'prob': prob[1]
    } for c, prob in zip(comments, probs)]
    return pred
