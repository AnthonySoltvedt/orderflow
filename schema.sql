-- OrderFlow database schema
-- Creates the tables required by the application.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES users(id)
);
