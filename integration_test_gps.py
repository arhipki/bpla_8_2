import unittest

import time

def convert_to_decimal(degree_str, direction):
    """Преобразование строки с градусами в десятичный формат."""
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
            timestamp_str = data_parts[1]  # Время фиксируется
            latitude = convert_to_decimal(data_parts[2], data_parts[3])
            longitude = convert_to_decimal(data_parts[4], data_parts[5])
            altitude = float(data_parts[9])
            speed = None  # Скорость не доступна в GGA

            # Форматирование даты для mktime
            current_time = time.localtime()
            year, month, day = current_time.tm_year, current_time.tm_mon, current_time.tm_mday
            timestamp = time.strptime(f"{timestamp_str},{year},{month},{day}", "%H%M%S.%f,%Y,%m,%d")
            timestamp_seconds = time.mktime(timestamp)

        # Проверка на формат RMC для извлечения скорости
        elif data_parts[0] == "$GPRMC":
            timestamp_str = data_parts[1]
            latitude = convert_to_decimal(data_parts[3], data_parts[4])
            longitude = convert_to_decimal(data_parts[5], data_parts[6])
            speed = float(data_parts[7]) * 0.514444  # Преобразование узлов в м/с
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

#Файл integration_test_gps.py

import unittest
from gps_module import data_gps

class TestGPSIntegration(unittest.TestCase):

    def test_gga_data_integration(self):
        gps_data_gga = "$GPGGA,123519.487,3754.587,N,14507.036,W,1,08,0.9,545.4,M,46.9,M,,*47"
        expected_output = {
            "latitude": 37.90978333333333,
            "longitude": -145.11726666666667,
            "altitude": 545.4,
            "speed": None,
            # Значение времени не проверяется в тесте
        }
        output = data_gps(gps_data_gga)

        # Выполнение тестирования
        self.assertAlmostEqual(output["latitude"], expected_output["latitude"], places=7)
        self.assertAlmostEqual(output["longitude"], expected_output["longitude"], places=7)
        self.assertEqual(output["altitude"], expected_output["altitude"])
        self.assertIsNone(output["speed"])

    def test_rmc_data_integration(self):
        gps_data_rmc = "$GPRMC,123519.487,A,3754.587,N,14507.036,W,000.0,360.0,120419,,,D"
        expected_output = {
            "latitude": 37.90978333333333,
            "longitude": -145.11726666666667,
            "altitude": None,
            "speed": 0.0,
            # Значение времени не проверяется в тесте
        }
        output = data_gps(gps_data_rmc)

        # Выполнение тестирования
        self.assertAlmostEqual(output["latitude"], expected_output["latitude"], places=7)
        self.assertAlmostEqual(output["longitude"], expected_output["longitude"], places=7)
        self.assertIsNone(output["altitude"])
        self.assertEqual(output["speed"], expected_output["speed"])

if __name__ == "__main__":
    unittest.main()
