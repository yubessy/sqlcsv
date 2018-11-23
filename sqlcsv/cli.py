import csv
import sys

import click
from sqlalchemy import create_engine

from .casting import TypeCaster


def get_sql(sql, sqlfile):
    if sql is None and sqlfile is None:
        raise ValueError("Either sql or sqlfile is required")
    elif sql is None:
        sql = sqlfile.read()
        sqlfile.close()

    return sql


@click.group()
@click.option('--db-url', type=str, envvar='SQLCSV_DB_URL', required=True)
@click.option('--pre-sql', type=str, default=None)
@click.option('--header/--no-header', default=True)
@click.option('--delimiter', type=str, default=',')
@click.option('--lineterminator', type=str, default='\n')
@click.pass_context
def cli(ctx, db_url, pre_sql, header, delimiter, lineterminator):
    ctx.obj['db-url'] = db_url
    ctx.obj['pre-sql'] = pre_sql
    ctx.obj['header'] = header
    ctx.obj['delimiter'] = delimiter
    ctx.obj['lineterminator'] = lineterminator


@cli.command()
@click.option('--sql', type=str, default=None)
@click.option('--sqlfile', type=click.File('r'), default=None)
@click.option('--datafile', type=click.File('w'), default=sys.stdout)
@click.pass_context
def select(ctx, sql, sqlfile, datafile):
    engine = create_engine(ctx.obj['db-url'])
    sql = get_sql(sql, sqlfile)
    writer = csv.writer(
        datafile,
        delimiter=ctx.obj['delimiter'],
        lineterminator=ctx.obj['lineterminator'],
    )
    pre_sql = ctx.obj['pre-sql']
    header = ctx.obj['header']

    with engine.connect() as conn:
        if pre_sql:
            conn.execute(pre_sql)

        result = conn.execute(sql)

        if header:
            writer.writerow(result.keys())

        for row in result:
            writer.writerow(row)


@cli.command()
@click.option('--sql', type=str, default=None)
@click.option('--sqlfile', type=click.File('r'), default=None)
@click.option('--datafile', type=click.File('r'), default=sys.stdin)
@click.option('--types', type=str, required=True)
@click.option('--nullables', type=str, default=None)
@click.option('--date-format', type=str, default='%Y-%m-%d %H:%M:%S')
@click.pass_context
def insert(ctx, sql, sqlfile, datafile, types, nullables, date_format):
    engine = create_engine(ctx.obj['db-url'])
    sql = get_sql(sql, sqlfile)
    reader = csv.reader(
        datafile,
        delimiter=ctx.obj['delimiter'],
    )
    pre_sql = ctx.obj['pre-sql']
    header = ctx.obj['header']
    caster = TypeCaster(types, nullables, date_format)

    with engine.connect() as conn:
        if pre_sql:
            conn.execute(pre_sql)

        if header:
            next(reader)

        conn.execute(sql, *(caster.cast(row) for row in reader))


def main():
    cli(obj={})
