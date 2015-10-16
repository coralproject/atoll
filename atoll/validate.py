import six
import types
from hashlib import md5
from collections import namedtuple


class t:
    """
    Special types
    """
    any = types.new_class('any')
    self = types.new_class('self') # Recursion


def build_tree(input):
    """
    Expand a type signature into a tree of type nodes
    """
    typ = type(input)

    # support for old-style py2 classes
    if typ is type or (six.PY2 and typ is types.ClassType):
        return TypeNode(input)

    elif typ in [list, set]:
        l = len(input)
        if l == 1:
            ch = next(iter(input))
            return TypeNode(typ, ch=[build_tree(ch)])
        elif l == 0:
            raise TypeError('You must specify the element type of lists and sets')
        else:
            raise TypeError('Lists and sets can have only one element type')

    elif typ is tuple:
        if len(input) == 0:
            raise TypeError('You must specify the element type(s) of tuples')
        return TypeNode(typ, ch=[build_tree(ch) for ch in input])

    elif typ is dict:
        return TypeNode(_dict_to_struct(input), struct=True)

    else:
        raise TypeError('Unsupported type: {}'.format(typ))


def _dict_to_struct(dct):
    """
    Convert a dictionary into a pseudo-struct,
    which is an instance of a named tuple mapping keys to type nodes
    """
    # build the namedtuple to represent the 'struct'
    keys = [k for k in dct.keys()]
    hash = md5('__'.join(keys).encode('utf-8')).hexdigest()
    type_name = 't{}'.format(hash)
    typ = namedtuple(type_name, keys)

    # recurse and convert to type nodes
    _dct = {}
    for k, v in dct.items():
        _dct[k] = build_tree(v) if type(v) != dict else TypeNode(_dict_to_struct(v), struct=True)

    # the 'struct' is actually an instance of the namedtuple
    # where its attributes are type nodes
    struct = typ(**_dct)
    return struct


class TypeNode():
    def __init__(self, typ, ch=[], struct=False):
        self.type = typ
        self.children = ch
        self.struct = struct

    def accepts(self, other):
        """Whether `self` can accept input from `other`"""
        if self.struct and other.struct:
            other_dict = other.type._asdict()
            return all(p in other_dict for p in self.type._asdict())
        else:
            if not self.sim(other):
                return False
            return all(ch.accepts(ch_other) for ch, ch_other in zip(self.children, other.children))

    def sim(self, other):
        """Checks for 'similarity', if the node types are equal but does not check their children"""
        if self.type != other.type:
            return False
        if len(self.children) != len(other.children):
            return False
        return True

    def __eq__(self, other):
        """Checks for exact equality (symmetric)"""
        if not self.sim(other):
            return False
        return all(ch == ch_other for ch, ch_other in zip(self.children, other.children))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        indent = '  '
        if self.struct:
            # namedtuple (pseudo-struct)
            # reconstruct into dict form
            pstruct = self.type
            kvs = []
            for attr in pstruct._fields:
                val = getattr(pstruct, attr)
                val_parts = str(val).split('\n')
                val_repr = ('\n' + indent).join(val_parts)
                field = '"{}": {}'.format(attr, val_repr)
                kvs.append(field)
            kvs = indent + ('\n' + indent).join(kvs)
            return '\n'.join(['{', kvs, '}'])

        elif self.type in [list, set]:
            schar, echar = ('[', ']') if self.type is list else ('{', '}')

            # lists and sets only ever have one child
            ch = self.children[0]
            if ch.type == tuple:
                ch_parts = str(ch).split('\n')
                ch_s, ch_e = ch_parts[0].strip(), ch_parts[-1].strip()
                ch = indent + ('\n'+indent).join(ch_parts[1:-1])
                return '\n'.join([schar + ch_s, ch, ch_e + echar])
            else:
                return ''.join([schar, str(ch), echar])

        elif self.type == tuple:
            ch = indent + ('\n' + indent).join([str(c) for c in self.children])
            return '\n'.join(['(', ch, ')'])

        # special recursive case
        elif self.type == 'self':
            return 'self'

        else:
            return self.type.__name__
