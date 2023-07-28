import sqlite3


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)


def create():
    database = r"../hotels.db"

    sql_create_requests = """CREATE TABLE requests (
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
                        );"""

    sql_create_cities = """CREATE TABLE cities (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          query_name TEXT NOT NULL,
                          region_id INTEGER NOT NULL
                        );"""

    sql_create_hotels = """CREATE TABLE hotels (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          hotels_com_id INTEGER,
                          name TEXT NOT NULL,
                          region_id INTEGER NOT NULL,
                          distance REAL,
                          price REAL,
                          link TEXT NOT NULL
                        );"""

    sql_create_hotel_images = """CREATE TABLE hotel_images (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          hotel_id INTEGER NOT NULL,
                          url TEXT NOT NULL,
                          FOREIGN KEY(hotel_id) REFERENCES hotels(id)
                        );"""

    conn = create_connection(database)
    if conn is not None:
        create_table(conn, sql_create_requests)
        create_table(conn, sql_create_cities)
        create_table(conn, sql_create_hotels)
        create_table(conn, sql_create_hotel_images)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    create()
