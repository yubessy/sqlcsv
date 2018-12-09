# sqlcsv

Simple command line tool that can be used to:

- SELECT data from database and export the result as CSV
- INSERT data into database from CSV

Note that it works only with Python 3, not 2.

## Installation

Via PyPI:

```
$ pip3 install sqlcsv
```

It does not specify any database drivers as explicit dependencies, so install the one you need:

```
# MySQL
$ pip3 install mysqlclient

# PostgreSQL
$ pip3 install psycopg2
```

## Basic usage

In the examples below following table schema with MySQL is used:

```sql
CREATE TABLE testtable(
  id INT AUTO_INCREMENT PRIMARY KEY,
  int_col INT,
  float_col FLOAT,
  varchar_col VARCHAR(255)
)
```

### Database connection

Database connection can be specified using `--db-url` option in the form of SQLAlchemy URL:

```
$ sqlcsv --db-url 'mysql://testuser:testpassword@127.0.0.1:3306/testdb' <subcommand> ...
```

Also it will be read from `SQLCSV_DB_URL` environment variable if set:

```
$ export SQLCSV_DB_URL='mysql://testuser:testpassword@127.0.0.1:3306/testdb'
$ sqlcsv <subcommand> ...
```

From here they are omitted from command line examples.

### SELECT

Assume we already have following records on the table:

```
+----+---------+-----------+-------------+
| id | int_col | float_col | varchar_col |
+----+---------+-----------+-------------+
|  1 |       1 |         1 | aaa         |
|  2 |       2 |         2 | bbb         |
|  3 |    NULL |      NULL | NULL        |
+----+---------+-----------+-------------+
```

Use `select` subcommand and give `SELECT` query using `--sql` option:

```
$ sqlcsv select --sql 'SELECT * FROM testtable'
id,int_col,float_col,varchar_col
1,1,1.0,aaa
2,2,2.0,bbb
3,,,
```

If you want to save the result to file, use `--outfile` option:

```
$ sqlcsv select --sql 'SELECT * FROM testtable' --outfile out.csv
```

### INSERT

Assume we already have following dataset in `input.csv`:

```
int_col,float_col,varchar_col
1,1.0,aaa
2,2.0,bbb
```

Use `insert` subcommand and give `INSERT` query with placeholders using `--sql` option, followed by `--types` option specifying types of each field:

```
$ sqlcsv insert \
  --sql 'INSERT INTO testtable(int_col, float_col, varchar_col) VALUES (%s, %s, %s)' \
  --infle input.csv --types int,float,str
```

The resulted records in the table would be:

```
+----+---------+-----------+-------------+
| id | int_col | float_col | varchar_col |
+----+---------+-----------+-------------+
|  1 |       1 |         1 | aaa         |
|  2 |       2 |         2 | bbb         |
+----+---------+-----------+-------------+
```

Note that type names in `--types` are the same as Python primitive type function names.
Also it can be short form like `--types i,f,s`

Currently it supports only `int`, `float` and `str`.

#### NULLs

You may have CSV file contains empty cell like:

```
int_col,float_col,varchar_col
1,,aaa
2,2.0,
```

If you want to treat them as 'NULL' in database, use `--nullable` option to convert them before insertion:

```
$ sqlcsv insert
  --sql 'INSERT INTO testtable(int_col, float_col, varchar_col) VALUES (%s, %s, %s)
  --infile input.csv --types int,float,str --nullable false,true,true \
```

The result would be:

```
+----+---------+-----------+-------------+
| id | int_col | float_col | varchar_col |
+----+---------+-----------+-------------+
|  1 |       1 |      NULL | aaa         |
|  2 |       2 |         2 | NULL        |
+----+---------+-----------+-------------+
```

Note that values of `--nullable` have to be one of `true` or `false`, and they can also be written as `t` or `f` in a short form.

## More options

### CSV dialect

If your desired input or output is tab-separated (TSV), use `--tab` option:

