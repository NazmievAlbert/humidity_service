from flask import Flask, request, jsonify
from datetime import datetime
from config import Config
from config import error_logger
from services.weather_service import WeatherService
from services.calculation import HumidityCalculator
from services.rate_limiter import RateLimiter
from models.schemas import HumidityRequest, HumidityResponse

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.ensure_ascii = False  # Добавить после создания app
    config = config_class()
    weather_service = WeatherService(config)
    calculator = HumidityCalculator()
    rate_limiter = RateLimiter(config)

    def process_humidity_calculation(lat: float, lon: float, target_temp: float) -> tuple[dict | None, str | None]:
        """Обрабатывает расчет влажности с логированием ошибок"""
        try:
            weather_data = weather_service.get_weather_data(lat, lon)
            if not weather_data or 'hourly' not in weather_data:
                error_msg = "Не удалось получить данные о погоде или неверный формат ответа"
                error_logger.error(error_msg)
                return None, error_msg

            # Проверяем наличие всех необходимых полей в ответе
            required_fields = ['temperature_2m', 'relativehumidity_2m', 'surface_pressure']
            for field in required_fields:
                if field not in weather_data['hourly']:
                    error_msg = f"Отсутствует обязательное поле в данных о погоде: {field}"
                    error_logger.error(error_msg)
                    return None, error_msg

            current_temp = weather_data['hourly']['temperature_2m'][0]
            current_rh = weather_data['hourly']['relativehumidity_2m'][0]
            current_pressure = weather_data['hourly']['surface_pressure'][0]

            abs_humidity = calculator.calculate_absolute_humidity(current_temp, current_rh, current_pressure)
            target_rh = calculator.calculate_relative_humidity(target_temp, abs_humidity, current_pressure)

            response = HumidityResponse(
                location={"latitude": lat, "longitude": lon},
                current_weather={
                    "temperature": current_temp,
                    "relative_humidity": current_rh,
                    "current_pressure": current_pressure,
                    "absolute_humidity": abs_humidity
                },
                target_temperature=target_temp,
                target_relative_humidity=target_rh,
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            return response.model_dump(), None

        except Exception as e:
            error_logger.error(f"Ошибка при расчете влажности: {str(e)}", exc_info=True)
            return None, "Внутренняя ошибка сервера при расчете влажности"

    @app.route('/calculate_humidity', methods=['GET', 'POST'])
    def calculate_humidity():
        """Основной endpoint для расчета влажности"""
        try:
            # Проверка ограничения скорости
            client_ip = request.remote_addr
            if not rate_limiter.check_rate_limit(client_ip):
                error_logger.warning(f"Превышен лимит запросов для IP: {client_ip}")
                return jsonify({"error": "Превышен лимит запросов. Попробуйте позже."}), 429

            # Валидация входных данных
            try:
                if request.method == 'POST':
                    data = HumidityRequest.model_validate(request.get_json())
                else:
                    data = HumidityRequest(
                        latitude=float(request.args.get('latitude')),
                        longitude=float(request.args.get('longitude')),
                        target_temp=float(request.args.get('target_temp'))
                    )
            except ValueError as e:
                error_logger.error(f"Ошибка валидации входных данных: {str(e)}")
                return jsonify({"error": f"Неверные входные данные: {str(e)}"}), 400
            except Exception as e:
                error_logger.error(f"Неожиданная ошибка при валидации данных: {str(e)}", exc_info=True)
                return jsonify({"error": "Неверный формат запроса"}), 400

            # Обработка запроса
            response, error = process_humidity_calculation(
                data.latitude, data.longitude, data.target_temp
            )

            if error:
                return jsonify({"error": error}), 500

            return jsonify(response)

        except Exception as e:
            error_logger.critical(f"Критическая ошибка в обработчике calculate_humidity: {str(e)}", exc_info=True)
            return jsonify({"error": "Внутренняя ошибка сервера"}), 500

    @app.errorhandler(404)
    def not_found_error(error):
        error_logger.warning(f"404 Not Found: {request.url}")
        return jsonify({"error": "Ресурс не найден"}), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        error_logger.warning(f"405 Method Not Allowed: {request.method} {request.url}")
        return jsonify({"error": "Метод не разрешен"}), 405

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, threaded=True)