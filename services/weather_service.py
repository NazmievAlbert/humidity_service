import requests
from functools import lru_cache, wraps
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from config import Config



def timed_lru_cache(maxsize: int = 128, ttl=None):
    """LRU-кеш с TTL (время жизни записи в секундах)"""
    def decorator(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.expiration = {}  # Словарь для хранения времени добавления записей

        @wraps(func)
        def wrapped_func(self, *args, **kwargs):
            # Получаем TTL из конфига (если передан как callable) или используем дефолтное значение
            current_ttl = ttl(self) if callable(ttl) else ttl
            if current_ttl is None:
                # Если TTL не задан, отключаем проверку времени (кеш без TTL)
                return func(self, *args, **kwargs)

            # Генерируем ключ кеша
            key = args + tuple(kwargs.items())

            # Проверяем, есть ли запись в кеше и не истек ли срок
            if key in func.expiration:
                if datetime.now().timestamp() - func.expiration[key] < current_ttl:
                    return func(self, *args, **kwargs)
                else:
                    # Удаляем просроченную запись
                    func.cache_clear()  # Можно оптимизировать, удаляя только ключ `key`
                    del func.expiration[key]

            # Вызываем функцию и сохраняем время добавления
            result = func(self, *args, **kwargs)
            func.expiration[key] = datetime.now().timestamp()
            return result

        return wrapped_func
    return decorator


class WeatherService:
    def __init__(self, config):
        self.config = config

    @timed_lru_cache(maxsize=Config.CACHE_SIZE, ttl=None)
    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Получает данные о погоде с кешированием и TTL (1 час)"""
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

