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
@click.option('-u', '--db-url', type=str, envvar='SQLCSV_DB_URL', required=True)
@click.option('-H', '--no-header', is_flag=True)
@click.option('-d', '--delimiter', type=str, default=None)
@click.option('-T', '--tab', is_flag=True)
@click.option('-l', '--lineterminator', type=str, default='\n')
@click.option('-p', '--pre-sql', type=str, default=None)
@click.pass_context
def cli(ctx, db_url, no_header, delimiter, tab, lineterminator, pre_sql):
    ctx.obj['db-url'] = db_url
    ctx.obj['header'] = not no_header
    ctx.obj['delimiter'] = delimiter or ('\t' if tab else ',')
    ctx.obj['lineterminator'] = lineterminator
    ctx.obj['pre-sql'] = pre_sql


@cli.command()
@click.option('-s', '--sql', type=str, default=None)
@click.option('-f', '--sqlfile', type=click.File('r'), default=None)
@click.option('-o', '--outfile', type=click.File('w'), default=sys.stdout)
@click.pass_context
def select(ctx, sql, sqlfile, outfile):
    engine = create_engine(ctx.obj['db-url'])
    sql = get_sql(sql, sqlfile)
    writer = csv.writer(
        outfile,
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
@click.option('-s', '--sql', type=str, default=None)
@click.option('-f', '--sqlfile', type=click.File('r'), default=None)
@click.option('-i', '--infile', type=click.File('r'), default=sys.stdin)
@click.option('-t', '--types', type=str, required=True)
@click.option('-n', '--nullables', type=str, default=None)
@click.option('-m', '--date-format', type=str, default='%Y-%m-%d %H:%M:%S')
@click.pass_context
def insert(ctx, sql, sqlfile, infile, types, nullables, date_format):
    engine = create_engine(ctx.obj['db-url'])
    sql = get_sql(sql, sqlfile)
    reader = csv.reader(
        infile,
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
