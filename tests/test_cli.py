from io import StringIO
from pytest import mark, raises

import sqlcsv.cli as cli


@mark.parametrize('sql,sqlfile,expected,exc', [
    ('SELECT 1;', None, 'SELECT 1;', None),
    (None, StringIO('SELECT 2;'), 'SELECT 2;', None),
    (None, None, None, ValueError),
    ('SELECT 1;', StringIO('SELECT 2;'), None, ValueError),
])
def test_get_sql(sql, sqlfile, expected, exc):
    if not exc:
        assert cli._get_sql(sql, sqlfile) == expected
    else:
        with raises(exc):
            cli._get_sql(sql, sqlfile)


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
def test_flag_to_type(spec, expected, exc):
    if not exc:
        assert cli._flag_to_type(spec) is expected
    else:
        with raises(exc):
            cli._flag_to_type(spec)


@mark.parametrize('spec,expected,exc', [
    ('t', True, None),
    ('true', True, None),
    ('1', True, None),
    ('f', False, None),
    ('false', False, None),
    ('0', False, None),
    ('T', True, None),
    ('other', None, ValueError),
])
def test_flag_to_bool(spec, expected, exc):
    if not exc:
        assert cli._flag_to_bool(spec) is expected
    else:
        with raises(exc):
            cli._flag_to_bool(spec)
