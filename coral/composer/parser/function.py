import re
import math


def sign(n):
    return math.copysign(1, n)

operators = '+-*^/%().' # . for floats
valid_chars = 'abcdefghijklmnopqrstuvwxyz_'

conv_table = {
    'sin': 'math.sin',
    'cos': 'math.cos',
    'tan': 'math.tan',
    'log': 'math.log',
    'abs': 'abs',
    'trunc': 'int',
    'round': 'round',
    'sign': 'sign',
    'pi': 'math.pi',
    'e': 'math.e'
}


def parse_func(expr, whitelist, locals):
    """parses a composer expression into a function
    notes:
    - accepts only basic mathematical operators/functions & whitelisted functions
    - symbols are always separated by operators (i.e. never by whitespace)
    - must pass in the caller's `locals()` so necessary functions are there

    this is pretty hacky tbh
    """
    parsed = parse(expr, whitelist)
    src = 'def func(input): return {}'.format(parsed)
    exec(src, locals)
    return locals.pop('func')


def parse(expr, whitelist):
    """parses a composer expression"""
    # remove all whitespace
    expr = re.sub(r'\s+', '', expr)

    seq = []
    parsed = []
    for ch in expr:
        if ch in valid_chars:
            seq.append(ch)
        elif ch in operators or ch.isdigit():
            if seq:
                sym = process_sequence(seq, whitelist)
                parsed.append(sym)
                seq = []

            # power operator
            if ch == '^':
                ch = '**'

            parsed.append(ch)
        else:
            raise ValueError('Illegal character: "{}"'.format(ch))

    if seq:
        parsed.append(process_sequence(seq, whitelist))
    return ''.join(parsed)


def process_sequence(seq, whitelist):
    """processes a sequence of characters into a symbol"""
    sym = ''.join(seq)
    out = validate_symbol(sym, whitelist)
    return out


def validate_symbol(sym, whitelist):
    """validates a symbol"""
    if sym in whitelist:
        return '{}(input)'.format(sym)
    elif sym in conv_table:
        return conv_table[sym]
    else:
        raise ValueError('Illegal symbol: "{}". Is it whitelisted?'.format(sym))
