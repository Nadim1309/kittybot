import os
import hashlib
import requests
import time
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


load_dotenv()
token = os.getenv('TOKEN')
updater = Updater(token)
URL1 = 'https://api.thecatapi.com/v1/images/search'
URL2 = 'https://www.cbr-xml-daily.ru/daily_json.js'
PID = os.getenv('PID')
KEY1 = os.getenv('KEY1')
query = 'pid=' + PID + '&method=getRandItem&format=json&uts=' + \
    str(int(time.time()))
signature = hashlib.md5((query + KEY1).encode())
url = 'http://anecdotica.ru/api?' + query + '&hash=' + signature.hexdigest()
crb_daily = 0


def get_joke():
    response = requests.get(url)
    response = response.json()
    return response['item']['text']


def weather_request(update, context):
    city_url = {
        'Ульяновск': 'https://api.weather.yandex.ru/v2/forecast?lat=54.378391&lon=48.584446',
        'Москва': 'https://api.weather.yandex.ru/v2/forecast?lat=55.745007&lon=37.618140',
        'Питер': 'https://api.weather.yandex.ru/v2/forecast?lat=59.909216&lon=30.313955',
        'Самара': 'https://api.weather.yandex.ru/v2/forecast?lat=53.194304&lon=50.110218',
        'Тамбов': 'https://api.weather.yandex.ru/v2/forecast?lat=52.707802&lon=41.437512',
        'Казань': 'https://api.weather.yandex.ru/v2/forecast?lat=55.792794&lon=49.114206',
        'Екатеринбург': 'https://api.weather.yandex.ru/v2/forecast?lat=56.828866&lon=60.588062',
    }
    con = {'clear': 'ясно', 'partly-cloudy': 'малооблачно',
           'cloudy': 'облачно с прояснениями', 'snow-showers': 'снегопад',
           'overcast': 'пасмурно', 'drizzle': 'морось', 'hail': 'град',
           'light-rain': 'небольшой дождь', 'rain': 'дождь',
           'moderate-rain': 'умеренно сильный дождь',
           'continuous-heavy-rain': 'длительный сильный дождь',
           'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег',
           'snow': 'снег', 'thunderstorm-with-hail': 'гроза с градом',
           'thunderstorm': 'гроза', 'showers': 'ливень',
           'thunderstorm-with-rain': 'дождь с грозой',
           'heavy-rain': 'сильный дождь', }
    url = city_url[update.message.text]
    headers = {'X-Yandex-API-Key': os.getenv('KEY_YANDEX')}
    response = requests.get(url, headers=headers)
    date = response.json()['forecasts'][0]['date']
    city = update.message.text
    t = response.json()['fact']['temp']
    t_massage = (f'Текущая температура {t}')
    condition = response.json()['fact']['condition']
    response = f'{date}, {city}, {t_massage}, {con[condition]}'
    return response


def get_new_image():
    try:
        response = requests.get(URL1)
    except Exception as error:
        print(error)
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)
    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def new_cat(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())


def first_menu(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    menu = ReplyKeyboardMarkup([['котофото', 'погода', ],
                                ['курсы валют', 'шутка юмора))']],
                               resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Посмотри, какого котика я тебе нашёл'.format(name),
        reply_markup=menu
    )
    context.bot.send_photo(chat.id, get_new_image())


def weather_menu(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    menu = ReplyKeyboardMarkup([['Ульяновск', 'Москва', 'Питер', 'Тамбов'],
                                ['Самара', 'Казань', 'Екатеринбург', 'Назад']],
                               resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='{}, в каком городе смотрим погоду?'.format(name),
        reply_markup=menu
    )


def hear_you(update, context):
    text = update.message.text
    if text == 'погода':
        weather_menu(update, context)
    elif text in ['Назад', 'котофото']:
        first_menu(update, context)
    elif text in ['Ульяновск', 'Москва', 'Питер',
                  'Тамбов', 'Самара', 'Казань', 'Екатеринбург']:
        send_message(update, context, weather_request(update, context))
    elif text == 'курсы валют':
        send_message(update, context, get_crb_daily())
    elif text == 'шутка юмора))':
        send_message(update, context, get_joke())


def get_crb_daily():
    try:
        response = requests.get(URL2)
    except Exception as error:
        print(error)
    response = response.json()
    context = {1: response['Date'],
               2: response['Valute']['GBP']['Name'],
               3: response['Valute']['GBP']['Value'],
               4: response['Valute']['USD']['Name'],
               5: response['Valute']['USD']['Value'],
               6: response['Valute']['EUR']['Name'],
               7: response['Valute']['EUR']['Value'],
               8: response['Valute']['CNY']['Name'],
               9: response['Valute']['CNY']['Value'], }
    q1 = context[1]
    q2 = context[2]
    q3 = context[3]
    q4 = context[4]
    q5 = context[5]
    q6 = context[6]
    q7 = context[7]
    q8 = context[8]
    q9 = context[9]
    response = f'{q1}\n {q2}  {q3}\n {q4}  {q5}\n {q6}  {q7}\n 10 {q8}  {q9}'
    return response


def send_message(update, context, message):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=message
    )


def main():
    """Основная логика работы бота"""
    updater.dispatcher.add_handler(CommandHandler('start', first_menu))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, hear_you))
    updater.start_polling(poll_interval=5.0)


if __name__ == '__main__':
    main()
