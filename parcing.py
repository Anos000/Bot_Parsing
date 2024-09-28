from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Настройка для работы с Firefox
options = webdriver.FirefoxOptions()
#options.add_argument('--headless')  # Запуск браузера в фоновом режиме (без графического интерфейса)
options.binary_location = "C:\Program Files\Mozilla Firefox/firefox.exe"

# Устанавливаем драйвер для Firefox с использованием webdriver_manager
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

# URL страницы интернет-магазина
url = "https://megamarket.ru/catalog/smartfony-android/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A7714%2C%22max%22%3A9053%7D%7D"  # Замените на реальный URL интернет-магазина

# Открываем страницу
driver.get(url)

# Прокручиваем страницу до конца для подгрузки товаров
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)  # Ждем некоторое время для загрузки контента

'''# Ожидание загрузки элементов (например, карточки товара с классом 'product-item')
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "catalog-item-regular-desktop ddl_product catalog-item-desktop"))  # Замените на актуальный класс товаров
    )
except:
    print("Товары не загрузились!")
    driver.quit()
    exit()'''

# Получаем HTML-код после выполнения JavaScript
html_content = driver.page_source

# Инициализируем BeautifulSoup для парсинга полученного HTML
soup = BeautifulSoup(html_content, 'lxml')

# Находим все товары на странице (замените 'product-item' на реальный класс карточек товаров)
products = soup.find_all('div', class_='catalog-item-regular-desktop ddl_product catalog-item-desktop')

# Проходим по каждому товару и выводим его данные
for product in products:
    # Извлекаем название товара (замените на реальный селектор)
    title = product.find('a', class_='catalog-item-regular-desktop__title-link ddl_product_link').text.strip()  # Пример: используйте правильный тег и класс

    # Извлекаем цену товара (замените на реальный селектор)
    price = product.find('div', class_='catalog-item-regular-desktop__price').text.strip()  # Пример: используйте правильный тег и класс

    # Извлекаем ссылку на товар (замените на реальный селектор)
    link = product.find('a', class_='catalog-item-regular-desktop__title-link ddl_product_link')['href']  # Пример: используйте правильный тег и класс

    # Выводим данные о товаре
    print(f"Название: {title}, Цена: {price}, Ссылка: https://megamarket.ru{link}")

# Закрываем браузер
driver.quit()