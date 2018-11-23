CREATE SCHEMA testschema;
CREATE TABLE testschema.testtable (
  id SERIAL PRIMARY KEY,
  int_col INT,
  real_col REAL,
  varchar_col VARCHAR(255),
  bytea_col BYTEA,
  timestamp_col TIMESTAMP
)
;

INSERT INTO
  testschema.testtable(int_col, real_col, varchar_col, bytea_col, timestamp_col)
VALUES
  (1, 1.0, 'aaa', 'xxx', '2001-01-01 01:23:45'),
  (2, 2.0, 'bbb', 'yyy', '2002-02-02 12:34:56'),
  (NULL, NULL, NULL, NULL, NULL)
;
