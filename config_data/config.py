import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env.template.')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('hello', "Поприветствовать бота"),
    ('survey', "Опрос"),
    ('lowprice', "Самые дешёвые отели в городе"),
    ('highprice', "Самые дорогие отели в городе"),
    ('bestdeal', "Лучшие по цене и расположению от центра"),
    ('history', "Показать историю поиска"),
)