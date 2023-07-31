import sqlite3
import logging
from utils.constants import DATABASE_NAME


class DBUtil:

    def __init__(self):
        self._dbname = DATABASE_NAME
        self._conn = sqlite3.connect(self._dbname)

    def get_region_id_by_city_name(self, name: str):
        cities = self.get_city_by_name(name)
        if not cities or len(cities) == 0:
            raise Exception('City not found!')
        return cities[0][3]

    def get_city_by_region_id(self, region_id: str):
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM cities WHERE region_id = {region_id}')
            return cursor.fetchall()

    def get_city_by_name(self, name: str):
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM cities WHERE name = '{name}'")
            return cursor.fetchall()

    def add_city(self, name: str, query_name: str, region_id: str):
        cities = self.get_city_by_region_id(region_id)
        if cities and len(cities) > 0:
            return

        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cities (name, query_name, region_id) VALUES ('" +
                           DBUtil.safe_str(name) + "', '" + query_name + "'," + region_id + ")")
            conn.commit()

    def get_hotel_by_id(self, hotel_id: int):
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM hotels WHERE hotels_com_id = {hotel_id}')
            return cursor.fetchall()

    def add_hotel(self, hotel_id: int, name: str, region_id: int, distance: float, price: float):
        hotels = self.get_hotel_by_id(hotel_id)
        if hotels and len(hotels) > 0:
            return

        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO hotels (hotels_com_id, name, region_id, distance, price) VALUES(" +
                           str(hotel_id) + ", '" + DBUtil.safe_str(name) + "', " + str(region_id) + ", " +
                           str(distance) + ", " + str(price) + ")")
            conn.commit()

    def add_hotel_image(self, hotel_id: int, url: str, logger: logging.Logger):
        hotels = self.get_hotel_by_id(hotel_id)
        if not hotels or len(hotels) == 0:
            logger.error('Hotel not found by hotels com ID')
            return
        print()
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO hotel_images (hotel_id, url) VALUES (" +
                           str(hotels[0][0]) + ", '" + url + "')")
            conn.commit()

    @staticmethod
    def safe_str(string: str) -> str:
        res = string.replace("'", "")
        res = res.replace("\"", "")
        return res


db = DBUtil()
