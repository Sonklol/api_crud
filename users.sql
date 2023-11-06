CREATE TABLE users (
    iduser INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    fsurname VARCHAR(100) NOT NULL,
    ssurname VARCHAR(100),
    birthdate DATE NOT NULL,
    permissions ENUM('user','admin') NOT NULL DEFAULT 'user',
    email VARCHAR(255) NOT NULL UNIQUE,
    passwd VARCHAR(255) NOT NULL,
    code INT(6),
    active TINYINT(1) NOT NULL DEFAULT 0
);