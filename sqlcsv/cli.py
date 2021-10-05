import csv
import gzip
import os

import click

from .command import Command

QUOTING = {
    'ALL': csv.QUOTE_ALL,
    'MINIMAL': csv.QUOTE_MINIMAL,
    'NONNUMERIC': csv.QUOTE_NONNUMERIC,
    'NONE': csv.QUOTE_NONE,
}


def _get_sql(sql, sqlfile):
    if sql is None and sqlfile is None:
        raise ValueError("Either sql or sqlfile is required")
    elif sql is not None and sqlfile is not None:
        raise ValueError("Either only sql or sqlfile can be specified")

    if sql is None:
        sql = sqlfile.read()
        sqlfile.close()

    return sql


def _flag_to_type(spec):
    spec = spec.lower()
    if spec in ('i', 'int'):
        return int
    elif spec in ('f', 'float'):
        return float
    elif spec in ('s', 'str'):
        return str
    else:
        raise ValueError("Unknown type spec '{}'".format(spec))


def _flag_to_bool(spec):
    spec = spec.lower()
    if spec in ('t', 'true', '1'):
        return True
    elif spec in ('f', 'false', '0'):
        return False
    else:
        raise ValueError("Unknown nullable spec '{}'".format(spec))


def _open(filename, mode="rt"):
    if os.path.splitext(filename)[1] == ".gz":
        return gzip.open(filename, mode)
    else:
        return click.open_file(filename, mode)


@click.group()
@click.option('-u', '--db-url', envvar='SQLCSV_DB_URL',
              help='Datasbase connection URL.')
@click.option('-p', '--pre-sql', default=None,
              help='SQL to be run before main operation.')
@click.option('-P', '--post-sql', default=None,
              help='SQL to be run after main operation.')
@click.option('-X', '--transaction', is_flag=True,
              help='If set, run queries in a transaction.')
@click.option('-H', '--no-header', is_flag=True,
              help='(CSV dialect) If set, do not output header line (select) and also treat input as not having header line (insert).')  # noqa
@click.option('-T', '--tab', is_flag=True,
              help='(CSV dialect) If set, input or output will be tab-separated (TSV).')
@click.option('-d', '--delimiter', default=',',
              help='(CSV dialect) Column delimiter char.')
@click.option('-l', '--lineterminator', default='\n',
              help='(CSV dialect) Line terminator char.')
@click.option('-Q', '--quoting', type=click.Choice(QUOTING.keys(), case_sensitive=False), default='MINIMAL',  # noqa
              help='(CSV dialect) Quoting mode.')
@click.option('-q', '--quotechar', default='"',
              help='(CSV dialect) Quoting char.')
@click.option('-e', '--escapechar', default=None,
              help='(CSV dialect) Escaping char.')
@click.option('-B', '--no-doublequote', is_flag=True,
              help='(CSV dialect) If set, quoting char itself will not be doubled.')
@click.pass_context
def cli(
    ctx, db_url, pre_sql, post_sql, transaction,
    no_header, tab, delimiter, lineterminator,
    quoting, quotechar, escapechar, no_doublequote,
):
    '''Import/Export data to/from relational databases using SQL statements with CSV files.'''
    ctx.obj = Command(
        db_url=db_url,
        pre_sql=pre_sql,
        post_sql=post_sql,
        transaction=transaction,
        header=not no_header,
        dialect=dict(
            delimiter='\t' if tab else delimiter,
            lineterminator=lineterminator,
            quoting=QUOTING[quoting.upper()],
            quotechar=quotechar,
            escapechar=escapechar,
            doublequote=not no_doublequote,
        )
    )


@cli.command()
@click.option('-s', '--sql', type=str, default=None,
              help='SELECT query string.')
@click.option('-f', '--sqlfile', type=click.File('r'), default=None,
              help='SELECT query file.')
@click.option('-o', '--outfile',
              type=click.Path(dir_okay=False, writable=True, allow_dash=True), default="-",
              help='Output CSV file.')
@click.pass_context
def select(ctx, sql, sqlfile, outfile):
    '''Export data from relational databases using SELECT statement and output as CSV.'''
    command = ctx.obj
    sql = _get_sql(sql, sqlfile)

    with _open(outfile, "wt") as f:
        command.select(sql, f)


@cli.command()
@click.option('-s', '--sql', type=str, default=None,
              help='INSERT query string.')
@click.option('-f', '--sqlfile', type=click.File('r'), default=None,
              help='INSERT query file.')
@click.option('-i', '--infile',
              type=click.Path(dir_okay=False, readable=True, allow_dash=True), default="-",
              help='Input CSV file.')
@click.option('-t', '--types', type=str, required=True,
              help="Types of each column, comma-separated e.g. 'int,float,string'.")
@click.option('-n', '--nullables', type=str, default=None,
              help="Whether or not allow nulls for each column, comma-separated e.g. 'true,false'.")
@click.option('-c', '--chunk-size', type=int, default=None,
              help="Insert records splitted up to chunks with specified row count for each, if specified.")  # noqa
@click.pass_context
def insert(ctx, sql, sqlfile, infile, types, nullables, chunk_size):
    '''Import data to relational databases using INSERT statement from CSV.'''
    command = ctx.obj
    sql = _get_sql(sql, sqlfile)
    types = tuple(map(_flag_to_type, types.split(',')))
    nullables = nullables and tuple(map(_flag_to_bool, nullables.split(',')))

    with _open(infile, "rt") as f:
        command.insert(sql, f, types, nullables, chunk_size)
