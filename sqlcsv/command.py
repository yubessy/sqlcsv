import csv
from contextlib import contextmanager

from sqlalchemy import create_engine

from .casting import TypeCaster


class Command:

    def __init__(self, db_url, pre_sql, post_sql, header, dialect):
        self._db_url = db_url
        self._pre_sql = pre_sql
        self._post_sql = post_sql
        self._header = header
        self._dialect = dialect

    @contextmanager
    def _connect_exec(self):
        engine = create_engine(self._db_url)

        with engine.connect() as conn:
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

    def insert(self, sql, infile, types, nullables):
        reader = csv.reader(infile, **self._dialect)
        caster = TypeCaster(types, nullables)

        with self._connect_exec() as conn:
            if self._header:
                next(reader)

            conn.execute(sql, *(caster.cast(row) for row in reader))
