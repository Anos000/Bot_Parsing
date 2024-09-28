from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Настройка для работы с Firefox (можно адаптировать для Яндекс.Браузера)
options = webdriver.FirefoxOptions()
# options.add_argument('--headless')  # Запуск браузера в фоновом режиме (без графического интерфейса)
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"

# Устанавливаем драйвер для Firefox с использованием webdriver_manager
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

# URL страницы интернет-магазина
url = "https://megamarket.ru/catalog/smartfony-android/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A7714%2C%22max%22%3A11000%7D%7D"  # Пример: URL магазина с фильтрацией товаров

# Открываем первую страницу
driver.get(url)

# Функция для прокрутки страницы вниз и ожидания полной загрузки товаров
def scroll_and_load(driver):
    scroll_pause_time = 5
    max_scroll_attempts = 10
    scroll_attempts = 0

    while scroll_attempts < max_scroll_attempts:
        # Прокрутка страницы вниз
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        try:
            # Проверка наличия товаров на странице
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "catalog-item-regular-desktop"))
            )
            break
        except Exception:
            print(f"Попытка прокрутки {scroll_attempts + 1} не удалась, продолжаем...")
        scroll_attempts += 1

    if scroll_attempts == max_scroll_attempts:
        print("Не удалось загрузить все товары после нескольких попыток.")
        driver.quit()
        exit()

# Функция для получения данных о товарах на текущей странице
def get_products(soup):
    products = soup.find_all('div', class_='catalog-item-regular-desktop ddl_product catalog-item-desktop')
    n = 0
    for product in products:
        n+=1
        # Извлекаем название товара
        title = product.find('a', class_='catalog-item-regular-desktop__title-link ddl_product_link').text.strip()

        # Извлекаем цену товара
        price = product.find('div', class_='catalog-item-regular-desktop__price').text.strip()

        # Извлекаем ссылку на товар
        link = product.find('a', class_='catalog-item-regular-desktop__title-link ddl_product_link')['href']

        # Выводим данные о товаре
        print(f"{n} Название: {title}, Цена: {price}, Ссылка: https://megamarket.ru{link}")

# Основной цикл для перехода по страницам
while True:
    # Прокрутка и ожидание загрузки товаров
    scroll_and_load(driver)

    # Получаем HTML текущей страницы
    html_content = driver.page_source

    # Инициализируем BeautifulSoup для парсинга страницы
    soup = BeautifulSoup(html_content, 'lxml')

    # Сбор данных о товарах
    get_products(soup)

    # Ищем кнопку для перехода на следующую страницу
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'btn-cloudy xl catalog-items-list__show-more')

        # Проверяем, активна ли кнопка "Следующая страница"
        if 'disabled' in next_button.get_attribute('class'):
            print("Все страницы обработаны.")
            break

        # Кликаем по кнопке "Следующая страница" для перехода
        next_button.click()
        time.sleep(5)  # Ждем загрузки следующей страницы

    except Exception as e:
        print("Кнопка для перехода на следующую страницу не найдена или страницы закончились.")
        break  # Выходим из цикла, если страницы закончились

# Закрываем браузер
driver.quit()
