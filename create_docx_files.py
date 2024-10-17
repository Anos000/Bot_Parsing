import os
import pandas as pd
from docx import Document

# Функция для создания .docx файла на основе Excel файла
def save_unique_products_to_docx(file_name, output_docx_file):
    excel_file = f"downloads/{file_name}"  # Путь к Excel файлу
    try:
        if os.path.exists(excel_file):
            print(f"Чтение файла: {excel_file}")
            # Читаем данные из Excel файла
            df = pd.read_excel(excel_file)

            print(f"Количество строк в файле: {len(df)}")
            if df.empty:
                print("Файл пуст.")
                return None

            # Проверяем наличие необходимых колонок
            if 'Название' not in df.columns or 'Артикул' not in df.columns:
                print("Файл не содержит необходимых колонок 'Название' или 'Артикул'.")
                return None

            # Убираем дубликаты по колонке "Артикул"
            unique_products = df[['Название', 'Артикул']].drop_duplicates(subset=['Артикул'])
            print(f"Количество уникальных товаров: {len(unique_products)}")

            # Создаем документ .docx
            doc = Document()
            doc.add_heading(f'Список уникальных товаров из {file_name}', 0)

            # Добавляем таблицу в документ
            table = doc.add_table(rows=1, cols=3)
            table.style = 'Table Grid'
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = '№'
            hdr_cells[1].text = 'Название'
            hdr_cells[2].text = 'Артикул'

            # Заполняем таблицу
            for idx, row in enumerate(unique_products.itertuples(), 1):
                row_cells = table.add_row().cells
                row_cells[0].text = str(idx)
                row_cells[1].text = str(row.Название)
                row_cells[2].text = str(row.Артикул)

            # Сохраняем документ
            doc.save(output_docx_file)
            print(f"Документ сохранен: {output_docx_file}")
            return output_docx_file
        else:
            print(f"Файл {excel_file} не найден.")
            return None
    except Exception as e:
        print(f"Ошибка при обработке файла {file_name}: {e}")
        return None

# Список файлов и соответствующих имен для сохранения
files = [
    ("parsed_data.xlsx", "downloads/parsed_data_products.docx"),
    ("parsed_data2.xlsx", "downloads/parsed_data2_products.docx"),
    ("parsed_data_autoopt.xlsx", "downloads/parsed_data_autoopt_products.docx"),
]

# Обработка каждого файла
for excel_file, docx_file in files:
    save_unique_products_to_docx(excel_file, docx_file)
