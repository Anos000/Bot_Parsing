# your_script.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
import pytz
import re

# Настройка для работы с Chrome
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Запуск браузера в фоновом режиме
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Устанавливаем драйвер для Chrome с использованием webdriver_manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL страницы интернет-магазина
url = "https://avtobat36.ru/catalog/gaz_1/"
driver.get(url)
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'lxml')

# Находим номер последней страницы
pages = soup.find('div', class_='bx_pagination_page').find_all('li')
last_page = int(pages[-2].text.strip())

# Создаем список для хранения данных
parsed_data = []

# Проходим по страницам от 1 до last_page
for page in range(1, last_page + 1):
    page_url = f"https://avtobat36.ru/catalog/gaz_1/?PAGEN_2={page}"
    driver.get(page_url)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'lxml')

    products = soup.find_all('div', class_=re.compile(r'catalog-section-item sec_item itm_'))
    print(f"Страница {page}: найдено товаров {len(products)}")

    # Текущая дата и время в вашем часовом поясе (UTC+3)
    tz = pytz.timezone("Europe/Moscow")
    current_date = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

    for product in products:
        try:
            # Проверяем наличие элемента перед извлечением текста
            title_element = product.find('a', class_='d-lnk-txt')
            title = title_element.text.strip() if title_element else "Нет названия"

            price_element = product.find('span', class_='js-price')
            price = price_element.text.strip() if price_element else 'Необходимо уточнять'

            number_element = product.find('div', class_='sec_params d-note')
            number = number_element.text.strip().split()[1] if number_element else "Нет артикула"

            link_element = product.find('a', class_='d-lnk-txt')
            link = link_element['href'] if link_element else "Нет ссылки"

            parsed_data.append({
                "Дата парсинга": current_date,
                "Название": title,
                "Артикул": number,
                "Цена": price,
                "Ссылка": f"https://avtobat36.ru{link}"
            })
        except Exception as e:
            print(f"Ошибка при обработке товара: {e}")

# Сохраняем данные в Excel, добавляя их в существующий файл
downloads_dir = "downloads"
os.makedirs(downloads_dir, exist_ok=True)
excel_file = os.path.join(downloads_dir, "parsed_data.xlsx")

# Объединяем данные, если файл уже существует
try:
    if os.path.exists(excel_file):
        existing_df = pd.read_excel(excel_file, engine='openpyxl')
        df = pd.concat([existing_df, pd.DataFrame(parsed_data)], ignore_index=True)
    else:
        df = pd.DataFrame(parsed_data)

    df.to_excel(excel_file, index=False)
    print(f"Данные успешно сохранены и обновлены в {excel_file}")

except ValueError as e:
    print(f"Ошибка при чтении файла Excel: {e}. Создаем новый файл...")
    df = pd.DataFrame(parsed_data)
    df.to_excel(excel_file, index=False)

driver.quit()
