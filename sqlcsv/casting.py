class TypeCaster:

    def __init__(self, types, nullables):
        self._types = types
        if nullables:
            assert len(types) == len(nullables)
            self._nullables = nullables
        else:
            self._nullables = [False] * len(types)

    def _cast_ith(self, i, val):
        if self._nullables[i] and not val:
            return None
        else:
            return self._types[i](val)

    def cast(self, row):
        return [self._cast_ith(i, v) for i, v in enumerate(row)]
