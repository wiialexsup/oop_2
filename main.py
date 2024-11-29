import csv
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict


class FileProcessor:
    """Класс для чтения и обработки данных из файлов."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = []

    def read_file(self):
        """Определяет тип файла и вызывает соответствующий метод чтения."""
        if self.file_path.endswith('.csv'):
            self.data = self._read_csv_file()
        elif self.file_path.endswith('.xml'):
            self.data = self._read_xml_file()
        else:
            raise ValueError("Неверный формат файла. Поддерживаются только CSV и XML.")

    def _read_csv_file(self):
        """Чтение данных из CSV-файла."""
        data = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    clean_row = {k.strip(): v.strip() for k, v in row.items()}
                    data.append(clean_row)
        except Exception as e:
            raise RuntimeError(f"Ошибка при чтении файла CSV: {e}")
        return data

    def _read_xml_file(self):
        """Чтение данных из XML-файла."""
        data = []
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            for item in root.findall('item'):
                record = {k: v for k, v in item.attrib.items()}
                data.append(record)
        except Exception as e:
            raise RuntimeError(f"Ошибка при чтении файла XML: {e}")
        return data

    def process_data(self):
        """Обработка данных: поиск дубликатов и подсчет этажности зданий."""
        duplicates = self._find_duplicates()
        city_summary = self._count_floors_by_city()
        return duplicates, city_summary

    def _find_duplicates(self):
        """Поиск дубликатов в данных."""
        duplicates = Counter(
            tuple(sorted((k, v if v is not None else "null") for k, v in item.items()))
            for item in self.data
        )
        return [
            {k: v for k, v in record} for record, count in duplicates.items() if count > 1
        ]

    def _count_floors_by_city(self):
        """Подсчет зданий по этажности в разрезе городов."""
        city_summary = defaultdict(lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
        for record in self.data:
            city = record.get("city")
            floors = record.get("floor") or record.get("floors")
            if city and floors and floors.isdigit():
                city_summary[city][int(floors)] += 1
        return city_summary


class Application:
    """Класс для управления взаимодействием с пользователем."""

    @staticmethod
    def display_statistics(duplicates, city_summary, processing_time):
        """Выводит обработанную статистику."""
        print("\nСводная статистика:")

        print("\n1) Дублирующиеся записи:")
        if duplicates:
            for record in duplicates:
                print(f"Запись: {record}")
        else:
            print("Дубликатов не обнаружено.")

        print("\n2) Количество зданий по этажности в городах:")
        for city, summary in city_summary.items():
            print(f"{city}: {summary}")

        print(f"\n3) Время обработки файла: {processing_time:.2f} секунд.")

    def run(self):
        """Запускает основной цикл программы."""
        print("Добро пожаловать! Для завершения введите 'exit'.")

        while True:
            file_path = input("\nВведите путь к файлу-справочнику: ").strip()

            if file_path.lower() == 'exit':
                print("Завершение работы программы.")
                break

            try:
                processor = FileProcessor(file_path)
                start_time = time.time()

                processor.read_file()
                duplicates, city_summary = processor.process_data()

                processing_time = time.time() - start_time
                self.display_statistics(duplicates, city_summary, processing_time)

            except Exception as e:
                print(f"Ошибка: {e}")


if __name__ == "__main__":
    app = Application()
    app.run()