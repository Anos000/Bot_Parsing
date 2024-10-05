import telebot
from telebot import types
import os
import subprocess

bot = telebot.TeleBot('7702548527:AAH-xkmHniF9yw09gDtN_JX7tleKJLJjr4E')  # Замените на свой токен бота

# Функция для обновления файла Excel из репозитория
def update_excel_file():
    try:
        # Обновление репозитория
        subprocess.run(["git", "pull"], check=True)
        print("Файл Excel обновлен из репозитория.")
    except subprocess.CalledProcessError:
        print("Ошибка при обновлении файла Excel.")

# Приветственное сообщение с меню
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Получить данные")
    item2 = types.KeyboardButton("Информация о боте")
    item3 = types.KeyboardButton("Контакты")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Привет! Выберите опцию из меню:", reply_markup=markup)

# Обработчик текста
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Получить данные":
        bot.send_message(message.chat.id, "Загружаю последние данные...")

        # Обновляем Excel файл
        update_excel_file()

        excel_file = "downloads/parsed_data.xlsx"  # Путь к файлу

        try:
            if os.path.exists(excel_file):
                with open(excel_file, 'rb') as file:
                    bot.send_document(message.chat.id, file)
                bot.send_message(message.chat.id, "Вот ваши данные!")
            else:
                bot.send_message(message.chat.id, "Файл с данными не найден.")
        except Exception as e:
            bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

    elif message.text == "Информация о боте":
        bot.send_message(message.chat.id, "Этот бот парсит данные с веб-сайта и отправляет их в формате Excel.")
    elif message.text == "Контакты":
        bot.send_message(message.chat.id, "Связаться с нами можно по адресу: example@example.com")
    else:
        bot.send_message(message.chat.id, "Выберите опцию из меню.")

# Запуск бота
bot.polling(none_stop=True, interval=0)
