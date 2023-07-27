import sqlite3
import logging
from config_data.config import DATABASE_NAME


class DBUtil:

    def __init__(self):
        self._dbname = DATABASE_NAME
        self._conn = sqlite3.connect(self._dbname)

    def get_hotels(self):
        pass

    def get_step(self, chat_id: int):
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT step FROM requests WHERE chat_id = {chat_id} AND is_current = 1')
            return cursor.fetchall()

    def get_current_request(self, chat_id: int):
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM requests WHERE chat_id = {chat_id} AND is_current = 1')
            return cursor.fetchall()

    def add_request(self, chat_id: int, operation: str):
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO requests (chat_id, operation, step, is_current) VALUES(" +
                           str(chat_id) + ", '" + DBUtil.safe_str(operation) + "', 1, 1)")
            conn.commit()

    def add_city_to_request(self, chat_id: int, city: str):
        requests = self.get_current_request(chat_id)
        if not requests or len(requests) == 0:
            raise Exception('Current request not found!')
        request_id = requests[0][0]
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE requests SET city = '" + DBUtil.safe_str(city) + "', step = 2 " +
                           "WHERE id = " + str(request_id))
            conn.commit()

    def add_start_date_to_request(self, chat_id: int, start_date: str):
        requests = self.get_current_request(chat_id)
        if not requests or len(requests) == 0:
            raise Exception('Current request not found!')
        request_id = requests[0][0]
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE requests SET start_date = '" + DBUtil.safe_str(start_date) +
                           "', step = 4 WHERE id = " + str(request_id))
            conn.commit()

    def add_end_date_to_request(self, chat_id: int, end_date: str):
        requests = self.get_current_request(chat_id)
        if not requests or len(requests) == 0:
            raise Exception('Current request not found!')
        request_id = requests[0][0]
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE requests SET end_date = '" + DBUtil.safe_str(end_date) +
                           "', step = 5 WHERE id = " + str(request_id))
            conn.commit()

    def add_hotel_count_to_request(self, chat_id: int, hotel_count: int):
        requests = self.get_current_request(chat_id)
        if not requests or len(requests) == 0:
            raise Exception('Current request not found!')
        request_id = requests[0][0]
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE requests SET hotel_count = " + str(hotel_count) + ", step = 6 " +
                           "WHERE id = " + str(request_id))
            conn.commit()

    def set_photo_needed_to_request(self, chat_id: int, photo_needed: str):
        requests = self.get_current_request(chat_id)
        if not requests or len(requests) == 0:
            raise Exception('Current request not found!')
        request_id = requests[0][0]
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE requests SET photo_needed = " +
                           str(1 if photo_needed == 'yes' else 0) + ", step = 7 " +
                           "WHERE id = " + str(request_id))
            conn.commit()

    def add_photo_count_to_request(self, chat_id: int, photo_count: int):
        requests = self.get_current_request(chat_id)
        if not requests or len(requests) == 0:
            raise Exception('Current request not found!')
        request_id = requests[0][0]
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE requests SET photo_count = " + str(photo_count) + ", step = 8 " +
                           "WHERE id = " + str(request_id))
            conn.commit()

    def add_region_id_to_request(self, chat_id: int, region_id: str):
        requests = self.get_current_request(chat_id)
        if not requests or len(requests) == 0:
            raise Exception('Current request not found!')
        request_id = requests[0][0]
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE requests SET region_id = " + DBUtil.safe_str(region_id) +
                           ", step = 3 WHERE id = " + str(request_id))
            conn.commit()

    def add_region_id_to_request_by_city_name(self, chat_id: int, name: str):
        cities = self.get_city_by_name(name)
        if not cities or len(cities) == 0:
            raise Exception('City not found!')
        region_id = cities[0][3]

        requests = self.get_current_request(chat_id)
        if not requests or len(requests) == 0:
            raise Exception('Current request not found!')
        request_id = requests[0][0]

        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE requests SET region_id = " + str(region_id) + ", step = 3 " +
                           "WHERE id = " + str(request_id))
            conn.commit()

    def set_current_step(self, chat_id: int, step: int):
        requests = self.get_current_request(chat_id)
        if not requests or len(requests) == 0:
            raise Exception('Current request not found!')
        request_id = requests[0][0]

        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE requests SET step = {step} WHERE id = {request_id}")
            conn.commit()

    def set_request_inactive(self, chat_id: int):
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE requests SET is_current = 0, step = 0 WHERE chat_id = {chat_id}")
            conn.commit()

    def delete_requests(self, chat_id: int):
        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM requests WHERE chat_id = {chat_id}')
            conn.commit()

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

    def add_hotel(self, hotel_id: int, name: str, region_id: int, distance: float, price: float, link: str):
        hotels = self.get_hotel_by_id(hotel_id)
        if hotels and len(hotels) > 0:
            return

        with sqlite3.connect(self._dbname) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO hotels (hotels_com_id, name, region_id, distance, price, link) VALUES(" +
                           str(hotel_id) + ", '" + DBUtil.safe_str(name) + "', " + str(region_id) + ", " +
                           str(distance) + ", " + str(price) + ", '" + link + "')")
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
