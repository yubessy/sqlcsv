CREATE TABLE testtable (
  id INT AUTO_INCREMENT PRIMARY KEY,
  int_col INT,
  float_col FLOAT,
  varchar_col VARCHAR(255),
  datetime_col DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

INSERT INTO
  testtable(int_col, float_col, varchar_col, datetime_col)
VALUES
  (1, 1.0, 'aaa', '2001-01-01 01:23:45'),
  (2, 2.0, 'bbb', '2002-02-02 12:34:56'),
  (NULL, NULL, NULL, NULL)
;
