import csv

import click
from sqlalchemy import create_engine

from .casting import TypeCaster


@click.group()
@click.option('--db-url', type=str, required=True)
@click.option('--header/--no-header', default=True)
@click.option('--delimiter', type=str, default=',')
@click.pass_context
def cli(ctx, db_url, header, delimiter):
    ctx.obj['db-url'] = db_url
    ctx.obj['header'] = header
    ctx.obj['delimiter'] = delimiter


@cli.command()
@click.option('--lineterminator', type=str, default='\n')
@click.argument('sqlfile', type=click.File('r'))
@click.argument('csvfile', type=click.File('w'))
@click.pass_context
def select(ctx, lineterminator, sqlfile, csvfile):
    sql = sqlfile.read()
    sqlfile.close()
    writer = csv.writer(
        csvfile=csvfile,
        delimiter=ctx.obj['delimiter'],
        lineterminator=lineterminator,
    )
    engine = create_engine(ctx.obj['db-url'])

    result = engine.execute(sql)
    if ctx.obj['header']:
        writer.writerow(result.keys())
    for row in result:
        writer.writerow(row)


@cli.command()
@click.option('--types', type=str, required=True)
@click.option('--nullables', type=str, default=None)
@click.option('--date-format', type=str, default='%Y-%m-%d %H:%M:%S')
@click.argument('sqlfile', type=click.File('r'))
@click.argument('csvfile', type=click.File('r'))
@click.pass_context
def insert(ctx, types, nullables, date_format, sqlfile, csvfile):
    sql = sqlfile.read()
    sqlfile.close()
    reader = csv.reader(
        csvfile=csvfile,
        delimiter=ctx.obj['delimiter'],
    )
    engine = create_engine(ctx.obj['db-url'])

    caster = TypeCaster(types, nullables, date_format)

    if ctx.obj['header']:
        next(reader)
    engine.execute(sql, *(caster.cast(row) for row in reader))


def main():
    cli(obj={})
