class Config:
    WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
    WEATHER_API_PARAMS = {
        "hourly": "temperature_2m,relativehumidity_2m,dewpoint_2m,surface_pressure,pressure_msl",
        "forecast_days": 1
    }
    RATE_LIMIT = 20  # 20 запросов в минуту
    RATE_LIMIT_WINDOW = 60  # 60 секунд
    CACHE_SIZE = 128  # Размер кеша для запросов погоды
    CACHE_TTL = 3600  # 1 час (в секундах)
    COORDINATE_PRECISION: int = 2


# config.py
import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "cache.log",  # Логи будут писаться в этот файл
            "mode": "a",
        },
    },
    "loggers": {
        "cache_logger": {  # Логгер для кеширования
            "handlers": ["console", "file"],  # Вывод и в консоль, и в файл
            "level": "INFO",  # Минимальный уровень логирования
            "propagate": False,  # Отключаем передачу родительским логгерам
        },
    },
}

# Инициализация логгера
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("cache_logger")  # Используйте этот логгер в коде