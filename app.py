from flask import Flask, request, jsonify
from datetime import datetime
from config import Config
from services.weather_service import WeatherService

from services.calculation import HumidityCalculator
from services.rate_limiter import RateLimiter
from models.schemas import HumidityRequest, HumidityResponse

def create_app(config_class=Config):
    app = Flask(__name__)
    config = config_class()
    weather_service = WeatherService(config)
    calculator = HumidityCalculator()
    rate_limiter = RateLimiter(config)

    def process_humidity_calculation(lat: float, lon: float, target_temp: float) -> tuple[dict | None, str | None]:
        weather_data = weather_service.get_weather_data(lat, lon)
        if not weather_data or 'hourly' not in weather_data:
            return None, "Failed to fetch weather data"

        current_temp = weather_data['hourly']['temperature_2m'][0]
        current_rh = weather_data['hourly']['relativehumidity_2m'][0]
        current_pressure = weather_data['hourly']["surface_pressure"][0]

        abs_humidity = calculator.calculate_absolute_humidity(current_temp, current_rh,current_pressure)
        target_rh = calculator.calculate_relative_humidity(target_temp, abs_humidity,current_pressure)

        response = HumidityResponse(
            location={"latitude": lat, "longitude": lon},
            current_weather={
                "temperature": current_temp,
                "relative_humidity": current_rh,
                "current_pressure":current_pressure,
                "absolute_humidity": abs_humidity
            },
            target_temperature=target_temp,
            target_relative_humidity=target_rh,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        return response.model_dump(), None

    @app.route('/calculate_humidity', methods=['GET', 'POST'])
    def calculate_humidity():
        if not rate_limiter.check_rate_limit(request.remote_addr):
            return jsonify({"error": "Rate limit exceeded"}), 429

        try:
            if request.method == 'POST':
                data = HumidityRequest.model_validate(request.get_json())
            else:
                data = HumidityRequest(
                    latitude=request.args.get('latitude'),
                    longitude=request.args.get('longitude'),
                    target_temp=request.args.get('target_temp')
                )
        except Exception as e:
            return jsonify({"error": str(e)}), 400

        response, error = process_humidity_calculation(
            data.latitude, data.longitude, data.target_temp
        )

        if error:
            return jsonify({"error": error}), 500

        return jsonify(response)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, threaded=True)