from os.path import split
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
from datetime import datetime  # Для добавления текущей даты
import re

def parse_and_save_to_excel():
    # Настройка для работы с Firefox
    options = webdriver.FirefoxOptions()

    #options.add_argument('--headless')  # Запуск браузера в фоновом режиме (без графического интерфейса)
    options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"

    # Устанавливаем драйвер для Firefox с использованием webdriver_manager
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    # URL страницы интернет-магазина
    url = "https://avtobat36.ru/catalog/gaz_1/"

    # Открываем страницу
    driver.get(url)

    # Получаем HTML-код после выполнения JavaScript
    html_content = driver.page_source

    # Инициализируем BeautifulSoup для парсинга полученного HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # Находим номер последней страницы
    pages = soup.find('div', class_='bx_pagination_page').find_all('li')
    last_page = int(pages[-2].text.strip())

    for page in range(2, last_page+2):

        # Открываем страницу
        driver.get(url)

        # Получаем HTML-код после выполнения JavaScript
        html_content = driver.page_source

        # Инициализируем BeautifulSoup для парсинга полученного HTML
        soup = BeautifulSoup(html_content, 'lxml')

        # Находим все товары на странице
        products = soup.find_all('div', class_=re.compile(r'catalog-section-item sec_item itm_'))

        # Создаем список для сохранения данных
        parsed_data = []

        # Текущая дата и время
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Проходим по каждому товару и извлекаем данные
        for product in products:
            # Извлекаем название товара
            title = product.find('a', class_='d-lnk-txt').text.strip()

            # Извлекаем цену товара
            try: price = product.find('span', class_='js-price').text.strip()
            except: price = 'Необходимо уточнять'

            # Извлекаем артикул товара
            number = product.find('div', class_='sec_params d-note').text.strip().split()[1]

            # Извлекаем ссылку на товар
            link = product.find('a', class_='d-lnk-txt')['href']

            # Сохраняем данные о товаре с датой парсинга
            parsed_data.append({
                "Дата парсинга": current_date,  # Добавляем дату парсинга
                "Название": title,
                "Артикул": number,
                "Цена": price,
                "Ссылка": f"https://avtobat36.ru{link}"
            })

        # Преобразуем данные в DataFrame
        df = pd.DataFrame(parsed_data)

        # Определяем путь для сохранения в папке "downloads"
        downloads_dir = "downloads"
        os.makedirs(downloads_dir, exist_ok=True)  # Создаем папку, если она не существует
        excel_file = os.path.join(downloads_dir, "parsed_data.xlsx")

        # Если файл существует, то добавляем данные, иначе создаем новый файл
        if os.path.exists(excel_file):
            with pd.ExcelWriter(excel_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
        else:
            df.to_excel(excel_file, index=False)

        # Назначаем ссылку на нужную страницу
        url = f"https://avtobat36.ru/catalog/gaz_1/?PAGEN_2={page}"

    driver.quit()

    return excel_file

print(parse_and_save_to_excel())