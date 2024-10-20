import telebot
from telebot import types
import os
import subprocess
import threading
from diagrama import plot_price_history_by_articul  # Импорт функции из другого файла

bot = telebot.TeleBot('7702548527:AAH-xkmHniF9yw09gDtN_JX7tleKJLJjr4E')  # Замените на свой токен бота

# Глобальная переменная для отслеживания состояния
stop_event = threading.Event()
is_plotting = False  # Флаг для отслеживания процесса построения графика

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
    item3 = types.KeyboardButton("Динамика цены товара")
    item4 = types.KeyboardButton("Информация о боте")
    item5 = types.KeyboardButton("Контакты")
    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(message.chat.id, "Привет! Выберите опцию из меню:", reply_markup=markup)

# Обработчик текста
@bot.message_handler(content_types=['text'])
def handle_text(message):
    global stop_event, is_plotting  # Используем глобальные переменные

    # Если пользователь нажимает другую кнопку, останавливаем процесс
    if is_plotting:
        stop_event.set()  # Устанавливаем событие, чтобы остановить процесс построения графика
        is_plotting = False  # Сбрасываем флаг

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

    elif message.text == "Динамика цены товара":
        bot.send_message(message.chat.id, "Пожалуйста, введите артикул товара:")
        bot.register_next_step_handler(message, process_articul)  # Регистрируем следующий шаг для обработки артикула

    elif message.text.startswith("Excel:"):
        file_name_map = {
            "Excel: Parsed Data": "parsed_data.xlsx",
            "Excel: Parsed Data Autoopt": "parsed_data_autoopt.xlsx",
            "Excel: Parsed Data Vapkagro": "parsed_data2.xlsx"
        }
        file_name = file_name_map.get(message.text)
        output_excel_file = f"downloads/{file_name}"

        if os.path.exists(output_excel_file):
            with open(output_excel_file, 'rb') as file:
                bot.send_document(message.chat.id, file)
            bot.send_message(message.chat.id, "Вот файл Excel!")
        else:
            bot.send_message(message.chat.id, f"Файл {output_excel_file} не найден.")

    elif message.text.startswith("Docx:"):
        file_name_map = {
            "Docx: Parsed Data": "parsed_data_products.docx",
            "Docx: Parsed Data Autoopt": "parsed_data_autoopt_products.docx",
            "Docx: Parsed Data Vapkagro": "parsed_data2_products.docx"
        }
        file_name = file_name_map.get(message.text)
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
        bot.send_message(message.chat.id,
                         "Связаться с нами можно по почте: krutskih.nikita04@gmail.com или forever777007007007@gmail.com")

def process_articul(message):
    global stop_event, is_plotting  # Используем глобальные переменные

    articul = message.text.strip()  # Получаем артикул от пользователя
    bot.send_message(message.chat.id, f"Получен артикул: {articul}. Запускаю функцию для построения графика...")

    stop_event.clear()  # Сбрасываем событие, чтобы разрешить выполнение функции
    is_plotting = True  # Устанавливаем флаг, что построение графика идет

    # Передаем chat_id и bot в функцию для построения графика
    threading.Thread(target=run_plotting, args=(articul, message.chat.id, bot)).start()

def run_plotting(articul, chat_id, bot):
    try:
        plot_price_history_by_articul(articul, chat_id, bot)
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {e}")
    finally:
        is_plotting = False  # Сбрасываем флаг после завершения

# Запуск бота
bot.polling(none_stop=True, interval=0)
