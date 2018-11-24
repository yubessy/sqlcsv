from pytest import mark, raises

import sqlcsv.casting as casting


@mark.parametrize('spec,expected,exc', [
    ('i', int, None),
    ('int', int, None),
    ('f', float, None),
    ('float', float, None),
    ('s', str, None),
    ('str', str, None),
    ('I', int, None),
    ('other', None, ValueError),
])
def test_castfunc(spec, expected, exc):
    if not exc:
        assert casting._castfunc(spec) is expected
    else:
        with raises(exc):
            casting._castfunc(spec)


@mark.parametrize('spec,expected,exc', [
    ('t', True, None),
    ('true', True, None),
    ('1', True, None),
    ('f', False, None),
    ('false', False, None),
    ('0', False, None),
    ('T', True, None),
])
def test_nullable(spec, expected, exc):
    if not exc:
        assert casting._nullable(spec) is expected
    else:
        with raises(exc):
            casting._nullable('spec')


@mark.parametrize('types,nullables,exc', [
    ('i,f,s', 't,t,t', None),
    ('i,f,s', 't,t', AssertionError),
    ('i,f', 't,t,t', AssertionError),
])
def test_TypeCaster_init(types, nullables, exc):
    if not exc:
        casting.TypeCaster(types, nullables)
    else:
        with raises(exc):
            casting.TypeCaster(types, nullables)


@mark.parametrize('types,nullables,rows,result,exc', [
    ('i,f,s', 't,t,t', '1,1.0,aaa'.split(','), [1, 1.0, 'aaa'], None),
    ('i,f,s', 't,t,t', ',,'.split(','), [None, None, None], None),
    ('i,f,s', 'f,f,f', '1,1.0,aaa'.split(','), [1, 1.0, 'aaa'], None),
    ('i,f,s', 'f,f,f', ',,'.split(','), None, ValueError),
    ('i,f,s', 't,t,t', '1,1.0'.split(','), [1, 1.0], None),
    ('i,f,s', 't,t,t', ','.split(','), [None, None], None),
    ('i,f,s', 't,t,t', '1,1.0,aaa,xxx'.split(','), None, IndexError),
    ('i,f,s', 't,t,t', ',,,'.split(','), None, IndexError),
])
def test_TypeCaster_cast(types, nullables, rows, result, exc):
    tc = casting.TypeCaster(types, nullables)
    if not exc:
        assert tc.cast(rows) == result
    else:
        with raises(exc):
            tc.cast(rows)
