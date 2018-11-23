import csv

import click
from sqlalchemy import create_engine

from .casting import TypeCaster


@click.group()
@click.option('--db-url', type=str, required=True)
@click.pass_context
def cli(ctx, db_url):
    ctx.obj['engine'] = create_engine(db_url)


@cli.command()
@click.argument('sql-file', type=click.File('r'))
@click.argument('out-file', type=click.File('w'))
@click.pass_context
def select(ctx, sql_file, out_file):
    sql = sql_file.read()
    sql_file.close()
    writer = csv.writer(out_file, lineterminator='\n')

    engine = ctx.obj['engine']
    result = engine.execute(sql)
    writer.writerow(result.keys())
    for row in result:
        writer.writerow(row)


@cli.command()
@click.option('--types', type=str, required=True)
@click.option('--nullables', type=str, default=None)
@click.option('--date-format', type=str, default='%Y-%m-%d %H:%M:%S')
@click.argument('sql-file', type=click.File('r'))
@click.argument('in-file', type=click.File('r'))
@click.pass_context
def insert(ctx, types, nullables, date_format, sql_file, in_file):
    sql = sql_file.read()
    sql_file.close()
    reader = csv.reader(in_file)

    caster = TypeCaster(types, nullables, date_format)

    engine = ctx.obj['engine']
    next(reader)
    engine.execute(sql, *(caster.cast(row) for row in reader))


def main():
    cli(obj={})
