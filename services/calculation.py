import math


class HumidityCalculator:
    @staticmethod
    def calculate_absolute_humidity(temp_c, relative_humidity, pressure_hPa=1013.25):
        """Рассчитывает абсолютную влажность (г/м³) с учетом давления.

        Args:
            temp_c (float): Температура (°C)
            relative_humidity (float): Относительная влажность (%)
            pressure_hPa (float): Атмосферное давление (гПа, по умолчанию 1013.25 гПа)

        Returns:
            float: Абсолютная влажность (г/м³)
        """
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

        return absolute_humidity

    @staticmethod
    def calculate_relative_humidity(temp_c, absolute_humidity, pressure_hPa=1013.25):
        """Рассчитывает относительную влажность (%) с учетом давления.

        Args:
            temp_c (float): Температура (°C)
            absolute_humidity (float): Абсолютная влажность (г/м³)
            pressure_hPa (float): Атмосферное давление (гПа, по умолчанию 1013.25 гПа)

        Returns:
            float: Относительная влажность (%)
        """
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

        # Ограничение в пределах 0-100%
        return max(0.0, min(100.0, relative_humidity))