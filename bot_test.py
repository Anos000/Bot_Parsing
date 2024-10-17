import telebot
from telebot import types
import os
import subprocess
import pandas as pd
from docx import Document
from datetime import datetime

bot = telebot.TeleBot('7702548527:AAH-xkmHniF9yw09gDtN_JX7tleKJLJjr4E')  # Замените на свой токен бота

# Функция для обновления файлов Excel из репозитория
def update_excel_files():
    try:
        subprocess.run(["git", "pull"], check=True)
        print("Файлы Excel обновлены из репозитория.")
    except subprocess.CalledProcessError:
        print("Ошибка при обновлении файлов Excel.")

# Приветственное сообщение с меню
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Получить Excel файлы")
    item2 = types.KeyboardButton("Получить docx файлы (Список товаров)")
    item3 = types.KeyboardButton("Информация о боте")
    item4 = types.KeyboardButton("Контакты")
    markup.add(item1, item2, item3, item4)
    bot.send_message(message.chat.id, "Привет! Выберите опцию из меню:", reply_markup=markup)

# Обработчик текста
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Получить Excel файлы":
        bot.send_message(message.chat.id, "Загружаю последние данные (Excel файлы)...")
        update_excel_files()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Excel: Parsed Data")
        item2 = types.KeyboardButton("Excel: Parsed Data Autoopt")
        item3 = types.KeyboardButton("Excel: Parsed Data Vapkagro")
        item_back = types.KeyboardButton("Назад")
        markup.add(item1, item2, item3, item_back)

        bot.send_message(message.chat.id, "Выберите Excel файл для загрузки:", reply_markup=markup)

    elif message.text == "Получить docx файлы (Список товаров)":
        bot.send_message(message.chat.id, "Загружаю последние данные (docx файлы со списками товаров)...")
        update_excel_files()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Docx: Parsed Data")
        item2 = types.KeyboardButton("Docx: Parsed Data Autoopt")
        item3 = types.KeyboardButton("Docx: Parsed Data Vapkagro")
        item_back = types.KeyboardButton("Назад")
        markup.add(item1, item2, item3, item_back)

        bot.send_message(message.chat.id, "Выберите docx файл для вывода списка товаров:", reply_markup=markup)

    # Обработка запросов на загрузку Excel файлов
    if message.text == "Excel: Parsed Data":
        file_name = "parsed_data.xlsx"  # Указываем файл Excel
        output_excel_file = f"downloads/{file_name}"

        if os.path.exists(output_excel_file):
            with open(output_excel_file, 'rb') as file:
                bot.send_document(message.chat.id, file)
            bot.send_message(message.chat.id, "Вот файл Excel!")
        else:
            bot.send_message(message.chat.id, f"Файл {output_excel_file} не найден.")

    elif message.text == "Excel: Parsed Data Autoopt":
        file_name = "parsed_data_autoopt.xlsx"  # Указываем файл Excel
        output_excel_file = f"downloads/{file_name}"

        if os.path.exists(output_excel_file):
            with open(output_excel_file, 'rb') as file:
                bot.send_document(message.chat.id, file)
            bot.send_message(message.chat.id, "Вот файл Excel!")
        else:
            bot.send_message(message.chat.id, f"Файл {output_excel_file} не найден.")

    elif message.text == "Excel: Parsed Data Vapkagro":
        file_name = "parsed_data2.xlsx"  # Указываем файл Excel
        output_excel_file = f"downloads/{file_name}"

        if os.path.exists(output_excel_file):
            with open(output_excel_file, 'rb') as file:
                bot.send_document(message.chat.id, file)
            bot.send_message(message.chat.id, "Вот файл Excel!")
        else:
            bot.send_message(message.chat.id, f"Файл {output_excel_file} не найден.")

    # Обработка запросов на загрузку docx файлов
    elif message.text == "Docx: Parsed Data":
        file_name = "parsed_data_products.docx"  # Указываем файл docx
        output_docx_file = f"downloads/{file_name}"

        if os.path.exists(output_docx_file):
            with open(output_docx_file, 'rb') as file:
                bot.send_document(message.chat.id, file)
            bot.send_message(message.chat.id, "Вот список товаров (docx)!")
        else:
            bot.send_message(message.chat.id, f"Файл {output_docx_file} не найден.")

    elif message.text == "Docx: Parsed Data Autoopt":
        file_name = "parsed_data_autoopt_products.docx"  # Указываем файл docx
        output_docx_file = f"downloads/{file_name}"

        if os.path.exists(output_docx_file):
            with open(output_docx_file, 'rb') as file:
                bot.send_document(message.chat.id, file)
            bot.send_message(message.chat.id, "Вот список товаров (docx)!")
        else:
            bot.send_message(message.chat.id, f"Файл {output_docx_file} не найден.")

    elif message.text == "Docx: Parsed Data Vapkagro":
        file_name = "parsed_data2_products.docx"  # Указываем файл docx
        output_docx_file = f"downloads/{file_name}"

        if os.path.exists(output_docx_file):
            with open(output_docx_file, 'rb') as file:
                bot.send_document(message.chat.id, file)
            bot.send_message(message.chat.id, "Вот список товаров (docx)!")
        else:
            bot.send_message(message.chat.id, f"Файл {output_docx_file} не найден.")

    elif message.text == "Назад":
        send_welcome(message)  # Возвращаемся в главное меню

    elif message.text == "Информация о боте":
        bot.send_message(message.chat.id, "Этот бот парсит данные с веб-сайта и отправляет их в формате текста.")
    elif message.text == "Контакты":
        bot.send_message(message.chat.id, "Связаться с нами можно по почте: krutskih.nikita04@gmail.com или forever77700700777@gmail.com")

# Запуск бота
bot.polling(none_stop=True, interval=0)
