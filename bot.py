import telebot
from telebot import types
import os
from parcing import parse_and_save_to_excel  # Импортируем функцию для парсинга

bot = telebot.TeleBot('7702548527:AAH-xkmHniF9yw09gDtN_JX7tleKJLJjr4E')  # Замените на свой токен бота


# Приветственное сообщение с меню
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создаем объект клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Добавляем кнопки
    item1 = types.KeyboardButton("Начать парсинг")
    item2 = types.KeyboardButton("Информация о боте")
    item3 = types.KeyboardButton("Контакты")

    markup.add(item1, item2, item3)

    # Отправляем приветственное сообщение с кнопками
    bot.send_message(message.chat.id, "Привет! Выберите опцию из меню:", reply_markup=markup)


# Обработчик текста
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Начать парсинг":
        bot.send_message(message.chat.id, "Начинаем парсинг... Это может занять некоторое время.")

        try:
            # Вызываем функцию парсинга и получаем путь к Excel файлу
            excel_file = parse_and_save_to_excel()

            # Отправляем файл пользователю
            with open(excel_file, 'rb') as file:
                bot.send_document(message.chat.id, file)

            # Сообщаем об успешном завершении
            bot.send_message(message.chat.id, "Парсинг завершен! Вот ваш Excel файл.")

        except Exception as e:
            bot.send_message(message.chat.id, f"Произошла ошибка при парсинге: {e}")

    elif message.text == "Информация о боте":
        bot.send_message(message.chat.id, "Этот бот парсит данные с веб-сайта и отправляет их в формате Excel.")

    elif message.text == "Контакты":
        bot.send_message(message.chat.id, "Связаться с нами можно по адресу: krutskih.nikita04@gmail.com")

    else:
        bot.send_message(message.chat.id, "Выберите опцию из меню.")


# Запуск бота
bot.polling(none_stop=True, interval=0)
