from io import StringIO
from unittest.mock import patch

from pytest import fixture
from sqlalchemy import create_engine

import sqlcsv.command


@fixture
def db():
    engine = create_engine('sqlite://')
    engine.execute('''
        CREATE TABLE testtable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            int_col INTEGER,
            real_col REAL,
            text_col TEXT
        );
    ''')

    with patch('sqlcsv.command.create_engine', lambda any_url: engine):
        yield engine

    engine.execute('''
        DROP TABLE testtable;
    ''')


@fixture
def select_all_sql():
    return '''
        SELECT * FROM testtable;
    '''


@fixture
def insert_one_sql():
    return '''
        INSERT INTO testtable(int_col, real_col, text_col)
        VALUES (1, 1.0, 'aaa');
    '''


@fixture
def insert_placeholder_sql():
    return '''
        INSERT INTO testtable(int_col, real_col, text_col)
        VALUES (?, ?, ?);
    '''


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


def test_connect_exec(db, command_args, select_all_sql):
    cmd = sqlcsv.command.Command(**command_args)
    with cmd._connect_exec() as conn:
        result = conn.execute(select_all_sql).fetchall()
        assert result == []


def test_connect_exec_with_transaction(db, command_args, insert_one_sql, select_all_sql):
    command_args['transaction'] = True
    cmd = sqlcsv.command.Command(**command_args)
    try:
        with cmd._connect_exec() as conn:
            conn.execute(insert_one_sql)
            raise Exception('An error')
    except Exception:
        pass

    result = db.execute(select_all_sql).fetchall()
    assert result == []


def test_connect_exec_without_transaction(db, command_args, insert_one_sql, select_all_sql):
    cmd = sqlcsv.command.Command(**command_args)
    try:
        with cmd._connect_exec() as conn:
            conn.execute(insert_one_sql)
            raise Exception('An error')
    except Exception:
        pass

    result = db.execute(select_all_sql).fetchall()
    assert result == [(1, 1, 1.0, 'aaa')]


def test_connect_exec_pre_sql(db, command_args, insert_one_sql, select_all_sql):
    command_args['pre_sql'] = insert_one_sql
    cmd = sqlcsv.command.Command(**command_args)
    with cmd._connect_exec() as conn:
        result = conn.execute(select_all_sql).fetchall()
        assert result == [(1, 1, 1.0, 'aaa')]


def test_connect_exec_post_sql(db, command_args, insert_one_sql, select_all_sql):
    command_args['post_sql'] = insert_one_sql
    cmd = sqlcsv.command.Command(**command_args)
    with cmd._connect_exec() as conn:
        result = conn.execute(select_all_sql).fetchall()
        assert result == []

    result = db.execute(select_all_sql).fetchall()
    assert result == [(1, 1, 1.0, 'aaa')]


def test_select(db, command_args, insert_one_sql, select_all_sql):
    db.execute(insert_one_sql)

    outfile = StringIO()
    cmd = sqlcsv.command.Command(**command_args)
    cmd.select(select_all_sql, outfile)
    outfile.seek(0)
    assert outfile.read() == 'id,int_col,real_col,text_col\n1,1,1.0,aaa\n'


def test_select_no_header(db, command_args, insert_one_sql, select_all_sql):
    db.execute(insert_one_sql)

    outfile = StringIO()
    command_args['header'] = False
    cmd = sqlcsv.command.Command(**command_args)
    cmd.select(select_all_sql, outfile)
    outfile.seek(0)
    assert outfile.read() == '1,1,1.0,aaa\n'


def test_insert(db, command_args, insert_placeholder_sql, select_all_sql):
    infile = StringIO('int_col,real_col,text_col\n1,1.0,aaa\n')
    types = [int, float, str]
    nullables = [False, False, False]
    cmd = sqlcsv.command.Command(**command_args)
    cmd.insert(insert_placeholder_sql, infile, types, nullables)

    result = db.execute(select_all_sql).fetchall()
    assert result == [(1, 1, 1.0, 'aaa')]


def test_insert_no_header(db, command_args, insert_placeholder_sql, select_all_sql):
    infile = StringIO('1,1.0,aaa\n')
    types = [int, float, str]
    nullables = [False, False, False]
    command_args['header'] = False
    cmd = sqlcsv.command.Command(**command_args)
    cmd.insert(insert_placeholder_sql, infile, types, nullables)

    result = db.execute(select_all_sql).fetchall()
    assert result == [(1, 1, 1.0, 'aaa')]


def test_insert_nullable(db, command_args, insert_placeholder_sql, select_all_sql):
    infile = StringIO('int_col,real_col,text_col\n,,\n')
    types = [int, float, str]
    nullables = [True, True, True]
    cmd = sqlcsv.command.Command(**command_args)
    cmd.insert(insert_placeholder_sql, infile, types, nullables)

    result = db.execute(select_all_sql).fetchall()
    assert result == [(1, None, None, None)]
