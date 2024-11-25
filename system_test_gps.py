import unittest

import time


def convert_to_decimal(degree_str, direction):
    """Преобразование строки с градусами в десятичный формат."""
    if not degree_str:  # Проверка на пустую строку
        raise ValueError("Строка с градусами пуста")

    # Преобразование строки в float
    degree_value = float(degree_str)
    degrees = int(degree_value // 100)
    minutes = degree_value % 100
    decimal = degrees + (minutes / 60.0)

    if direction in ['S', 'W']:
        decimal *= -1
    return decimal


def data_gps(gps_data):
    """Обработка данных с GPS.

    Args:
        gps_data: Строка данных в формате NMEA.

    Returns:
        Словарь с обработанными данными:
        - latitude: Широта (градусы).
        - longitude: Долгота (градусы).
        - altitude: Высота (метры).
        - speed: Скорость (м/с).
        - timestamp: Время (секунды).
    """
    try:
        # Разделение строки NMEA по запятым
        data_parts = gps_data.split(",")

        # Проверка на формат GGA
        if data_parts[0] == "$GPGGA":
            # Проверка минимальной длины данных и проверка на пустые поля
            if len(data_parts) < 10 or not data_parts[1] or not data_parts[2] or not data_parts[4] or not data_parts[9]:
                raise ValueError("Недостаточно данных для анализа GGA.")

            timestamp_str = data_parts[1]  # Время фиксируется
            latitude = convert_to_decimal(data_parts[2], data_parts[3])
            longitude = convert_to_decimal(data_parts[4], data_parts[5])
            altitude = float(data_parts[9])
            speed = None  # Скорость недоступна в GGA

            # Форматирование даты для mktime
            current_time = time.localtime()
            year, month, day = current_time.tm_year, current_time.tm_mon, current_time.tm_mday
            timestamp = time.strptime(f"{timestamp_str},{year},{month},{day}", "%H%M%S.%f,%Y,%m,%d")
            timestamp_seconds = time.mktime(timestamp)

        # Проверка на формат RMC для извлечения скорости
        elif data_parts[0] == "$GPRMC":
            # Проверка минимальной длины данных и проверка на пустые поля
            if len(data_parts) < 10 or not data_parts[1] or not data_parts[3] or not data_parts[5]:
                raise ValueError("Недостаточно данных для анализа RMC.")

            timestamp_str = data_parts[1]
            latitude = convert_to_decimal(data_parts[3], data_parts[4])
            longitude = convert_to_decimal(data_parts[5], data_parts[6])
            speed = float(data_parts[7]) * 0.514444 if data_parts[7] else 0.0  # Преобразуем узлы в м/с
            altitude = None  # Высота недоступна в RMC

            # Форматирование даты для mktime
            current_time = time.localtime()
            year, month, day = current_time.tm_year, current_time.tm_mon, current_time.tm_mday
            timestamp = time.strptime(f"{timestamp_str},{year},{month},{day}", "%H%M%S.%f,%Y,%m,%d")
            timestamp_seconds = time.mktime(timestamp)

        else:
            raise ValueError("Неизвестный формат NMEA")

        # Возвращение обработанных данных
        return {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "speed": speed,
            "timestamp": timestamp_seconds
        }

    except Exception as e:
        print("Ошибка при обработке данных GPS:", e)
        return None


#Файл system_test_gps.py

import unittest
from gps_module import data_gps


class TestGPSSystem(unittest.TestCase):

    def test_valid_gga_data(self):
        gps_data_gga = "$GPGGA,123456.78,4916.45,N,12311.12,W,1,12,0.5,30.0,M,0.0,M,,*47"
        expected_output = {
            "latitude": 49 + (16.45 / 60),  # 49.27425
            "longitude": -(123 + (11.12 / 60)),  # -123.18533333333334
            "altitude": 30.0,
            "speed": None,
        }
        output = data_gps(gps_data_gga)

        # Выполнение тестирования
        self.assertAlmostEqual(output["latitude"], expected_output["latitude"], places=7)
        self.assertAlmostEqual(output["longitude"], expected_output["longitude"], places=7)
        self.assertEqual(output["altitude"], expected_output["altitude"])
        self.assertIsNone(output["speed"])

    def test_valid_rmc_data(self):
        gps_data_rmc = "$GPRMC,123519.487,A,3754.587,N,14507.036,W,000.0,360.0,120419,,,D"
        expected_output = {
            "latitude": 37 + (54.587 / 60),  # 37.90978333333333
            "longitude": -(145 + (7.036 / 60)),  # -145.11726666666667
            "altitude": None,
            "speed": 0.0,
        }
        output = data_gps(gps_data_rmc)

        # Выполнение тестирования
        self.assertAlmostEqual(output["latitude"], expected_output["latitude"], places=7)
        self.assertAlmostEqual(output["longitude"], expected_output["longitude"], places=7)
        self.assertIsNone(output["altitude"])
        self.assertEqual(output["speed"], expected_output["speed"])

    def test_invalid_data(self):
        gps_data_invalid = "$GPGGA,12345,,N,,W,1,08,0.9,,,M,46.9,M,,47"
        output = data_gps(gps_data_invalid)
        self.assertIsNone(output)  # Ожидается, что выход будет None

    def test_edge_case(self):
        gps_data_edge_case = "$GPRMC,000000.000,V,0000.0000,N,00000.0000,W,000.0,000.0,010101,,,D"
        output = data_gps(gps_data_edge_case)
        self.assertIsNotNone(output)  # Ожидается, что выход не будет None

        self.assertEqual(output["latitude"], 0.0)  # Ожидается, что широта будет 0
        self.assertEqual(output["longitude"], 0.0)  # Ожидается, что долгота будет 0


if __name__ == "__main__":
    unittest.main()
