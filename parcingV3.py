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

# Основной URL страницы
base_url = "https://www.autoopt.ru/catalog/otechestvennye_gruzoviki?pageSize=100&PAGEN_1="

# Список для хранения данных о товарах
parsed_data = []

# Открываем первую страницу, чтобы получить общее количество товаров
driver.get(f"{base_url}1")
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'lxml')

# Извлекаем общее количество товаров
total_products_element = soup.find('div', class_='row mt-4 mb-4').find('span', class_='bold')

if total_products_element:
    total_products = int(total_products_element.text.strip())
    print(f"Всего товаров: {total_products}")
else:
    print("Не удалось получить общее количество товаров.")
    total_products = 0

# Рассчитываем количество страниц
products_per_page = 100
total_pages = (total_products // products_per_page) + (1 if total_products % products_per_page > 0 else 0)
print(f"Страниц для парсинга: {total_pages}")

# Функция для парсинга одной страницы
def parse_page(page_number):
    try:
        url = f"{base_url}{page_number}"
        print(f"Парсим страницу {page_number}: {url}")

        # Открываем страницу
        driver.get(url)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'lxml')

        # Находим все товары на странице
        products = soup.find_all('div', class_='n-catalog-item relative grid-item n-catalog-item__product')

        if not products:
            print(f"Товары на странице {page_number} не найдены.")
            return []  # Если товаров нет, возвращаем пустой список

        # Текущая дата и время
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Извлекаем информацию о каждом товаре
        parsed_data_page = []
        for product in products:
            try:
                # Название товара
                title = product.find('a', class_='n-catalog-item__name-link').text.strip()

                # Поиск цены товара
                price_elements = product.find_all('span', class_=re.compile(r'bold price-item.*'))
                price = price_elements[0].text.strip() if price_elements else 'Необходимо уточнять'

                # Артикул товара
                articule = product.find('div', class_='n-catalog-item__article')
                number = articule.find('span', class_='string bold nowrap n-catalog-item__click-copy n-catalog-item__ellipsis').text.strip() if articule.find('span', class_='string bold nowrap n-catalog-item__click-copy n-catalog-item__ellipsis') else 'Артикул не найден'

                # Ссылка на товар
                link = product.find('a', class_='n-catalog-item__name-link')['href']

                # Сохранение данных
                parsed_data_page.append({
                    "Дата парсинга": current_date,
                    "Название": title,
                    "Артикул": number,
                    "Цена": price,
                    "Ссылка": f"https://www.autoopt.ru{link}"
                })
            except Exception as e:
                print(f"Ошибка при обработке товара: {e}")

        return parsed_data_page

    except Exception as e:
        print(f"Ошибка при обработке страницы {page_number}: {e}")
        return []

# Функция для последовательного парсинга страниц
def parse_all_pages():
    page_number = 1
    while page_number <= total_pages:
        try:
            # Парсим текущую страницу
            data = parse_page(page_number)
            if not data:
                print(f"Парсинг завершен на странице {page_number}.")
                break  # Если данные пустые, прекращаем парсинг
            parsed_data.extend(data)
            page_number += 1  # Переходим к следующей странице
        except Exception as e:
            print(f"Ошибка при обработке страницы {page_number}: {e}")
            break  # Прекращаем при ошибке

# Запуск парсинга всех страниц
parse_all_pages()

# Проверка на изменения и сохранение данных
downloads_dir = "downloads"
os.makedirs(downloads_dir, exist_ok=True)
excel_file = os.path.join(downloads_dir, "parsed_data_autoopt.xlsx")

# Получаем дату вчерашнего дня
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# Инициализация new_df
new_df = pd.DataFrame(parsed_data)

# Проверка на наличие данных за вчерашний день
if os.path.exists(excel_file):
    existing_df = pd.read_excel(excel_file, engine='openpyxl')

    # Фильтруем данные за вчерашний день
    existing_df_yesterday = existing_df[existing_df['Дата парсинга'].str.contains(yesterday)]

    # Проверяем на изменения по сравнению с данными за вчерашний день
    if not existing_df_yesterday.equals(new_df):
        # Если есть изменения, добавляем все новые данные в файл
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_excel(excel_file, index=False)
        print(f"Данные успешно обновлены в {excel_file}")
    else:
        print("Нет изменений, данные не обновляются.")
else:
    # Если файла не существует, создаем новый
    new_df.to_excel(excel_file, index=False)
    print(f"Данные успешно сохранены в {excel_file}")

# Закрываем драйвер после завершения парсинга
driver.quit()
