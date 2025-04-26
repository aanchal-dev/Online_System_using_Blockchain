CREATE DATABASE voting_system;
USE voting_system;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(100),
    lname VARCHAR(100),
    fathername VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    email VARCHAR(100),
    mobile VARCHAR(20),
    password VARCHAR(100),
    id_proof VARCHAR(255),
    is_approved BOOLEAN DEFAULT FALSE
);

CREATE TABLE parties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    symbol VARCHAR(100)
);

CREATE TABLE votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(100),
    party_id INT,
    block_hash VARCHAR(64)
);
