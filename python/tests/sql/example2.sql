
CREATE DATABASE IF NOT EXISTS example3;

CREATE TABLE IF NOT EXISTS example3.table3 (
  id VARCHAR(255) PRIMARY KEY NOT NULL,
  json JSON,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  modified DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FULLTEXT(json),
  CHECK(JSON_VALID(json))
) ENGINE=InnoDB;

