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
