import os
import logging
from logging.config import dictConfig

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
    ENABLE_CACHE_LOGGING = False
    COORDINATE_PRECISION: int = 2
    # Указываем директорию для логов относительно текущего рабочего каталога

    LOG_DIR = 'logs'
    LOG_FILE = 'logs.log'  # Имя файла логов

    # Полный путь до файла логов


    LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

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
                "filename": LOG_PATH,  # Теперь используем переменную LOG_PATH
                "mode": "a",
            },
        },
        "loggers": {
            "cache_logger": {  # Логгер для кеширования
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "error_logger": {  #логгер для ошибок
                "handlers": ["console", "file"],
                "level": "ERROR",
                "propagate": False,
            },
        },
    }

# Проверяем существование директории и создаем её, если она отсутствует
if not os.path.exists(Config.LOG_DIR):
    os.makedirs(Config.LOG_DIR)

# Инициализация логгера
dictConfig(Config.LOGGING_CONFIG)
cache_logger = logging.getLogger("cache_logger")
error_logger = logging.getLogger("error_logger")

