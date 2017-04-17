import math
from coral.metrics.readability.utils import *
from coral.metrics.readability import Readability
import pika
import json
import os
import statsd
import sys

#
#  Usage:
#     python commentListener.py
#
#  Subscribes to Coral RabbitMQ messages, filters for comments,
#  validates messages, and calculates metrics on the text.
#

# Constants
COMMENT_EVENT = 'comment_import'

# Get some standard coral environment vars
try:
    rmq_user = os.environ['RABBITMQ_DEFAULT_USER']
    rmq_pass = os.environ['RABBITMQ_DEFAULT_PASS']
    rmq_host = os.environ['RABBITMQ_HOST']
    rmq_port = int(os.environ['RABBITMQ_PORT'])
    rmq_exchange = os.environ['AMQP_EXCHANGE']
    statsd_host = os.environ['STATSD_HOST']
    statsd_port = int(os.environ['STATSD_PORT'])

    # For mongo integration
    #mongo_db = os.environ['DBNAME']
    #mongo_host = os.environ['MONGODB_HOST']
except Exception as err:
    print("ERROR: Environment variable not found. " + err, file=sys.stderr)
    exit(1)

# Connect to Statsd
try:
    stat = statsd.StatsClient(statsd_host, statsd_port, prefix='atoll')
except Exception as err:
    print("WARNING: Could not connect to statsd. " + str(err), file=sys.stderr)

# Connect to RabbitMQ
try:
    credentials = pika.PlainCredentials(rmq_user, rmq_pass)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        rmq_host, rmq_port, '/', credentials))
except Exception as err:
    print("ERROR: Could not connect to RabbitMQ. " + str(err), file=sys.stderr)
    exit(1)

# Connect to Pillar exchange
try:
    channel = connection.channel()
    channel.exchange_declare(exchange=rmq_exchange,
                             type='fanout',
                             durable=True)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=rmq_exchange, queue=queue_name)
except Exception as err:
    print("ERROR: Could not connect to Pillar RabbitMQ exchange. " + str(err),
          file=sys.stderr)
    exit(1)

# Declare callback for each message
def callback(channel, method, properties, body):
    message_json = body.decode("utf-8")
    message = json.loads(message_json)

    # Check to see if the message is valid
    if 'name' in message:
        # Is it a comment?
        if isComment(message):
            # Validate comment
            valid, error = isValid(message)
            if valid:
                # Get comment text
                comment = message['payload']['body']
                # Get readability scores
                r = Readability(comment)
                readability_json = formatReadability(r)
                # For now print out message and readability
                print(readability_json.strip(), end="\t")
                print(message_json)
                # Increment stat
                stat.incr('readability', count=1, rate=1.0)
            else:
                print(error, file=sys.stderr)
                stat.incr('error', count=1, rate=1.0)
    else:
        print("UNKNOWN FORMAT: name field not found. " + json.dumps(message))
        stat.incr('unknown_format', count=1, rate=1.0)


# Assumes validated message (name exists)
def isComment(message):
    if message['name'] == COMMENT_EVENT:
        return True
    else:
        return False


def formatReadability(r):
    return json.dumps({
        'ari': r.ARI(),
        'flesch_reading_ease': r.FleschReadingEase(),
        'flesch_kincaid_grade_level': r.FleschKincaidGradeLevel(),
        'gunning_fog_index': r.GunningFogIndex(),
        'smog_index': r.SMOGIndex(),
        'coleman_liau_index': r.ColemanLiauIndex(),
        'lix': r.LIX(),
        'rix': r.RIX()
    })


def isValid(message):
    if 'payload' in message:
        if 'body' in message['payload']:
            return (True, "")
        else:
            stat.incr('unknown_format', count=1, rate=1.0)
            return (False, "UNKNOWN FORMAT: body field not found. " +
                json.dumps(message))
    else:
        stat.incr('unknown_format', count=1, rate=1.0)
        return (False, "UNKNOWN FORMAT: payload field not found. " +
            json.dumps(message))

# Consume messages
channel.basic_consume(callback, queue='', no_ack=True)
channel.start_consuming()
connection.close()

