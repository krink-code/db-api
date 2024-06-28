
create user 'dbuser'@'%' IDENTIFIED BY 'dbpass';
grant all privileges on *.* to 'dbuser'@'%' with grant option;
flush privileges;

