import os
import yaml

try:
    import pyspark
except ImportError:
    pyspark = None

CONF_BASE = '/etc/atoll/conf'
DISTRIB_CONF = {
    # this must be a _prebuilt_ spark archive, i.e. a spark binary package
    # you can build it and host it yourself if you like.
    'spark_binary': 'http://d3kbcqa49mib13.cloudfront.net/spark-1.5.0-bin-hadoop2.6.tgz',
    'zookeeper_host': '172.17.0.1:2181'
}

service_conf_path = os.path.join(CONF_BASE, 'distrib.yaml')
if os.path.exists(service_conf_path):
    with open(service_conf_path, 'r') as f:
        DISTRIB_CONF.update(yaml.load(f))

_SPARK_CTX = None

def spark_context(pipeline_name):
    global _SPARK_CTX
    if pyspark is None:
        raise ImportError('`pyspark` is required to run a distributed pipeline.')

    if _SPARK_CTX is None:
        conf = pyspark.SparkConf()
        conf.setMaster('mesos://zk://{}/mesos'.format(DISTRIB_CONF['zookeeper_host']))
        conf.setAppName(pipeline_name)
        conf.set('spark.executor.uri', DISTRIB_CONF['spark_binary'])
        _SPARK_CTX = pyspark.SparkContext(conf=conf)
    return _SPARK_CTX


def is_rdd(obj):
    return isinstance(obj, pyspark.rdd.RDD)
