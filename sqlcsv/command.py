import csv
from contextlib import contextmanager
from itertools import islice

from sqlalchemy import create_engine

from .casting import TypeCaster


def chunker(iterable, size):
    if size <= 0:
        raise ValueError('Chunk size must be greater than 0')

    it = iter(iterable)
    chunk = tuple(islice(it, size))
    while chunk:
        yield chunk
        chunk = tuple(islice(it, size))


class Command:

    def __init__(self, db_url, pre_sql, post_sql, transaction, header, dialect):
        self._db_url = db_url
        self._pre_sql = pre_sql
        self._post_sql = post_sql
        self._transaction = transaction
        self._header = header
        self._dialect = dialect

    @contextmanager
    def _connect_exec(self):
        if not self._db_url:
            raise ValueError('Database connection URL is not set')

        engine = create_engine(self._db_url)

        with engine.begin() if self._transaction else engine.connect() as conn:
            if self._pre_sql:
                conn.execute(self._pre_sql)

            yield conn

            if self._post_sql:
                conn.execute(self._post_sql)

    def select(self, sql, outfile):
        writer = csv.writer(outfile, **self._dialect)

        with self._connect_exec() as conn:
            result = conn.execute(sql)

            if self._header:
                writer.writerow(result.keys())

            for row in result:
                writer.writerow(row)

    def insert(self, sql, infile, types, nullables, chunk_size):
        reader = csv.reader(infile, **self._dialect)
        caster = TypeCaster(types, nullables)

        with self._connect_exec() as conn:
            if self._header:
                next(reader)

            if chunk_size is not None:
                for chunk in chunker(reader, chunk_size):
                    conn.execute(sql, *map(caster.cast, chunk))
            else:
                conn.execute(sql, *map(caster.cast, reader))
