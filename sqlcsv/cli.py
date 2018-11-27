import csv
import sys

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


@click.group()
@click.option('-u', '--db-url', envvar='SQLCSV_DB_URL', required=True)
@click.option('-p', '--pre-sql', default=None)
@click.option('-P', '--post-sql', default=None)
@click.option('-H', '--no-header', is_flag=True)
@click.option('-T', '--tab', is_flag=True)
@click.option('-d', '--delimiter', default=',')
@click.option('-l', '--lineterminator', default='\n')
@click.option('-Q', '--quoting', type=click.Choice(QUOTING.keys(), case_sensitive=False), default='MINIMAL')  # noqa
@click.option('-q', '--quotechar', default='"')
@click.option('-e', '--escapechar', default=None)
@click.option('-B', '--no-doublequote', is_flag=True)
@click.pass_context
def cli(
    ctx, db_url, pre_sql, post_sql,
    no_header, tab, delimiter, lineterminator,
    quoting, quotechar, escapechar, no_doublequote,
):
    ctx.obj = Command(
        db_url=db_url,
        pre_sql=pre_sql,
        post_sql=post_sql,
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
@click.option('-s', '--sql', type=str, default=None)
@click.option('-f', '--sqlfile', type=click.File('r'), default=None)
@click.option('-o', '--outfile', type=click.File('w'), default=sys.stdout)
@click.pass_context
def select(ctx, sql, sqlfile, outfile):
    command = ctx.obj
    sql = _get_sql(sql, sqlfile)

    command.select(sql, outfile)


@cli.command()
@click.option('-s', '--sql', type=str, default=None)
@click.option('-f', '--sqlfile', type=click.File('r'), default=None)
@click.option('-i', '--infile', type=click.File('r'), default=sys.stdin)
@click.option('-t', '--types', type=str, required=True)
@click.option('-n', '--nullables', type=str, default=None)
@click.pass_context
def insert(ctx, sql, sqlfile, infile, types, nullables):
    command = ctx.obj
    sql = _get_sql(sql, sqlfile)
    types = tuple(map(_flag_to_type, types.split(',')))
    nullables = nullables and tuple(map(_flag_to_bool, nullables.split(',')))

    command.insert(sql, infile, types, nullables)
