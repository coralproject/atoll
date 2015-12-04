from atoll.config import ZOOKEEPER_HOST, SPARK_BINARY

try:
    import pyspark
except ImportError:
    pyspark = None

_SPARK_CTX = None


def spark_context(pipeline_name):
    """return the app's spark context; make one if necessary"""
    global _SPARK_CTX
    if pyspark is None:
        raise ImportError('`pyspark` is required to run a distributed pipeline.')

    if _SPARK_CTX is None:
        conf = pyspark.SparkConf()
        conf.setMaster('mesos://zk://{}/mesos'.format(ZOOKEEPER_HOST))
        conf.setAppName(pipeline_name)
        conf.set('spark.executor.uri', SPARK_BINARY)
        _SPARK_CTX = pyspark.SparkContext(conf=conf)
    return _SPARK_CTX


def is_rdd(obj):
    return isinstance(obj, pyspark.rdd.RDD)
