import math
import json
import os
import sys
from atoll import Pipeline


# Usage:
#  python userWordCount.py comments.json

comment_lines = open(sys.argv[1], 'r')

comments = []

for message_json in comment_lines:
    message = json.loads(message_json)

    # Check to see if the message is valid
    if 'name' in message:
        # Get comment text
        comment = message['payload']['body']
        user = message['payload']['user_id']
        comments.append((user, comment))
    else:
        print("UNKNOWN FORMAT: name field not found. " + json.dumps(message), file=sys.stderr)

def wordCount(user, comment):
    # Word count and user
    wc = len(comment.split(" "))
    return (user, (wc, 1))

def addMean(x, y):
    return (x[0] + y[0], x[1] + y[1])

def divideMean(u, m):
    return (u, m[0]/m[1])

pipeline1 = Pipeline(name='wc_pipeline').map(wordCount).reduceByKey(addMean).map(divideMean)
results = pipeline1(comments)

for r in results:
    print(r[0], r[1])

