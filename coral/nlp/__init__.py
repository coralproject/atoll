from atoll import Pipeline
from .models import train_binary, run_model, preprocess


def extract_samples(data):
    return data['samples']

def extract_name(data):
    return data['name']

def extract_labels(comments):
    return [True if c['status'] < 3 else False for c in comments]


train_moderation_model = Pipeline(name='train_comments_moderation_model').fork(extract_name, extract_samples).to(preprocess, label_func=extract_labels).to(train_binary)
run_moderation_model = Pipeline(name='run_comments_moderation_model').fork(extract_name, extract_samples).to(run_model)
