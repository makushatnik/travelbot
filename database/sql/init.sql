CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  username TEXT,
  banned INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE hotels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hotels_com_id INTEGER,
  name TEXT NOT NULL,
  region_id INTEGER NOT NULL,
  distance REAL,
  price REAL
);

CREATE TABLE history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  command TEXT NOT NULL,
  made_at TEXT NOT NULL
);

CREATE TABLE history_hotels (
  history_id INTEGER NOT NULL,
  hotel_id INTEGER NOT NULL
);

CREATE TABLE hotel_images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hotel_id INTEGER NOT NULL,
  url TEXT NOT NULL,
  FOREIGN KEY(hotel_id) REFERENCES hotels(id)
);

CREATE TABLE cities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  query_name TEXT NOT NULL,
  region_id INTEGER NOT NULL
);