```
$ sqlcsv --tab select --sql 'SELECT * FROM testtable'
id	int_col	float_col	varchar_col
1	1	1.0	aaa
2	2	2.0	bbb
```

For other format settings, see `sqlcsv --help`.
Basically it supports the same dialect specification as [csv package in Python's standard libraries](https://docs.python.org/3/library/csv.html) does.

### Read SQL from file

In both `select` and `insert` subcommands you can use `--sqlfile` option intead of `--sql` in order to read query from a file:

```
$ sqlcsv select --sqlfile query.sql
$ sqlcsv insert --sqlfile query.sql ...
```

### Pre and post querying

In case you need to execute short query before/after the main query runs, it provides `--pre-sql` and `--post-sql` options to satisfy such needs:

```
$ sqlcsv select --pre-sql 'SET SESSION wait_timeout = 60' --sql ...
```

### Chunked insertion

When you import a large number of records into database, `--chunk-size` option is helpful to save memory usage by splitting file contents up into different pieces and transfer each of them to the database repeatedly.

```
$ sqlcsv insert --sql ... --infile ... --types ... --chunk-size 1000
```

### Run in transaction

If you want multiple queries executed in single command call such as ones specified by `--pre-sql` or `--post-sql` to be run in the same transaction, use `--transaction` option as follows:

```
$ sqlcsv --transaction select --pre-sql ... --post-sql ... --sql ...
```

It is also a good practice to use this option with `--chunk-size` in order to execute chunked insersion atomically and to avoid leaving incomplete data on table when the query is cancelled or aborted.

## Comparison between other tools

### LOAD or COPY

Major RDBMSs usually have built-in instructions to import data from files such as `LOAD` for MySQL or `COPY` for PostgreSQL.
They are obviously the primary choices you may consider but also have some limitations:

- Few platform support import/export across network; others only can do from local files
- Specification for data format or instruction varies for each platform

Sqlcsv works remotely and provides unified interfaces (except SQL dialects).

### CSVKit

[CSVKit](https://csvkit.readthedocs.io) is a popular toolkit for manipulating CSV files.
It provides [sql2csv](https://csvkit.readthedocs.io/en/latest/scripts/sql2csv.html) and [csvsql](https://csvkit.readthedocs.io/en/latest/scripts/csvsql.html) commands for export/import data from/to SQL databases.
**Consider using them before choosing sqlcsv** if they just satisfy your needs, as they have much more users and contributers.
Hoever, there sill might be a few reasons to prefer sqlcsv to them (and this is why it was created):

- CSVKit depends on several libraries including [agate](https://agate.readthedocs.io/) but not all of them are needed for interoperability between SQL databases and CSV files.
  Sqlcsv uses [csv package in Python's standard libraries](https://docs.python.org/3/library/csv.html) to interact with CSV files and [SQLAlchemy](https://www.sqlalchemy.org/) to query SQL databases, which leads to less library dependencies.
- CSVKit's csvsql command takes just table name for import, which make it easy to use.
  However, it is sometimes inconvenient in such cases where CSV file includes only a part of columns and others are generated dynamically by SQL expressions.
  Sqlcsv's `insert` subcommand, by contrast, takes `INSERT` statement, which might be verbose but provides more flexibility.

### Pandas

If you do not care about library dependencies, do not need custom `INSERT` statement to be specified, and even do not need command line interfaces, then just use [pandas](https://pandas.pydata.org/)' [DataFrame.to_sql](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_sql.html) or [read_sql](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_sql.html).
They will help you a lot if used with [DataFrame.to_csv](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_csv.html) or [read_csv](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html).

### Embulk

If your dataset is so large that requires optimization such as parallel processing, or you want some sophisticated I/O functionality such as retrying, consider using [Embulk](https://github.com/embulk/embulk).
It also provides well-developed plugin ecosystem that enables support of various data stores and data formats.
