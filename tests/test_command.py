from io import StringIO
from unittest.mock import patch

from pytest import fixture
from sqlalchemy import create_engine

import sqlcsv.command


SQL_CREATE_TABLE = '''
    CREATE TABLE testtable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        int_col INTEGER,
        real_col REAL,
        text_col TEXT
    );
'''
SQL_DROP_TABLE = '''
    DROP TABLE testtable;
'''
SQL_SELECT_ALL = '''
    SELECT * FROM testtable;
'''
SQL_INSERT_ONE = '''
    INSERT INTO testtable(int_col, real_col, text_col)
    VALUES (1, 1.0, 'aaa');
'''
SQL_INSERT_PLACEHOLDER = '''
    INSERT INTO testtable(int_col, real_col, text_col)
    VALUES (?, ?, ?);
'''


@fixture
def db():
    engine = create_engine('sqlite://')
    engine.execute(SQL_CREATE_TABLE)

    with patch('sqlcsv.command.create_engine', lambda any_url: engine):
        yield engine

    engine.execute(SQL_DROP_TABLE)


@fixture
def command_args():
    return dict(
        db_url='sqlite://',
        pre_sql=None,
        post_sql=None,
        transaction=False,
        header=True,
        dialect=dict(
            lineterminator='\n',
        ),
    )


def test_connect_exec(db, command_args):
    cmd = sqlcsv.command.Command(**command_args)
    with cmd._connect_exec() as conn:
        result = conn.execute(SQL_SELECT_ALL).fetchall()
        assert result == []


def test_connect_exec_with_transaction(db, command_args):
    command_args['transaction'] = True
    cmd = sqlcsv.command.Command(**command_args)
    try:
        with cmd._connect_exec() as conn:
            conn.execute(SQL_INSERT_ONE)
            raise Exception('An error')
    except Exception:
        pass

    result = db.execute(SQL_SELECT_ALL).fetchall()
    assert result == []


def test_connect_exec_without_transaction(db, command_args):
    cmd = sqlcsv.command.Command(**command_args)
    try:
        with cmd._connect_exec() as conn:
            conn.execute(SQL_INSERT_ONE)
            raise Exception('An error')
    except Exception:
        pass

    result = db.execute(SQL_SELECT_ALL).fetchall()
    assert result == [(1, 1, 1.0, 'aaa')]


def test_connect_exec_pre_sql(db, command_args):
    command_args['pre_sql'] = SQL_INSERT_ONE
    cmd = sqlcsv.command.Command(**command_args)
    with cmd._connect_exec() as conn:
        result = conn.execute(SQL_SELECT_ALL).fetchall()
        assert result == [(1, 1, 1.0, 'aaa')]


def test_connect_exec_post_sql(db, command_args):
    command_args['post_sql'] = SQL_INSERT_ONE
    cmd = sqlcsv.command.Command(**command_args)
    with cmd._connect_exec() as conn:
        result = conn.execute(SQL_SELECT_ALL).fetchall()
        assert result == []

    result = db.execute(SQL_SELECT_ALL).fetchall()
    assert result == [(1, 1, 1.0, 'aaa')]


def test_select(db, command_args):
    db.execute(SQL_INSERT_ONE)

    outfile = StringIO()
    cmd = sqlcsv.command.Command(**command_args)
    cmd.select(SQL_SELECT_ALL, outfile)
    outfile.seek(0)
    assert outfile.read() == 'id,int_col,real_col,text_col\n1,1,1.0,aaa\n'


def test_select_no_header(db, command_args):
    db.execute(SQL_INSERT_ONE)

    outfile = StringIO()
    command_args['header'] = False
    cmd = sqlcsv.command.Command(**command_args)
    cmd.select(SQL_SELECT_ALL, outfile)
    outfile.seek(0)
    assert outfile.read() == '1,1,1.0,aaa\n'


def test_insert(db, command_args):
    infile = StringIO('int_col,real_col,text_col\n1,1.0,aaa\n')
    types = [int, float, str]
    nullables = [False, False, False]
    cmd = sqlcsv.command.Command(**command_args)
    cmd.insert(SQL_INSERT_PLACEHOLDER, infile, types, nullables)

    result = db.execute(SQL_SELECT_ALL).fetchall()
    assert result == [(1, 1, 1.0, 'aaa')]


def test_insert_no_header(db, command_args):
    infile = StringIO('1,1.0,aaa\n')
    types = [int, float, str]
    nullables = [False, False, False]
    command_args['header'] = False
    cmd = sqlcsv.command.Command(**command_args)
    cmd.insert(SQL_INSERT_PLACEHOLDER, infile, types, nullables)

    result = db.execute(SQL_SELECT_ALL).fetchall()
    assert result == [(1, 1, 1.0, 'aaa')]


def test_insert_nullable(db, command_args):
    infile = StringIO('int_col,real_col,text_col\n,,\n')
    types = [int, float, str]
    nullables = [True, True, True]
    cmd = sqlcsv.command.Command(**command_args)
    cmd.insert(SQL_INSERT_PLACEHOLDER, infile, types, nullables)

    result = db.execute(SQL_SELECT_ALL).fetchall()
    assert result == [(1, None, None, None)]
