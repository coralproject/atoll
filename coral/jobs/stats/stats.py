# Usage:
#   python stats.py
# or
#   spark-submit stats.py pyspark

# Constants. Number of comments
# to load, connections.
N_COMMENTS = 100
MONGO_HOST = 'localhost'
MONGO_PORT = 27017

import sys

# Switch environment atoll/spark
if len(sys.argv) > 1:
    platform_arg = sys.argv[1]
else:
    platform_arg = ''

if platform_arg == 'pyspark':
    platform = 'spark'
    from pyspark import SparkConf, SparkContext
    conf = SparkConf().setAppName('stats')
    conf = conf.setMaster("local[*]")
    sc = SparkContext(conf=conf)
else:
    platform = 'atoll'
    from atoll import Pipeline


import json
import os
import pymongo
from bson.objectid import ObjectId
from functools import partial
from time import time


# Data extraction/transformation functions
# These are functions because fields may be
# nested, and for simple data transformations.
def getWordCount(message):
    wc = len(message['body'].split(" "))
    return (wc, 1)

def getReadability(message):
    r = ARI(message['body'])
    return (r, 1)

def getCreated(message):
    return message['date_created']

def getUserId(message):
    return message['user_id']

def getIsReply(message):
    return int(message['is_reply'])

def getHasReply(message):
    return int(message['has_reply'])

def one(x):
    return 1

def divideMean(x, y=None):
    if y is not None:
        return (x, y[0]/y[1])
    else:
        return (x[0], x[1][0]/x[1][1])


# Reduce functions
def addMean(x, y):
    return (x[0] + y[0], x[1] + y[1])

def count(x, y):
    return x + y

def smallest(x, y):
    if x < y:
        return x
    else:
        return y

def largest(x, y):
    if x > y:
        return x
    else:
        return y


# General function for creating a key
# to reduceByKey on and load data.
# We use partial to make more specific
# functions with one parameter.
def aggKey(fields, datafunc, dobj):
    dobj_fields = [str(dobj[f]) for f in fields]
    key = '.'.join(dobj_fields)
    return (key, datafunc(dobj))

# Utilities
def sanitize(s):
    # This is very blunt. Works for the purpose
    # of word count.
    return s.encode('ascii', 'ignore').decode('ascii')

def getAuthor(asset):
    """Get first author from asset"""

    a = "None"
    if 'authors' in asset:
        a = asset['authors'][0]['_id']
    if a == '':
        a = "None"
    return a

# More performant ARI. Drops nltk tokenizing
# and only does necessary metrics for ARI.
def ARI(text):
    wc = len(text.split(" "))
    cc = len(text)
    sc = text.count(".")

    # Smallest number of words/sentences
    # is one to avoid div by zero.
    if sc == 0:
        sc = 1

    score = 0.0
    if wc > 0.0:
        score = 4.71 * (cc / wc) + 0.5 * (wc / sc) - 21.43

    return score


def loadComments(comments_coll, assets_coll):
    comments_cursor = comments_coll.find().limit(N_COMMENTS)
    comments = []
    for comment in comments_cursor:
        # Leave elements as messages
        # since they will need to be
        # transformed to several different
        # keys for aggregation.
        # We want the data size to be very small.
        if 'asset_id' in comment:
            asset_id = ObjectId(comment['asset_id'])
            asset = assets_coll.find_one({"_id": asset_id})
            if 'section' in asset:
                c_sanitized = {}
                c_sanitized['section'] = sanitize(asset['section'])
                c_sanitized['author'] = sanitize(getAuthor(asset))
                c_sanitized['user_id'] = sanitize(str(comment['user_id']))
                c_sanitized['status'] = sanitize(comment['status'])
                c_sanitized['body'] = sanitize(comment['body'])
                c_sanitized['date_created'] = int(comment['date_created'].timestamp())
                c_sanitized['date_updated'] = int(comment['date_updated'].timestamp())
                c_sanitized['is_reply'] = 'parents' in comment and len(comment['parents']) > 0
                c_sanitized['has_reply'] = 'children' in comment and len(comment['children']) > 0
                c_sanitized['asset_id'] = str(asset['_id'])
                comments.append(c_sanitized)
    return comments


# Associate a path and a data munge function.
# Saves some typing.
def keyData(path, dataFunc):
      return partial(aggKey, path, dataFunc)

def getPipeline(name):
    if platform == 'atoll':
        return Pipeline(name=name)
    else:
        return sparkPipeline


def getCommonAggs(path):
    """Takes a pipeline and returns the common
    aggregations on it: count, replied count,
    replies count, first, last, word count."""

    pname = ".".join(path)
    aggs = {}
    aggs['count'] = getPipeline('c' + pname).map(keyData(path, one)).reduceByKey(count)
    aggs['replies'] = getPipeline('r' + pname).map(keyData(path, getIsReply)).reduceByKey(count)
    aggs['replied'] = getPipeline('rd' + pname).map(keyData(path, getHasReply)).reduceByKey(count)
    aggs['first'] = getPipeline('f' + pname).map(keyData(path, getCreated)).reduceByKey(smallest)
    aggs['last'] = getPipeline('l' + pname).map(keyData(path, getCreated)).reduceByKey(largest)
    aggs['wc'] = getPipeline('w' + pname).map(keyData(path, getWordCount)).reduceByKey(addMean).map(divideMean)
    aggs['readability'] = getPipeline('ry' + pname).map(keyData(path, getReadability)).reduceByKey(addMean).map(divideMean)
    return aggs


# Get the comments & assets
client = pymongo.MongoClient("mongodb://%s:%s" % (MONGO_HOST, MONGO_PORT))

db = client['coral']
assets_coll = db['assets']
comments_coll = db['comments']

comments = loadComments(comments_coll, assets_coll)


# This is required for getCommenAggs
if platform != 'atoll':
    sparkPipeline = sc.parallelize(comments)

# Create pipelines
all_aggs = {}
all_aggs['section_status'] = getCommonAggs(['user_id', 'section', 'status'])
all_aggs['author_status'] = getCommonAggs(['user_id', 'author', 'status'])
all_aggs['asset_status'] = getCommonAggs(['user_id', 'asset_id', 'status'])
all_aggs['section'] = getCommonAggs(['user_id', 'section'])
all_aggs['author'] = getCommonAggs(['user_id', 'author'])
all_aggs['asset'] = getCommonAggs(['user_id', 'asset_id'])


start_time = time()
# Do the work
for agg_collection in all_aggs:
    for agg in all_aggs[agg_collection]:
        if platform == 'atoll':
            all_aggs[agg_collection][agg] = all_aggs[agg_collection][agg](comments)
        else:
            all_aggs[agg_collection][agg] = all_aggs[agg_collection][agg].collect()

elapsed_time = time() - start_time

# For example
for x in all_aggs['asset']['readability']:
    print(x)


print(elapsed_time)
