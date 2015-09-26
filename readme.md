# atoll
### A microservice for data analysis pipelines

## Installation

(still in development so no installation yet)

## Setup

(config options will be here)

## Usage

### Defining pipes

Custom `Pipe`s are defined like so:

```python
from atoll import Pipe

class CharacterCountPipe(Pipe):
    input = [str]
    output = [int]

    # where the magic happens
    def __call__(self, input):
        return [len(s) for s in input]
```

The `input` and `output` attributes are required. These define the pipe's input and output type signatures, which are needed for validating pipelines when they are defined. They are also used to automatically document what the pipe accepts and returns.

The type signatures are composed of regular Python types, with one main restriction. Lists and sets must be homogenous, so they can be defined with only one element type (note that a tuple can be heterogenous and acts as a "type" on its own). For example, the following type signatures are valid:

```python
input = [str]
input = set(str)
input = [(bool, int)]
```

And the following are invalid:

```python
input = [str, int]
input = [(str, str), (str, int)]
```

Lists, however, can be arbitrarily nested, assuming that the nested lists are homogenous in the same way.

For example, `[str]` encapsulates `['a', 'b', 'c']` as well as `['a', ['b', 'c']]` (this may need revisiting).

These type signatures are capable of handling custom classes, all the primitive Python types, as well as dictionaries.

### Defining pipelines

Pipelines are defined just by creating an instance of the `Pipeline` class with a list of `Pipe`s:

```python
from atoll import Pipe, Pipeline

class TokenizerPipe(Pipe):
    input = [str]
    output = [[str]]

    def __call__(self, input):
        return [s.split(' ') for s in input]

class WordCountPipe(Pipe):
    input = [[str]]
    output = [int]

    def __call__(self, input):
        return [len(s) for s in input]

pipeline = Pipeline([TokenizerPipe(), WordCountPipe()])
```

They are called just by calling the pipeline with your input data:

```python
data = [
    'Coral reefs are diverse underwater ecosystems',
    'Coral reefs are built by colonies of tiny animals'
]

pipeline(data)
# >>> [6,9]
```

#### Nested pipelines

Pipelines may also be nested in each other:

```python
class LowercasePipe(Pipe):
    input = [str]
    output = [str]

    def __call__(self, input):
        return [s.lower() for s in input]

nested_pipeline = Pipeline([LowercasePipe(), pipeline])

nested_pipeline(data)
# >>> [6,9]
```

#### Branching pipelines

Pipelines can be branched and then reduced back into a single pipeline:

```python
class VowelEndingCountPipe(Pipe):
    input = [[str]]
    output = [int]
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']

    def __call__(self, input):
        return [sum(1 if w[-1] in self.vowels else 0 for w in s) for s in input]

class PercentVowelEndingPipe(Pipe):
    input = ([int], [int])
    output = [float]

    def __call__(self, vowel_counts, word_counts):
        return [v/w for v, w in zip(vowel_counts, word_counts)]

branching_pipeline = Pipeline([
        LowercasePipe(),
        TokenizerPipe(),
        (VowelEndingCountPipe(), WordCountPipe()),
        PercentVowelEndingPipe()
])

branching_pipeline(data)
# >>> [0.333, 0.333]
```

Branches in a pipelines can be executed in parallel as well by specifying a non-zero value for `n_jobs` when creating the pipeline:

```python
branching_pipeline = Pipeline([
        LowercasePipe(),
        TokenizerPipe(),
        (VowelEndingCountPipe(), WordCountPipe()),
        PercentVowelEndingPipe()
], n_jobs=2)
```

##### Identity pipes

When branching, sometimes you want to pass some data unmodified to a pipe after the branching. Identity pipes allow you to do that.

An identity pipe is declared by using the `None` keyword in a branching segment, e.g.:

```python
class CharCountPipe(Pipe):
    input = [[str]]
    output = [[int]]

    def __call__(self, input):
        return [[len(w) for w in s] for s in input]

class CharCountWithWordPipe(Pipe):
    input = ([[int]], [[str]])
    output = [[(int, str)]]

    def __call__(self, charcounts, wordlists):
        return [list(zip(counts, words)) for counts, words in zip(charcounts, wordlists)]

branching_pipeline = Pipeline([
        LowercasePipe(),
        TokenizerPipe(),
        (CharCountPipe(), None), # The output of TokenizerPipe will also be passed to CharCountWithWordPipe
        CharCountWithWordPipe()
])

branching_pipeline(data)
# >>> [[(5, 'coral'), (5, 'reefs'), (3, 'are'), (7, 'diverse'), (10, 'underwater'), (10, 'ecosystems')],
#      [(5, 'coral'), (5, 'reefs'), (3, 'are'), (5, 'built'), (2, 'by'), (8, 'colonies'), (2, 'of'), (4, 'tiny'), (7, 'animals')]]
```

#### Naming pipelines

It's a best practice to name your pipelines something descriptive so you know what it does:

```python
pipeline = Pipeline([
        LowercasePipe(),
        TokenizerPipe(),
        (VowelEndingCountPipe(), WordCountPipe()),
        PercentVowelEndingPipe()
], name='Percent vowel endings pipeline')
```

### The microservice

A simple microservice server is included which allows you to post data to your pipelines from elsewhere.

You can register your own pipelines using the provided `register_pipeline` function:

```python
from atoll import register_pipeline
register_pipeline('/percent_vowel_endings', pipeline)
```

Then you can post data in the proper format (as a JSON object with your data at the `data` key) to that endpoint, which will be at `/pipelines/percent_vowel_endings`:

```
curl -X POST -H "Content-Type: application/json" -d '{"data": ["this is a test", "another test"]}' http://localhost:5001/pipelines/percent_vowel_endings
# {"results": [0.25, 0]}
```

(Assuming you are running the microservice locally on port 5001)

True asynchronous support has not yet been added yet, but you can additionally specify a callback url to run the task asynchronously:

```
curl -X POST -H "Content-Type: application/json" -d '{"data": ["this is a test", "another test"], "callback": "http://mysite.com/callback"}' http://localhost:5001/pipelines/percent_vowel_endings
# {"results": [0.25, 0]} will be POSTed to the callback url
```
