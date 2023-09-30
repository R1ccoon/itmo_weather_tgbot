import asyncio
import logging
import sys
from os import getenv
import requests
import json
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.markdown import hbold

# Bot token
TOKEN = '5914681142:AAFz6D3bxgN77N-_GyugbsDEU7U86UtfWY8'
API_KEY_WEATHER = '3250e945-fe18-483c-b9cd-64739ae20b3e'
API_KEY_GEOCODER = '5f501b63-28dc-47a7-ad50-d449ead41042'
# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
builder = ReplyKeyboardBuilder()
cities = ['Москва', 'Санкт-Петербург', 'Сочи', 'Казань']
for index in cities:
    builder.button(text=f"{index}")
builder.adjust(2, 2)
DICT_WEATHER = {
    'clear': 'ясно.',
    'partly-cloudy': 'малооблачно.',
    'cloudy': 'облачно с прояснениями.',
    'overcast': 'пасмурно.',
    'light-rain': 'небольшой дождь.',
    'rain': 'дождь.',
    'heavy-rain': 'сильный дождь.',
    'showers': 'ливень.',
    'wet-snow': 'дождь со снегом.',
    'light-snow': 'небольшой снег.',
    'snow': 'снег.',
    'snow-showers': 'снегопад.',
    'hail': 'град.',
    'thunderstorm': 'гроза.',
    'thunderstorm-with-rain': 'дождь с грозой.',
    'thunderstorm-with-hail': 'гроза с градом.'
}


def get_city_coordinates(city):
    # Формируем URL-запрос
    url = f'https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY_GEOCODER}&geocode={city}&format=json'

    try:
        # Отправляем GET-запрос и получаем данные в формате JSON
        response = requests.get(url)
        data = response.json()
        # Получаем координаты города
        pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
        longitude = pos[0]
        latitude = pos[1]
        return get_weather_forecast(latitude, longitude, city)
    except Exception as e:
        m = [f"Не заню такого города("]
        return m


def get_weather_forecast(latitude, longitude, city):
    # Формируем URL-запрос
    url = f'https://api.weather.yandex.ru/v2/forecast?lat={latitude}&lon={longitude}&lang=ru_RU'

    # Заголовок запроса с указанием API-ключа
    headers = {
        'X-Yandex-API-Key': API_KEY_WEATHER
    }

    try:
        # Отправляем GET-запрос и получаем данные в формате JSON
        response = requests.get(url, headers=headers)
        data = response.json()

        # Получаем информацию о погоде
        forecast = data

        temp = forecast['fact']['temp']
        condition = forecast['fact']['condition']
        feels_like = forecast['fact']['feels_like']

        # Выводим данные о погоде
        m = [f'Прогноз погоды в городе {city}:',
             f'Температура: {temp}°C',
             f'Состояние: {DICT_WEATHER[condition]}',
             f'Ощущается как: {feels_like}']
        return m
    except Exception as e:
        m = [f"Произошла ошибка при получении погоды: {str(e)}"]
        return m


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Здравствуйте, {hbold(message.from_user.full_name)}, чтобы узнать погоду "
                         f"выберите свой город или напишите его в сообщение", reply_markup=builder.as_markup())


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    # Send a copy of the received message

    city = message.text
    try:
        for i in get_city_coordinates(city):
            await message.answer(i)


    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Ошибка")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())