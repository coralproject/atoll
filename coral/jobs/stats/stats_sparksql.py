from pyspark.sql import SQLContext
from pyspark.sql.functions import *
from time import time

sqlContext = SQLContext(sc)
df = sqlContext.read.json("comments_rdd.json")
sqlContext.registerDataFrameAsTable(df, "df")


def ARI(text):
    wc = len(text.split(" "))
    cc = len(text)
    sc = text.count(".")
    if sc == 0:
        sc = 1
    score = 0.0
    if wc > 0.0:
        score = 4.71 * (cc / wc) + 0.5 * (wc / sc) - 21.43
    return score

sqlContext.registerFunction("wc", lambda x: len(x.split(" ")))
sqlContext.registerFunction("ari", ARI)

d = sqlContext.sql("SELECT *, wc(body) as wc, ari(body) as readability FROM df")

start_time = time()

section_status = d.groupBy(d['user_id'], d['section'], d['status']).agg(mean("wc"), mean("readability"), count("is_reply"), count("has_reply"), max("date_created"), min("date_created"))
author_status = d.groupBy(d['user_id'], d['author'], d['status']).agg(mean("wc"), mean("readability"), count("is_reply"), count("has_reply"), max("date_created"), min("date_created"))
asset_status = d.groupBy(d['user_id'], d['asset_id'], d['status']).agg(mean("wc"), mean("readability"), count("is_reply"), count("has_reply"), max("date_created"), min("date_created"))
section = d.groupBy(d['user_id'], d['section']).agg(mean("wc"), mean("readability"), count("is_reply"), count("has_reply"), max("date_created"), min("date_created"))
author = d.groupBy(d['user_id'], d['author']).agg(mean("wc"), mean("readability"), count("is_reply"), count("has_reply"), max("date_created"), min("date_created"))
asset = d.groupBy(d['user_id'], d['asset_id']).agg(mean("wc"), mean("readability"), count("is_reply"), count("has_reply"), max("date_created"), min("date_created"))


section_status.show()
author_status.show()
asset_status.show()
section.show()
author.show()
asset.show()

elapsed_time = time() - start_time

print(elapsed_time)
