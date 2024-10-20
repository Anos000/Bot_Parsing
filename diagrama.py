import pandas as pd
import matplotlib.pyplot as plt
import os
import re  # Импортируем модуль для регулярных выражений


# Функция для очистки цен, оставляя только числа
def clean_price(price):
    if isinstance(price, str):
        # Убираем все символы, кроме цифр и десятичной точки
        price = re.sub(r'[^\d.]', '', price)
    return float(price) if price else None


# Функция для поиска артикулов в файлах и построения графиков
def plot_price_history_by_articul(articul):
    # Список файлов Excel для поиска с указанием имён
    excel_files = [
        ("downloads/parsed_data.xlsx", "File 1"),
        ("downloads/parsed_data2.xlsx", "File 2"),
        ("downloads/parsed_data_autoopt.xlsx", "File 3")
    ]

    # Словарь для хранения данных по каждому файлу
    data_by_file = {}

    # Проход по каждому файлу
    for file_name, label in excel_files:
        if os.path.exists(file_name):
            df = pd.read_excel(file_name)

            # Проверяем наличие необходимых колонок
            if 'Артикул' in df.columns and 'Цена' in df.columns and 'Дата парсинга' in df.columns:
                # Фильтрация данных по артикулу и создание копии для предотвращения SettingWithCopyWarning
                articul_data = df[df['Артикул'] == articul].copy()

                if not articul_data.empty:
                    print(f"Найден артикул {articul} в файле {file_name}")
                    # Очищаем цены
                    articul_data['Цена'] = articul_data['Цена'].apply(clean_price)

                    # Фильтруем данные, оставляя только непустые цены
                    articul_data = articul_data[articul_data['Цена'].notnull()]

                    if not articul_data.empty:
                        # Сохраняем данные для каждого файла
                        data_by_file[label] = articul_data[['Дата парсинга', 'Цена']]

    # Если данные найдены, строим графики
    if data_by_file:
        for source, data in data_by_file.items():
            data['Дата парсинга'] = pd.to_datetime(data['Дата парсинга'])  # Преобразуем даты

            # Сортируем по дате
            data = data.sort_values(by='Дата парсинга')

            # Построение графика для каждого источника данных
            plt.figure(figsize=(12, 8))
            plt.plot(data['Дата парсинга'], data['Цена'], marker='o', label=source)
            plt.title(f'Изменение цен для артикула {articul} в {source}')
            plt.xlabel('Дата')
            plt.ylabel('Цена')
            plt.xticks(rotation=45, ha='right')  # Поворот подписей по оси X для читаемости
            plt.grid()
            plt.legend()
            plt.tight_layout()

            # Сохранение графика в виде файла
            graph_file = f"downloads/price_history_{articul}_{source}.png"
            plt.savefig(graph_file)
            plt.show()
            print(f"График сохранен: {graph_file}")
    else:
        print(f"Артикул {articul} не найден в файлах.")


# Пример использования функции
plot_price_history_by_articul('020005216')
