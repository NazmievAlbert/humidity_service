import logging

import requests
from functools import lru_cache, wraps
from time import time  # Быстрее, чем datetime.now().timestamp()
from typing import Any, Dict, Optional, Tuple
from config import Config, error_logger
from config import cache_logger  # Импортируем настроенный логгер



def timed_lru_cache(maxsize=64, ttl=None, enable_logging=None):
    """Оптимизированный LRU-кеш с TTL для слабых серверов."""
    if enable_logging is None:
        enable_logging = Config.ENABLE_CACHE_LOGGING
    def decorator(func):
        cached_func = lru_cache(maxsize=maxsize)(func)
        cached_func.expiration = {}  # { (args, kwargs): timestamp }

        @wraps(func)
        def wrapped_func(self, *args, **kwargs):

            # 1. Определяем TTL (минимальная нагрузка)
            current_ttl = ttl(self) if callable(ttl) else ttl

            if current_ttl is None:
                current_ttl=Config.CACHE_TTL

            # 2. Если TTL нет — сразу возвращаем результат
            if current_ttl is None:
                if enable_logging:
                    cache_logger.info(f"[{func.__name__}] Кеш отключён (TTL=None)")
                return cached_func(self, *args, **kwargs)

            # 3. Генерируем ключ (быстро и без лишних операций)
            key = (args, frozenset(kwargs.items()))  # frozenset для хеширования

            # 4. Проверяем кеш (оптимизированная проверка)
            now = time()
            if key in cached_func.expiration:
                if now - cached_func.expiration[key] < current_ttl:
                    if enable_logging:
                        cache_logger.info(f"[{func.__name__}] Данные из кеша")
                    return cached_func(self, *args, **kwargs)
                else:
                    # Удаляем только просроченный ключ (не весь кеш!)
                    del cached_func.expiration[key]
                    if enable_logging:
                        cache_logger.info(f"[{func.__name__}] Кеш устарел")

            # 5. Сохраняем результат (с минимальными вычислениями)
            result = cached_func(self, *args, **kwargs)
            cached_func.expiration[key] = now
            if enable_logging:
                cache_logger.info(f"[{func.__name__}] Новые данные закешированы")
            return result

        return wrapped_func
    return decorator


class WeatherService:
    def __init__(self, config):
        self.config = config

    @timed_lru_cache(maxsize=Config.CACHE_SIZE, ttl=None, enable_logging=Config.ENABLE_CACHE_LOGGING)
    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        try:
            params = {
                **self.config.WEATHER_API_PARAMS,
                "latitude": round(float(lat), Config.COORDINATE_PRECISION),
                "longitude": round(float(lon), Config.COORDINATE_PRECISION)
            }
            response = requests.get(self.config.WEATHER_API_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            error_logger.error(f"Weather API request failed: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            error_logger.error(f"Unexpected error in get_weather_data: {str(e)}", exc_info=True)
            return None

