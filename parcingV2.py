from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime, timedelta
import pytz
import re
import time

# Настройка для работы с Chrome
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Запуск браузера в фоновом режиме
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Устанавливаем драйвер для Chrome с использованием webdriver_manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL страницы интернет-магазина
url = "https://vapkagro.ru/catalog/avtomobilnye-zapchasti/?PAGEN_1=1&SIZEN_1=12"
driver.get(url)

# Получаем HTML-код после выполнения JavaScript
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'lxml')

# Извлекаем список всех ссылок на страницы
pagination = soup.find('ul', class_='bx_pagination_page_list_num')
if pagination:
    last_page = int(pagination.find_all('a')[-1].text.strip())
else:
    last_page = 1  # Если нет пагинации, предполагаем, что только одна страница

print(f"Найдено страниц: {last_page}")

# Создаем список для сохранения данных
parsed_data = []

# Цикл по всем страницам
for page in range(1, last_page + 1):
    print(f"Парсим страницу: {page}")  # Выводим номер текущей страницы
    driver.get(f"https://vapkagro.ru/catalog/avtomobilnye-zapchasti/?PAGEN_1={page}&SIZEN_1=12")  # Переходим на следующую страницу

    # Ожидание для загрузки контента
    time.sleep(2)  # Задержка для прогрузки страницы

    # Получаем HTML-код после выполнения JavaScript
    html_content = driver.page_source

    # Инициализируем BeautifulSoup для парсинга полученного HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # Находим все товары на странице
    products = soup.find_all('div', class_='product-item-container tiles')

    if not products:
        print(f"Нет товаров на странице {page}, пропускаем страницу.")
        continue

    # Текущая дата и время
    tz = pytz.timezone("Europe/Moscow")
    current_date = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

    # Проходим по каждому товару и извлекаем данные
    for product in products:
        try:
            # Извлекаем название товара
            title = product.find('div', class_='name')['title'].strip()

            # Извлекаем цену товара
            try:
                price = product.find('span', id=re.compile(r'bx_\w+_price')).text.strip()
            except:
                price = 'Необходимо уточнять'

            # Извлекаем ссылку на товар
            link = product.find('div', class_='product_item_title').find('a')['href']
            driver.get(f"https://vapkagro.ru{link}")  # Переходим на страницу с товаром для извлечения артикула

            time.sleep(1)  # Ожидание для загрузки страницы

            # Инициализируем BeautifulSoup для страницы с артикулом
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'lxml')

            # Находим артикул
            details = soup.find('div', class_='product-item-detail-tabs').find_all('li', class_='product-item-detail-properties-item')
            number = 'Артикул не найден'
            for detail in details:
                if detail.find('span', class_='product-item-detail-properties-name').text.strip() == 'Артикул':
                    number = detail.find('span', class_='product-item-detail-properties-value').text.strip()
                    break

            print(title, number, price)

            # Сохраняем данные о товаре с датой парсинга
            parsed_data.append({
                "Дата парсинга": current_date,  # Добавляем дату парсинга
                "Название": title,
                "Артикул": number,
                "Цена": price,
                "Ссылка": f"https://vapkagro.ru{link}"
            })

        except Exception as e:
            print(f"Ошибка при обработке товара: {e}")

# Преобразование списка в DataFrame
new_data = pd.DataFrame(parsed_data)

# Путь к файлу Excel
downloads_dir = "downloads"
os.makedirs(downloads_dir, exist_ok=True)
excel_file = os.path.join(downloads_dir, "parsed_data2.xlsx")

# Получаем дату вчерашнего дня
yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

# Проверка на изменения только за вчерашний день
if os.path.exists(excel_file):
    existing_df = pd.read_excel(excel_file, engine='openpyxl')

    # Фильтруем данные за вчерашний день
    yesterday_data = existing_df[existing_df['Дата парсинга'].str.contains(yesterday)]

    # Проверяем на изменения: сравнение по артикулу и цене с данными за вчерашний день
    merged_df = pd.merge(new_data, yesterday_data, on='Артикул', how='left', suffixes=('_new', '_old'))
    changes = merged_df[(merged_df['Цена_new'] != merged_df['Цена_old']) | merged_df['Цена_old'].isna()]

    if not changes.empty:
        # Если хотя бы одно изменение есть, добавляем ВСЕ новые данные в файл (даже дубликаты)
        combined_df = pd.concat([existing_df, new_data], ignore_index=True)
        combined_df.to_excel(excel_file, index=False)
        print(f"Данные успешно обновлены в {excel_file}")
    else:
        print("Нет изменений, данные не обновляются.")
else:
    # Если файла не существует, создаем новый
    new_data.to_excel(excel_file, index=False)
    print(f"Данные успешно сохранены в {excel_file}")

driver.quit()
