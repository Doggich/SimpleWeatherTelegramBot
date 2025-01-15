import os
from telebot import TeleBot, types
import datetime
from dotenv import load_dotenv, find_dotenv
import pytz
import requests
import pprint

load_dotenv(find_dotenv())


def unix_to_datetime(unix_timestamp: int, timezone: str = 'UTC') -> str:
    return datetime.datetime.fromtimestamp(unix_timestamp, tz=pytz.timezone(timezone))


def get_weather(city: str, api_key: str) -> dict:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={api_key}"
    try:
        weather_data = requests.get(url).json()
        return weather_data
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


TOKEN: str = os.getenv("TOKEN")
API_KEY: str = os.getenv("OPENWEATHER_API_KEY")

bot: TeleBot = TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def welcome_msg(msg: types.Message) -> None:

    if msg.from_user.last_name:
        bot.send_message(msg.chat.id,
                         f"Hello, {msg.from_user.first_name} {msg.from_user.last_name} (<b><i>{msg.from_user.username}</i></b>).\n"
                         f"In this bot, you can view the weather in any city.",
                         parse_mode="HTML")
    else:
        bot.send_message(msg.chat.id,
                         f"Hello, {msg.from_user.first_name}(<b><i>{msg.from_user.username}</i></b>).\n"
                         f"In this bot, you can view the weather in any city.",
                         parse_mode="HTML")


@bot.message_handler(commands=["weather"])
def ask_for_city(msg: types.Message) -> None:
    bot.send_message(msg.chat.id, "Input the city name:")


@bot.message_handler(content_types=['text'])
def handle_city_input(msg: types.Message) -> None:
    if msg.text.lower() not in ["/start", "/weather"]:
        city = msg.text
        weather_data = get_weather(city, API_KEY)
        try:
            if weather_data:
                main_data = weather_data['main']
                weather_description = weather_data['weather'][0]['description'].capitalize()
                sunrise = unix_to_datetime(weather_data['sys']['sunrise'], 'UTC').strftime("%H:%M:%S")
                sunset = unix_to_datetime(weather_data['sys']['sunset'], 'UTC').strftime("%H:%M:%S")
                message = f"Weather in <u>{city.capitalize()}</u>:\n" \
                          f"Temperature: {main_data['temp']}°C\n" \
                          f"Feels like: {main_data['feels_like']}°C\n" \
                          f"Humidity: {main_data['humidity']}%\n" \
                          f"Pressure: {main_data['pressure']} hPa\n" \
                          f"Weather: {weather_description}\n" \
                          f"Sunrise: {sunrise}\n" \
                          f"Sunset: {sunset}"
                bot.send_message(msg.chat.id, message,  parse_mode="HTML")
            else:
                bot.send_message(msg.chat.id, "Could not retrieve weather data. Please check the city name.")
        except Exception:
            bot.send_message(msg.chat.id, "Could not retrieve weather data. Please check the city name.")


bot.polling()
