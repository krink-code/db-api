
CREATE DATABASE IF NOT EXISTS example;

CREATE TABLE IF NOT EXISTS example.table1 (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


INSERT INTO example.table1 (name)
VALUES 
 (UUID()),
 (UUID()),
 (UUID()),
 (UUID()),
 (UUID()),
 (UUID()),
 (UUID()),
 (UUID()),
 (UUID()),
 (UUID());



