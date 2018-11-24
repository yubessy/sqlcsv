# sqlcsv

Simple command line tool that can be used to:

- SELECT data from database and export the result as CSV
- INSERT data into database from CSV

## Installation

Via PyPI:

```
$ pip3 install sqlcsv
```

By default it does not install any database drivers.
Install them by your own need:

```
# MySQL
$ pip3 install mysqlclient

# PostgreSQL
$ pip3 install psycopg2
```

## Usage

In the examples below we use following table schema with MySQL:

```sql
CREATE TABLE testtable(
  id INT AUTO_INCREMENT PRIMARY KEY,
  int_col INT,
  float_col FLOAT,
  varchar_col VARCHAR(255)
)
```

### Connection

You can specify database connection info by SQLAlchemy URL using `--db-url`:

```
$ sqlcsv --db-url 'mysql://testuser:testpassword@127.0.0.1:3306/testdb' <subcommand> ...
```

Also it can be read from `SQLCSV_DB_URL` environment variable:

```
$ export SQLCSV_DB_URL='mysql://testuser:testpassword@127.0.0.1:3306/testdb'
$ sqlcsv <subcommand> ...
```

From here we assume that connection is specified using environment variable.

### SELECT

Assume we already have following records on the table in our database:

```
+----+---------+-----------+-------------+
| id | int_col | float_col | varchar_col |
+----+---------+-----------+-------------+
|  1 |       1 |         1 | aaa         |
|  2 |       2 |         2 | bbb         |
|  3 |    NULL |      NULL | NULL        |
+----+---------+-----------+-------------+
```

Use `select` subcommand and give `SELECT` query using '--sql':

```
$ sqlcsv select \
  --sql 'SELECT * FROM testtable'
id,int_col,float_col,varchar_col
1,1,1.0,aaa
2,2,2.0,bbb
3,,,
```

If you want to save the result to file, use `--outfile`:

```
$ sqlcsv select \
  --sql 'SELECT * FROM testtable' \
  --outfile out.csv
```

### INSERT

Assume we have following CSV file:

```
int_col,float_col,varchar_col
1,1.0,aaa
2,2.0,bbb
```

Use `insert` subcommand and give `INSERT` query with placeholders using '--sql', followed by `--types` specifying types of each field:

```
$ sqlcsv insert \
  --sql 'INSERT INTO testtable(int_col, float_col, varchar_col) VALUES (%s, %s, %s) \
  --types int,float,str
```

The resulted records in the table are to be:

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

#### NULLs

You may have CSV file contains empty cell and may want to treat them as `NULL` in SQL like:

```
int_col,float_col,varchar_col
1,,aaa
2,2.0,
```

In such case use `--nullable` to convert them to `None` before insertion:

```
$ sqlcsv insert \
  --sql 'INSERT INTO testtable(int_col, float_col, varchar_col) VALUES (%s, %s, %s) \
  --types int,float,str \
  --nullable false,true,true
```

The result to be:

```
+----+---------+-----------+-------------+
| id | int_col | float_col | varchar_col |
+----+---------+-----------+-------------+
|  1 |       1 |      NULL | aaa         |
|  2 |       2 |         2 | NULL        |
+----+---------+-----------+-------------+
```

Values of `--nullable` are one of `true` or `false`.
They can also be written as `t` or `f` in short forms.

### Read SQL from file

In both `select` and `insert` subcommands you can use `--sqlfile` option to read query from a file intead of using `--sql`:

```
$ sqlcsv select --sqlfile query.sql
$ sqlcsv insert --sqlfile query.sql
```

### CSV dialect

If your input or output have to be tab-separated (TSV), use `--tab` like:

```
$ sqlcsv --tab select --sql 'SELECT * FROM testtable'
id	int_col	float_col	varchar_col
1	1	1.0	aaa
2	2	2.0	bbb
```

For other format options, see `sqlcsv --help`.
Basically it supports the same option as [csv package in Python's standard libraries](https://docs.python.org/3/library/csv.html) does.

## Comparison between other tools

### LOAD (MySQL) or COPY (PostgreSQL)

Major RDBMSs usually have built-in instructions to import data from files such as `LOAD` instruction for MySQL or `COPY` for PostgreSQL.
They are obviously the primary options you may consider but there are some limitations for them:

- Few platform support imports across network; others only can do from local files
- Specification for data format or instruction varies for each platform

Sqlcsv works remotely and provides unified interfaces at least for CSV format.

### CSVKit

[CSVKit](https://csvkit.readthedocs.io) is a popular toolkit for manipulating CSV files.
It provides [sql2csv](https://csvkit.readthedocs.io/en/latest/scripts/sql2csv.html) and [csvsql](https://csvkit.readthedocs.io/en/latest/scripts/csvsql.html) commands for export/import data to/from files.
Consider using them before choosing sqlcsv if they just satisfy your needs, as they have much more users and contributers, though there might be a few reasons to prefer sqlcsv to them (and this is why it was created) :

- CSVKit depends on several libraries including [agate](https://agate.readthedocs.io/) but not all of them are needed for interoperability between SQL databases and CSV files.
  Sqlcsv uses [csv package in Python's standard libraries] for I/O with CSV files and [SQLAlchemy](https://www.sqlalchemy.org/) for querying SQL databases, which leads to less library dependencies.
- CSVKit's csvsql command takes just table name for import target, which make it easy to use.
  However, it is sometimes inconvenient in such cases where CSV file includes only a part of columns and others are generated dynamically by SQL expressions.
  Sqlcsv's `insert` subcommand, by contrast, takes `INSERT` statement, which might be verbose but provides more flexibility.

### Pandas

If you do not care about library dependencies, do not need custom `INSERT` statement and do not need command line interfaces, then just use [pandas](https://pandas.pydata.org/)' [DataFrame.to_sql](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_sql.html) method or [read_sql](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_sql.html) function.
They will help you a lot if used with [DataFrame.to_csv](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_csv.html) method or [read_csv](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html) function.

### Embulk

If your dataset is so large that needs performance optimization such as parallel processing, or you want some sophisticated I/O functionality such as retrying, consider using [Embulk](https://github.com/embulk/embulk).
It also supports various data stores and data formats with many plugins.

