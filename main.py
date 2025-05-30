# -*- coding: utf-8 -*-
from config.config import URL, BOT_TOKEN
import datetime
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, types, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

# Создаем клавиатуру один раз (глобально)
weather_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Получить погоду 🌤️")]],
    resize_keyboard=True,
    persistent=True  # Сохраняет клавиатуру между сообщениями
)


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==================
# ========== Функция соотношения ветра и направления ==
response = requests.get(URL)
wthr = response.json()
wind_dir = wthr.get('wind', {}).get('deg')



def get_wind_direction(wind_dir):
    directions = {
        (0, 24): "Северный",
        (25, 64): "Северо-Восточный",
        (65, 114): "Восточный",
        (115, 154): "Юго-Восточный",
        (155, 204): "Южный",
        (205, 244): "Юго-Западный",
        (245, 294): "Западный",
        (295, 334): "Северо-Западный",
        (335, 360): "Северный"
    }
    for (min_deg, max_deg), direction in directions.items():
        if min_deg <= wind_dir <= max_deg:
            return direction
    return "неизвестно"


# ======== ФУНКЦИЯ ОПРЕДЕЛЕНИЯ ТРАНСПОРТА ==================

def isAuto(wind_direction_str):
    if wind_direction_str in ("Северный", "Северо-Восточный", "Восточный", "Северо-Западный", "Западный"):
        transport = "на машине"
        return (transport)
    else:
        transport = "на автобусе"
        return transport

#======== ФУНКЦИЯ ДОБАВЛЕНИЯ ИКОНКИ ПОГОДЫ ==================
def get_weather_emoji(icon_code):
    emoji_map = {
        "01d": "☀️",  # ясно (день)
        "01n": "🌙",  # ясно (ночь)
        "02d": "⛅",  # малооблачно (день)
        "02n": "⛅",  # малооблачно (ночь)
        "03d": "☁️",  # облачно
        "03n": "☁️",
        "04d": "☁️",  # пасмурно
        "04n": "☁️",
        "09d": "🌧️",  # дождь
        "09n": "🌧️",
        "10d": "🌦️",  # дождь с солнцем
        "10n": "🌧️",
        "11d": "⛈️",  # гроза
        "11n": "⛈️",
        "13d": "❄️",  # снег
        "13n": "❄️",
        "50d": "🌫️",  # туман
        "50n": "🌫️"
    }
    return emoji_map.get(icon_code, "❓")  # если код неизвестен → "❓"

# ========== ОСНОВНЫЕ ФУНКЦИИ =========================
# ========== ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ =================
@dp.message(CommandStart())
async def handle_start(message: types.Message):
    await message.answer(
        text=f'Привет, {message.from_user.first_name}! Я бот, подсказывающий тебе на чем сегодня лучше добраться до фосфорного комплекса АО "Апатит"\U0001F698\U0001F68C,что бы ЛКП твоего авто не пострадало \U0001F327.',
        reply_markup=weather_kb
    )

# =========== ОТВЕТ НА КОМАНДУ HELP ==================
@dp.message(Command('help'))
async def handle_start(message: types.Message):
    await message.answer(
        text=f'Привет {message.from_user.first_name}, по всем возникающим вопросам или предложениям по улучшению бота напиши в ТГ @EO_Kvashnin'
    )

# ========== ОБРАБОТКА ОТВЕТА ПОЛЬЗОВАТЕЛЯ ===============

@dp.message()
async def get_wheather(message: types.Message):

    # === Подключение к API ===
    response = requests.get(URL)
    wthr = response.json()

    now = datetime.now()

    # === функция для соотношения градусов и направления ветра ===
    wind_direction = get_wind_direction(wind_dir)
    transport = isAuto(wind_direction)

    code_to_smile = {
        'Южный': chr(0x2B06),
        'Северо-Восточный': chr(0x2199),
        'Северо-Западный': chr(0x2198),
        'Юго-Восточный': chr(0x2196),
        'Восточный': chr(0x2B05),
        'Юго-Западный': chr(0x2197),
        'Западный': chr(0x27A1),
        'Северный': chr(0x2B07)
    }

    predlog = ''
    smile = ''
    wind_smile = ''
    sticker_s = ''
    car_emoji = '\U0001F698'
    try:
        # Проверка наличия записей
        if wthr.get('cod') == 200:

            currentDate = now.strftime("%d.%m.%Y %H:%M")
            wind_speed = wthr.get('wind', {}).get('speed')
            city = "Череповец"
            # Получаем температуру и округляем до целого
            temp_c = round(float(wthr.get('main', {}).get('temp'))) if wthr.get('main', {}).get('temp') is not None else 'Нет данных'
            # Получаем иконку погоды
            weather_icon = wthr.get("weather", [{}])[0].get("icon", "")
            weather_emoji = get_weather_emoji(weather_icon)


            if wind_direction in code_to_smile:
                wind_smile = code_to_smile[wind_direction]
            else:
                wind_smile = '\U0001F937'

            if transport == 'на машине':
                predlog = 'можно'
                sticker_s = 'CAACAgUAAxkBAAENVy5nYbcDZNian3GjIKWMjST9mKWfYgAC8gIAAq2uOFebuWyag2LaBjYE'
                smile = '\U0001F6A6\U0001F698'
            else:
                predlog = 'лучше'
                sticker_s = 'CAACAgUAAxkBAAENVyJnYbWosMBxG3jmuD48s3GXswPLbwACqQMAAukKyANqmZZeaEc9pDYE'
                smile = '\U0001F68C\U0001F3C3'

                # Формируем ответ
                # Формируем ответ
                loading_message_1 = await message.reply('Подключаюсь к источнику \U0001F9D0')
                await asyncio.sleep(1.5)
                loading_message_2 = await message.answer(text='Загружаю ответ \U0001F4AD')
                await asyncio.sleep(1.5)
                await bot.delete_message(chat_id=message.chat.id, message_id=loading_message_1.message_id)
                await bot.delete_message(chat_id=message.chat.id, message_id=loading_message_2.message_id)
                await message.answer(
                    text=f'***{city}***\n'
                         f'Погода на {currentDate} {weather_emoji}\n'
                         f'Температура: {temp_c} ℃\n'
                         f'\n'
                         f'{car_emoji * 13}\n'
                         f'Bетер  {wind_smile * 3} {wind_direction} {wind_speed} м/с\n'
                         f'\n'
                         f'{predlog} {transport} {smile}',
                        reply_markup=weather_kb

                )
                await asyncio.sleep(3)
                sticker_message = await bot.send_sticker(chat_id=message.chat.id, sticker=sticker_s)
                await asyncio.sleep(5)
                # Удаляем лишние сообщения

                await bot.delete_message(chat_id=message.chat.id, message_id=sticker_message.message_id)
        else:
            await message.reply("Нет данных для отображения.")

    except:
        await message.reply(f"Произошла ошибка")




async def main():
    logging.basicConfig(level=logging.DEBUG)  # логирование
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
