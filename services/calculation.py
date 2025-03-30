import math
from config import error_logger  # Импортируем логгер


class HumidityCalculator:
    @staticmethod
    def calculate_absolute_humidity(temp_c: float, relative_humidity: float, pressure_hPa: float = 1013.25) -> float:
        """Рассчитывает абсолютную влажность (г/м³) с учетом давления.

        Args:
            temp_c (float): Температура (°C)
            relative_humidity (float): Относительная влажность (%)
            pressure_hPa (float): Атмосферное давление (гПа, по умолчанию 1013.25 гПа)

        Returns:
            float: Абсолютная влажность (г/м³)

        Raises:
            ValueError: Если параметры выходят за допустимые границы
        """
        # Проверка входных параметров
        try:
            if not (-273.15 <= temp_c <= 100):
                error_msg = f"Invalid temperature: {temp_c}°C (must be between -273.15 and 100)"
                error_logger.error(error_msg)
                raise ValueError(error_msg)

            if not (0 <= relative_humidity <= 100):
                error_msg = f"Invalid humidity: {relative_humidity}% (must be between 0 and 100)"
                error_logger.error(error_msg)
                raise ValueError(error_msg)

            if pressure_hPa <= 0:
                error_msg = f"Invalid pressure: {pressure_hPa} hPa (must be positive)"
                error_logger.error(error_msg)
                raise ValueError(error_msg)

            # Константы для формулы Магнуса
            a = 6.112  # гПа
            b = 17.67
            c = 243.5  # °C

            # Давление насыщенного пара (гПа)
            es = a * math.exp((b * temp_c) / (c + temp_c))

            # Парциальное давление водяного пара (гПа)
            # Учет давления (более точная формула)
            e = (relative_humidity / 100) * es * pressure_hPa / (pressure_hPa - (1 - relative_humidity / 100) * es)

            # Абсолютная влажность (г/м³)
            absolute_humidity = (e * 1000) / (461.5 * (temp_c + 273.15))
        except Exception as e:
            error_logger.error(f"Error in calculate_absolute_humidity: {str(e)}", exc_info=True)
            raise

        return absolute_humidity


    @staticmethod
    def calculate_relative_humidity(temp_c: float, absolute_humidity: float, pressure_hPa: float = 1013.25) -> float:
        """Рассчитывает относительную влажность (%) с учетом давления.

        Args:
            temp_c (float): Температура (°C)
            absolute_humidity (float): Абсолютная влажность (г/м³)
            pressure_hPa (float): Атмосферное давление (гПа, по умолчанию 1013.25 гПа)

        Returns:
            float: Относительная влажность (%)

        Raises:
            ValueError: Если параметры выходят за допустимые границы
        """
        # Проверка входных параметров
        try:
            if not (-273.15 <= temp_c <= 100):
                error_msg = f"Invalid temperature: {temp_c}°C (must be between -273.15 and 100)"
                error_logger.error(error_msg)
                raise ValueError(error_msg)

            if not (0 < absolute_humidity <= 10000):
                error_msg = f"Invalid humidity: {absolute_humidity}% (must be >= 0 and <10000)"
                error_logger.error(error_msg)
                raise ValueError(error_msg)

            if pressure_hPa <= 0:
                error_msg = f"Invalid pressure: {pressure_hPa} hPa (must be positive)"
                error_logger.error(error_msg)
                raise ValueError(error_msg)

            # Константы для формулы Магнуса
            a = 6.112  # гПа
            b = 17.67
            c = 243.5  # °C

            # Парциальное давление водяного пара (гПа)
            e = (absolute_humidity * 461.5 * (temp_c + 273.15)) / 1000

            # Давление насыщенного пара (гПа)
            es = a * math.exp((b * temp_c) / (c + temp_c))

            # Относительная влажность с учетом давления
            relative_humidity = (e * (pressure_hPa - es + e)) / (es * pressure_hPa) * 100
        except Exception as e:
            error_logger.error(f"Error in calculate_relative_humidity: {str(e)}", exc_info=True)
            raise

        # Ограничение в пределах 0-100%
        return max(0.0, min(100.0, relative_humidity))