from atoll import Pipeline


def double(x):
    return 2 * x

inputs = [1,2,3,4]

pipeline1 = Pipeline(name='example_pipeline_1').map(double)
results = pipeline1(inputs)
assert results == [2,4,6,8]

pipeline2 = Pipeline(name='example_pipeline_2').map(double).map(double)
results = pipeline2(inputs)
assert results == [4,8,12,16]

pipeline3 = Pipeline(name='example_pipeline_3').fork(pipeline1, pipeline2)
results = pipeline3(inputs)
assert results == ([2,4,6,8], [4,8,12,16])


def extend_list(x):
    return x + x

inputs = [[1,2,3],[4,5,6]]

pipeline4 = Pipeline(name='example_pipeline_4').flatMap(extend_list)
results = pipeline4(inputs)
assert results == [1,2,3,1,2,3,4,5,6,4,5,6]

pipeline5 = Pipeline(name='example_pipeline_5').map(sum)
results = pipeline5(inputs)
assert results == [6,15]

def add(x, y):
    return x + y

pipeline6 = Pipeline(name='example_pipeline_6').flatMap(extend_list).reduce(add)
results = pipeline6(inputs)
assert results == 42


data = {'a': 1, 'b': 2, 'c': 3}
inputs = list(data.items())
pipeline7 = Pipeline(name='example_pipeline_7').mapValues(double)
results = pipeline7(inputs)
results = sorted(results, key=lambda x: x[0]) # to make the assertion consistent
assert results == [('a', 2), ('b', 4), ('c', 6)]


def make_pairs(x):
    return [x, 2*x]

pipeline8 = Pipeline(name='example_pipeline_8').flatMapValues(make_pairs)
results = pipeline8(inputs)
results = sorted(results, key=lambda x: x[0]) # to make the assertion consistent
assert results == [('a', 1), ('a', 2), ('b', 2), ('b', 4), ('c', 3), ('c', 6)]


def half(x):
    return 'half', x/2

def quarter(x):
    return 'quarter', x/4

inputs = [1,2,3,4]
pipeline9 = Pipeline(name='example_pipeline_9').forkMap(half, quarter)
results = pipeline9(inputs)
assert results == ([('half', 0.5), ('half', 1.0), ('half', 1.5), ('half', 2.0)], [('quarter', 0.25), ('quarter', 0.5), ('quarter', 0.75), ('quarter', 1.0)])

pipeline10 = Pipeline(name='example_pipeline_10').forkMap(half, quarter).flatMap().reduceByKey(add)
results = pipeline10(inputs)
assert results == [('quarter', 2.5), ('half', 5.0)]