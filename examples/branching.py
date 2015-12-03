from atoll import Pipe, Pipeline

data = [
    'Coral reefs are diverse underwater ecosystems',
    'Coral reefs are built by colonies of tiny animals'
]

class TokenizerPipe(Pipe):
    input = [str]
    output = [[str]]

    def __call__(self, input):
        return [s.split(' ') for s in input]

class LowercasePipe(Pipe):
    input = [str]
    output = [str]

    def __call__(self, input):
        return [s.lower() for s in input]

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
        (CharCountPipe(), None),
        CharCountWithWordPipe()
])

print(branching_pipeline(data))
