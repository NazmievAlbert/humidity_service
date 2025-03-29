from pydantic import BaseModel, Field, field_validator
from typing import Annotated
from config import Config

# Типы для аннотаций
Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]

class HumidityRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    target_temp: float

    @field_validator('latitude', 'longitude')
    @classmethod
    def round_coordinates(cls, v: float) -> float:
        """Округляет координаты до 2 знаков после запятой"""
        precision = Config.COORDINATE_PRECISION
        round_to = 10 ** -precision
        return round(v / round_to) * round_to

class HumidityResponse(BaseModel):
    location: dict[str, float]
    current_weather: dict[str, float]
    target_temperature: float
    target_relative_humidity: float
    timestamp: str