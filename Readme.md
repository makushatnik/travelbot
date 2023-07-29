## Travel Bot
### Commands
- start - Запуск бота. Показать кнопку "help"
- help - Показать список доступных команд
- lowprice - Узнать топ самых дешевых отелей в городе
- highprice - Узнать топ самых дорогих отелей в городе
- bestdeal - Узнать топ отелей, наиболее подходящих по цене и расположению от центра
- history - Узнать историю поиска отелей
### Settings
You need your own Telegram API token.\
Also you need to be registered at the [Rapidapi.com](https://rapidapi.com/apidojo/api/hotels4/). You need to get host & api key there.

When all preparations are done, you should do this steps:
1. Clone the repository,
2. Activate Virtual Environment in the project,
3. Create file .env with following variables:
   * BOT_TOKEN
   * RAPID_API_KEY
4. Type the commands:
    ```
    pip install -r requirements.txt
    python main.py
    ```