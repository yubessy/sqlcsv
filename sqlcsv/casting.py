def _castfunc(spec):
    spec = spec.lower()
    if spec in ('i', 'int'):
        return int
    elif spec in ('f', 'float'):
        return float
    elif spec in ('s', 'str'):
        return str
    else:
        raise ValueError("Unknown type spec '{}'".format(spec))


def _nullable(spec):
    spec = spec.lower()
    if spec in ('t', 'true', '1'):
        return True
    elif spec in ('f', 'false', '0'):
        return False
    else:
        raise ValueError("Unknown nullable spec '{}'".format(spec))


class TypeCaster:

    def __init__(self, types, nullables):
        self._castfuncs = tuple(_castfunc(t) for t in types)
        if nullables:
            assert len(types) == len(nullables)
            self._nullables = tuple(_nullable(n) for n in nullables)
        else:
            self._nullables = tuple([False] * len(types))

    def _cast_ith(self, i, val):
        if self._nullables[i] and not val:
            return None
        else:
            return self._castfuncs[i](val)

    def cast(self, row):
        return [self._cast_ith(i, v) for i, v in enumerate(row)]
