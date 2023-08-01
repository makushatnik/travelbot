import json
import logging

import requests
from typing import Dict, List
from datetime import datetime
from telebot import TeleBot, types
from telebot.types import InputMediaPhoto
from config_data.config import *
from utils.constants import *
from keyboards.reply.reply import get_keyboard_for_cities
from database.orm import Hotel, HotelImage, City
from utils.utils import safe_str


class ApiRequests:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def get_cities(self, bot: TeleBot, chat_id: int, query: str, locale: str):
        """
        Function for sending query for getting list of cities
        """
        # print('get_cities func')
        bot.send_chat_action(chat_id=chat_id, action='typing')
        params = {
            "q": query,
            "locale": locale
        }

        try:
            response = requests.get(LOCATIONS_URL, headers=get_common_headers(), params=params)
            if not response.status_code == 200:
                self.logger.error(f'Status = {response.status_code}')
                return

            json_data = json.loads(response.text)
            found = False
            markup = get_keyboard_for_cities()
            for region in json_data['sr']:
                display_name = 'None'
                if region['regionNames'] and region['regionNames']['secondaryDisplayName']:
                    display_name = region['regionNames']['secondaryDisplayName']
                region_id = region.get('gaiaId', 0)

                if region_id != 0:
                    found = True
                    City.create(name=display_name, query_name=query, region_id=region_id)
                    region_key = types.InlineKeyboardButton(text=display_name,
                                                            callback_data=f'region:{region_id}')
                    markup.add(region_key)
            if found:
                bot.send_message(chat_id, 'Select city', reply_markup=markup)
            else:
                bot.send_message(chat_id, 'Nothing was found')
        except Exception as ex:
            self.logger.error(ex)

    def get_hotels(self, bot: TeleBot, chat_id: int, data: Dict):
        """
        Function for sending query for getting list of hotels
        """
        # print('get_hotels func')
        bot.send_chat_action(chat_id=chat_id, action='typing')
        start_date = datetime.strptime(data['start_date'], DATE_FORMAT)
        end_date = datetime.strptime(data['end_date'], DATE_FORMAT)
        days_diff = (end_date - start_date).days
        days_diff = 1 if days_diff <= 1 else days_diff
        command = data['command']

        result = []
        try:
            response = requests.post(PROPERTIES_LIST_URL,
                                     headers=get_common_headers(),
                                     json=get_hotels_params(data, start_date, end_date))
            if not response.status_code == 200:
                self.logger.error(f'Status = {response.status_code}')
                return

            json_data = json.loads(response.text)
            props = json_data['data']['propertySearch']['properties']
            if len(props) == 0:
                self.logger.error('No Properties at all!')
                return

            result += process_hotels_json(props, data, days_diff)
        except Exception as ex:
            self.logger.error(ex)

        detail_request_needed = data['photo_count'] > 1
        try:
            cnt = len(result)
            if cnt == 0:
                bot.send_message(chat_id, 'No properties were found using data you entered')
                return

            i = 1
            for prop_elem in result:
                if command == 'bestdeal' and prop_elem['distance'] > data['max_distance']:
                    break

                if data['photo_needed']:
                    bot.send_chat_action(chat_id=chat_id, action='upload_photo')
                    # if we need just 1 photo, we'll send it right away
                    if not detail_request_needed:
                        bot.send_photo(chat_id, prop_elem['images'][0], caption=prop_elem['text'])
                    else:
                        photo_urls = self.get_prop_photos(prop_elem['id'], data['photo_count'])
                        photos = [
                            InputMediaPhoto(media=url,
                                            caption=prop_elem['text']) if idx == 0 else InputMediaPhoto(media=url)
                            for idx, url in enumerate(photo_urls)
                        ]
                        bot.send_media_group(chat_id, photos)
                else:
                    bot.send_message(chat_id, prop_elem['text'], disable_web_page_preview=True)

                if i < cnt:
                    bot.send_chat_action(chat_id=chat_id, action='typing')
                i += 1
        except Exception as ex:
            self.logger.error(ex)

    def get_prop_photos(self, prop_id: int, max_cnt: int) -> List[str]:
        # print('get_prop_photos func')
        params = {
            "currency": "USD",
            "eapid": 1,
            "locale": "ru_RU",
            "siteId": 300000001,
            "propertyId": str(prop_id)
        }

        response = requests.post(PROPERTIES_DETAIL_URL, headers=get_common_headers(), json=params)
        if not response.status_code == 200:
            self.logger.error(f'Status = {response.status_code}')
            return []

        i = 0
        photo_urls = []
        json_data = json.loads(response.text)
        images = json_data['data']['propertyInfo']['propertyGallery']['images']
        for image in images:
            if i >= max_cnt:
                break

            photo_urls.append(image['image']['url'])
            i += 1
        return photo_urls


