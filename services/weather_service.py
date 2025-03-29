import requests
from functools import lru_cache
from typing import Optional, Dict, Any
from config import Config



class WeatherService:
    def __init__(self, config):
        self.config = config

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Получает данные о погоде с кешированием"""
        params = {
            **self.config.WEATHER_API_PARAMS,
            "latitude": round(float(lat), Config.COORDINATE_PRECISION),
            "longitude": round(float(lon), Config.COORDINATE_PRECISION)
        }
        try:
            response = requests.get(self.config.WEATHER_API_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
        