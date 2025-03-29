import pytest

from services.calculation import HumidityCalculator


class TestHumidityCalculator:
    @pytest.mark.parametrize("temp,relative_humidity,saturation_temp", [
        (40, 30, 17.9),  # Примерные значения
        (40, 70, 33),
        (20, 30, 1),
        (20, 70, 14),
        (10,30,-6.7),
        (10, 70, 4.4),
        (0, 30, -14.5),
        (0, 70, -4.4),
        (-10, 30, -23.2),
        (-10, 70, -14.1),

    ])
    def test_calculate_absolute_humidity(self, temp, relative_humidity, saturation_temp):
        result_abs = HumidityCalculator.calculate_absolute_humidity(temp_c=temp,relative_humidity=relative_humidity)
        result_relative= HumidityCalculator.calculate_relative_humidity(temp_c=saturation_temp, absolute_humidity=result_abs)
        print(result_relative)
        assert result_relative >95