def get_common_headers() -> Dict:
    return {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }


def get_hotels_params(data: Dict, start_date: datetime, end_date: datetime) -> Dict:
    params = {
        "currency": "USD",
        "eapid": "1",
        "locale": data['language'],
        "siteId": 300000001,
        "destination": {
            "regionId": str(data['region_id'])
        },
        "checkInDate": {"day": start_date.day, "month": start_date.month, "year": start_date.year},
        "checkOutDate": {"day": end_date.day, "month": end_date.month, "year": end_date.year},
        "rooms": [{"adults": 1}],
        "resultsStartingIndex": 0,
        "resultsSize": data['hotel_count'],
        "sort": data["sort"],
        "filters": {"availableFilter": "SHOW_AVAILABLE_ONLY"}
    }

    if data['command'] == 'bestdeal':
        params["filters"] = {
            "price": {
                "min": data["min_price"],
                "max": data["max_price"]
            }
        }
    return params


def process_hotels_json(props: List[Dict], data: Dict, days_diff: int) -> List[Dict]:
    # print('process_hotels_json func')
    # command = data['command']
    # max_distance = data['max_distance']
    result = []
    i = 1
    for prop in props:
        prop_elem = {}
        hotel_id = prop['id']
        prop_elem['id'] = hotel_id
        prop_name = prop['name']
        price = round(prop['price']['lead']['amount'], 2)
        distance = prop['destinationInfo']['distanceFromDestination']['value']
        region_id = prop['destinationInfo']['regionId']
        link = f'{HOTELS_URL}/h{hotel_id}.Hotel-Information'
        neighborhood_name = ''
        if prop['neighborhood'] and prop['neighborhood']['name']:
            neighborhood_name = prop['neighborhood']['name']
        elif prop['destinationInfo'] and prop['destinationInfo']['distanceFromMessaging']:
            neighborhood_name = prop['destinationInfo']['distanceFromMessaging']
        price_diff = round(days_diff * price, 2)
        prop_elem['distance'] = float(distance)

        prop_elem['text'] = f'{i}) Название отеля: {prop_name}\n' \
                            f'От центра: {distance} км\n' \
                            f'Название района: {neighborhood_name}\n' \
                            f'Цена за сутки: ${price}\n' \
                            f'Всего за {days_diff} дней: ${price_diff}\n' \
                            f'{link}'

        Hotel.create(
            hotels_com_id=hotel_id,
            name=safe_str(prop_name),
            region_id=region_id,
            distance=distance,
            price=price
        )
        i += 1

        # if user decided to watch a photo, we'll show it
        if data['photo_needed'] == 1:
            prop_image = prop['propertyImage']
            # some properties have no image, so we need to check it
            if prop_image and prop_image['image'] and prop_image['image']['url']:
                url = prop_image['image']['url']
                prop_elem['images'] = []
                prop_elem['images'].append(url)
                HotelImage.create(hotel_id=hotel_id, url=url)

        result.append(prop_elem)
    return result


def custom_key(prop_elem: Dict):
    return prop_elem.distance