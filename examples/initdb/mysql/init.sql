CREATE TABLE testtable (
  id INT AUTO_INCREMENT PRIMARY KEY,
  int_col INT,
  float_col FLOAT,
  varchar_col VARCHAR(255),
  blob_col BLOB,
  datetime_col DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

INSERT INTO
  testtable(int_col, float_col, varchar_col, blob_col, datetime_col)
VALUES
  (1, 1.0, 'aaa', 'xxx', '2001-01-01 01:23:45'),
  (2, 2.0, 'bbb', 'yyy', '2002-02-02 12:34:56'),
  (NULL, NULL, NULL, NULL, NULL)
;
