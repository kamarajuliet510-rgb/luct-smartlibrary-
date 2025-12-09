-- Create tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'staff'
);

CREATE TABLE author (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    bio VARCHAR(500),
    nationality VARCHAR(50),
    birth_year INTEGER
);

CREATE TABLE member (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    membership_type VARCHAR(20),
    join_date DATE
);

CREATE TABLE bookclub (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    meeting_day VARCHAR(20)
);

CREATE TABLE book (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author_id INTEGER REFERENCES author(id) ON DELETE SET NULL,
    isbn VARCHAR(13) UNIQUE,
    publisher VARCHAR(100),
    published_year INTEGER,
    genre VARCHAR(50),
    copies_available INTEGER DEFAULT 1
);

CREATE TABLE loan (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES book(id) ON DELETE CASCADE,
    member_id INTEGER REFERENCES member(id) ON DELETE CASCADE,
    loan_date DATE,
    due_date DATE,
    return_date DATE,
    status VARCHAR(20)
);