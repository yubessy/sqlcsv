from pytest import mark, raises

import sqlcsv.casting as casting


@mark.parametrize('types,nullables,exc', [
    ([int, float, str], [True, True, True], None),
    ([int, float, str], [True, True], AssertionError),
    ([int, float], [True, True, True], AssertionError),
])
def test_TypeCaster_init(types, nullables, exc):
    if not exc:
        casting.TypeCaster(types, nullables)
    else:
        with raises(exc):
            casting.TypeCaster(types, nullables)


@mark.parametrize('types,nullables,rows,result,exc', [
    ([int, float, str], [True, True, True], '1,1.0,aaa'.split(','), [1, 1.0, 'aaa'], None),
    ([int, float, str], [False, False, False], '1,1.0,aaa'.split(','), [1, 1.0, 'aaa'], None),
    ([int, str], [True, True], ','.split(','), [None, None], None),
    ([int, str], [False, False], ','.split(','), None, ValueError),
    ([int, str], [True, True], '1'.split(','), [1], None),
    ([int, str], [True, True], ''.split(','), [None], None),
    ([int, str], [True, True], '1,aaa,xxx'.split(','), None, IndexError),
    ([int, str], [True, True], ',,'.split(','), None, IndexError),
])
def test_TypeCaster_cast(types, nullables, rows, result, exc):
    tc = casting.TypeCaster(types, nullables)
    if not exc:
        assert tc.cast(rows) == result
    else:
        with raises(exc):
            tc.cast(rows)
