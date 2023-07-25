import json
import logging

import requests
from datetime import datetime
from telebot import TeleBot, types
from env_receiver import EnvReceiver
from constants import *
from db import DBUtil


class ApiRequests:
    def __init__(self, env_receiver: EnvReceiver, logger: logging.Logger):
        self._env_receiver = env_receiver
        self.logger = logger

    def get_cities(self, bot: TeleBot, chat_id: int, db: DBUtil, query: str):
        print('get_cities func')
        if not query:
            raise Exception('Query isnt set')

        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": self._env_receiver.rapid_api_key,
            "X-RapidAPI-Host": self._env_receiver.rapid_api_host
        }
        params = {
            "q": query,
            "locale": "en_US"
        }
        response = requests.get(LOCATIONS_URL, headers=headers, params=params)
        if not response.status_code == 200:
            self.logger.error(f'Status = {response.status_code}')
            return

        json_data = json.loads(response.text)
        if json_data['sr'] and len(json_data['sr']) > 0:
            found = False
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for region in json_data['sr']:
                display_name = 'None'
                if region['regionNames'] and region['regionNames']['secondaryDisplayName']:
                    display_name = region['regionNames']['secondaryDisplayName']
                region_id = region.get('gaiaId', 0)

                if region_id != 0:
                    found = True
                    db.add_city(display_name, query, region_id)
                    self.logger.info(f'REGION NAME = {display_name}, ID = {region_id}')
                    region_key = types.InlineKeyboardButton(text=display_name,
                                                            callback_data=f'region:{region_id}')
                    markup.add(region_key)
            if found:
                with bot.retrieve_data(chat_id) as data:
                    data["markup_changed"] = True
                bot.send_message(chat_id, 'Select city', reply_markup=markup)
            else:
                bot.send_message(chat_id, 'Nothing was found')
        else:
            bot.send_message(chat_id, 'Nothing was found')

    def get_hotels(self, bot: TeleBot, chat_id: int, db: DBUtil):
        print('get_hotels func')
        req = db.get_current_request(chat_id)[0]
        print('Settings =', req)
        start_date = datetime.strptime(req[5], DATE_FORMAT)
        end_date = datetime.strptime(req[6], DATE_FORMAT)
        time_diff = (end_date - start_date).days
        print('TIMEDELTA = ', time_diff)

        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": self._env_receiver.rapid_api_key,
            "X-RapidAPI-Host": self._env_receiver.rapid_api_host
        }
        params = {
            "currency": "USD",
            "eapid": "1",
            "locale": "en_US",
            "siteId": 300000001,
            "destination": {
                "regionId": str(req[4])
            },
            "checkInDate": {"day": start_date.day, "month": start_date.month, "year": start_date.year},
            "checkOutDate": {"day": end_date.day, "month": end_date.month, "year": end_date.year},
            "rooms": [{"adults": 1}],
            "resultsStartingIndex": 0,
            "resultsSize": req[7],
            "sort": "PRICE_LOW_TO_HIGH",
            "filters": {"availableFilter": "SHOW_AVAILABLE_ONLY"}
        }
        print('PARAMS =', params)
        response = requests.post(PROPERTIES_LIST_URL, headers=headers, params=params)
        if not response.status_code == 200:
            self.logger.error(f'Status = {response.status_code}')
            return

        json_data = json.loads(response.text)
        print('JSON DATA')
        print(json_data)
        if json_data['data']:
            resp_data = json_data.data
            if resp_data.propertySearch and resp_data.propertySearch.properties:
                props = resp_data.propertySearch.properties
                if len(props) == 0:
                    self.logger.error('No Properties at all!')
                    return

                for prop in props:
                    hotel_id = prop.id
                    prop_name = prop.name
                    price = prop.price.lead.amount
                    distance = prop.destinationInfo.distanceFromDestination.value
                    region_id = prop.destinationInfo.regionId
                    link = f'{HOTELS_URL}/h{hotel_id}.Hotel-Information'
                    prop_text = f'{prop_name}\n{distance} miles\
                        \n{prop.neighborhood.name}\n{price}\n{link}'
                    bot.send_message(chat_id, prop_text)
                    if time_diff > 0:
                        bot.send_message(chat_id, 'Total cost for ' + str(time_diff) +
                                         ' days: $' + str(round(price * time_diff, 2)))
                    db.add_hotel(hotel_id, prop_name, region_id, distance, price, link)

                    if req[8] == 1:
                        prop_image = prop.propertyImage
                        if prop_image and prop_image.image and prop_image.image.url:
                            url = prop_image.image.url
                            bot.send_photo(chat_id, url)
                            db.add_hotel_image(hotel_id, url, self.logger)
                        else:
                            self.logger.error('Cant get Property Image!')
                else:
                    self.logger.error('No Properties at all!')
            else:
                self.logger.error('Cant get Properties!')
        else:
            self.logger.error('Cant get Response Data!')
