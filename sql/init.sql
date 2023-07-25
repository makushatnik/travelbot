CREATE TABLE requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chat_id INTEGER NOT NULL,
  operation TEXT NOT NULL,
  city TEXT,
  region_id INTEGER,
  start_date TEXT,
  end_date TEXT,
  hotel_count INTEGER DEFAULT 0,
  photo_needed INTEGER NOT NULL DEFAULT 0,
  photo_count INTEGER DEFAULT 0,
  step INTEGER NOT NULL DEFAULT 0,
  is_current INTEGER NOT NULL
)

CREATE TABLE hotels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hotels_com_id INTEGER,
  name TEXT NOT NULL,
  region_id INTEGER NOT NULL,
  distance REAL,
  price REAL,
  link TEXT NOT NULL
)

CREATE TABLE history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chat_id INTEGER NOT NULL,
  operation TEXT NOT NULL,
  made_at TEXT NOT NULL
)

CREATE TABLE history_hotels (
  history_id INTEGER NOT NULL,
  hotel_id INTEGER NOT NULL
)

CREATE TABLE hotel_images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hotel_id INTEGER NOT NULL,
  url TEXT NOT NULL,
  FOREIGN KEY(hotel_id) REFERENCES hotels(id)
)

CREATE TABLE cities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  query_name TEXT NOT NULL,
  region_id INTEGER NOT NULL
)