import json
import random


def random_string(length=10):
    return ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length)])

def random_comments(users, n=100, p_responses=0.5):
    n_replies = [random.randint(1,2) if random.random() < p_responses else 0 for _ in range(n)]

    return [{
        'user': random.choice(users),
        'body': ' '.join(random_string() for _ in range(10)),
        'replies': random_comments(users, n=r)
    } for r in n_replies]


if __name__ == '__main__':
    users = [random_string() for _ in range(20)]
    raw_data = random_comments(users)

    with open('threads.json', 'w') as f:
        json.dump(raw_data, f, indent=4)
