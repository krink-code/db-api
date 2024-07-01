create user 'dbuser'@'%' IDENTIFIED BY 'dbpass';
grant all privileges on db1.* to 'dbuser'@'%';
flush privileges;
